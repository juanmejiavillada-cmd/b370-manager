"""
B370 — Núcleo compartido entre scripts CLI y MCP server.

Centraliza:
- Conexión WooCommerce REST API (CK/CS desde .env)
- Conexión SSH + WP-CLI para meta keys (_thumbnail_id, wavi_value)
- Helpers de búsqueda de imágenes en WP Media
- Modo dry-run para operaciones de escritura

Convención de variables de entorno (igual al .env existente):
    WC_URL, WC_CK, WC_CS, SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS, SSH_PATH

NOTA: este módulo no escribe a stdout (corrompería el JSON-RPC del MCP).
Todos los logs van a stderr o archivo. Los scripts CLI siguen pudiendo imprimir
con print() porque ellos no son MCP servers.
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


# Cargar .env del proyecto (un nivel arriba de mcp/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ── Credenciales WooCommerce ─────────────────────────────────────────────────
WC_URL   = os.getenv("WC_URL", "https://b370sports.com")
WC_CK    = os.getenv("WC_CK")
WC_CS    = os.getenv("WC_CS")
API_BASE = f"{WC_URL}/wp-json/wc/v3"
AUTH     = HTTPBasicAuth(WC_CK, WC_CS) if WC_CK and WC_CS else None

# ── Credenciales SSH ─────────────────────────────────────────────────────────
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT", 65002))
SSH_USER = os.getenv("SSH_USER")
SSH_PASS = os.getenv("SSH_PASS")
SSH_PATH = os.getenv("SSH_PATH", "~/domains/b370sports.com/public_html")

# ── Configuración de comportamiento ──────────────────────────────────────────
DELAY = 0.3  # delay entre llamadas a la API
DRY_RUN = os.getenv("B370_DRY_RUN", "true").lower() == "true"

# Bandas de precio para validación
PRICE_MIN = float(os.getenv("B370_PRICE_MIN", "50000"))
PRICE_MAX = float(os.getenv("B370_PRICE_MAX", "200000"))

# Estructura oficial de precios (según README del proyecto)
PRECIOS_DEFAULT = {
    "Tipo fan":     80000,
    "Tipo jugador": 110000,  # En transición a "Tipo original" según script normalizar_calidad
    "Tipo original": 110000,
    "1.1":          120000,
    "Retro":        80000,
    "Buzo AN":      95000,
    "Gabán AN":     150000,
}


# ============================================================================
# Logging seguro (archivo + stderr, NUNCA stdout)
# ============================================================================
def setup_logger(name: str = "b370-mcp") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log_file = os.getenv("B370_LOG_FILE", str(PROJECT_ROOT / "b370-mcp.log"))
    try:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception as e:
        sys.stderr.write(f"WARN: log file no disponible: {e}\n")
    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


log = setup_logger()


# ============================================================================
# Validaciones
# ============================================================================
def assert_wc_credentials():
    """Lanza error si no hay credenciales de WC configuradas."""
    if not WC_CK or not WC_CS:
        raise RuntimeError(
            "Faltan WC_CK / WC_CS en .env. "
            f"Esperado en: {PROJECT_ROOT / '.env'}"
        )


def validate_price(price: float) -> tuple[bool, str]:
    """Valida que un precio esté dentro de bandas."""
    try:
        p = float(price)
    except (TypeError, ValueError):
        return False, f"Precio no numérico: {price!r}"
    if p < PRICE_MIN:
        return False, f"Precio ${p:,.0f} < mínimo ${PRICE_MIN:,.0f}"
    if p > PRICE_MAX:
        return False, f"Precio ${p:,.0f} > máximo ${PRICE_MAX:,.0f}"
    return True, "OK"


# ============================================================================
# WooCommerce REST helpers
# ============================================================================
def wc_get(path: str, **params) -> requests.Response:
    """GET a la API de WC. path sin /wp-json/wc/v3/."""
    assert_wc_credentials()
    return requests.get(f"{API_BASE}/{path}", auth=AUTH, params=params)


def wc_post(path: str, payload: dict) -> requests.Response:
    """POST a la API de WC."""
    assert_wc_credentials()
    return requests.post(f"{API_BASE}/{path}", auth=AUTH, json=payload)


def wc_put(path: str, payload: dict) -> requests.Response:
    """PUT a la API de WC."""
    assert_wc_credentials()
    return requests.put(f"{API_BASE}/{path}", auth=AUTH, json=payload)


def wc_delete(path: str, **params) -> requests.Response:
    """DELETE a la API de WC."""
    assert_wc_credentials()
    return requests.delete(f"{API_BASE}/{path}", auth=AUTH, params=params)


# ============================================================================
# Operaciones comunes WC
# ============================================================================
def get_product(product_id: int) -> dict:
    """Trae un producto por ID."""
    r = wc_get(f"products/{product_id}")
    return r.json() if r.status_code == 200 else {}


def get_variations(product_id: int) -> list[dict]:
    """Lista variaciones de un producto."""
    r = wc_get(f"products/{product_id}/variations", per_page=100)
    return r.json() if r.status_code == 200 else []


def get_or_create_category(nombre: str) -> Optional[int]:
    """Devuelve ID de categoría, la crea si no existe."""
    r = wc_get("products/categories", search=nombre, per_page=20)
    if r.status_code == 200:
        for cat in r.json():
            if cat["name"].lower() == nombre.lower():
                return cat["id"]
    if DRY_RUN:
        log.info(f"[DRY] crearía categoría '{nombre}'")
        return None
    r = wc_post("products/categories", {"name": nombre})
    if r.status_code in (200, 201):
        return r.json()["id"]
    log.error(f"Error creando categoría '{nombre}': {r.text[:150]}")
    return None


def product_exists(nombre: str) -> Optional[int]:
    """Devuelve ID si ya existe un producto con ese nombre exacto."""
    r = wc_get("products", search=nombre, per_page=10)
    if r.status_code == 200:
        for p in r.json():
            if p["name"].strip().lower() == nombre.strip().lower():
                return p["id"]
    return None


# ============================================================================
# SSH + WP-CLI (para meta keys que la REST API no expone bien)
# ============================================================================
def ssh_connect():
    """Establece conexión SSH. Devuelve cliente paramiko o None."""
    if not SSH_PASS:
        log.warning("SSH_PASS no configurado en .env — operaciones SSH no disponibles")
        return None
    try:
        import paramiko
    except ImportError:
        log.error("paramiko no instalado. pip install paramiko")
        return None
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            SSH_HOST, port=SSH_PORT, username=SSH_USER,
            password=SSH_PASS, timeout=15,
        )
        log.info(f"SSH conectado a {SSH_HOST}:{SSH_PORT}")
        return client
    except Exception as e:
        log.error(f"SSH falló: {e}")
        return None


def ssh_exec(client, cmd: str) -> str:
    """Ejecuta comando en SSH dentro de SSH_PATH y devuelve stdout."""
    full = f"cd {SSH_PATH} && {cmd}"
    _, stdout, _ = client.exec_command(full)
    return stdout.read().decode(errors="replace").strip()


def find_image_ids_by_name(nombre_imagen: str) -> list[int]:
    """
    Busca IDs de imágenes en WP Media filtrando por nombre de archivo en la URL.

    Uso típico: si subiste BARCELONA-LOCAL_1.jpg, BARCELONA-LOCAL_2.jpg, etc.,
    pasas "BARCELONA-LOCAL" y devuelve los IDs ordenados (menor = principal).

    Args:
        nombre_imagen: prefijo del archivo (ej "BARCELONA-LOCAL")

    Returns:
        Lista ordenada de IDs (vacía si SSH no disponible o no encuentra).
    """
    client = ssh_connect()
    if not client:
        return []
    try:
        cmd = (
            f'wp post list --post_type=attachment --fields=ID,guid '
            f'--format=csv --posts_per_page=9999 2>/dev/null '
            f'| grep -i "{nombre_imagen}"'
        )
        output = ssh_exec(client, cmd)
        ids = []
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split(",", 1)
            if parts[0].strip().isdigit():
                ids.append(int(parts[0].strip()))
        return sorted(ids)
    finally:
        client.close()


def assign_image_meta_via_ssh(post_id: int, main_id: int, gallery_ids: list[int] = None) -> bool:
    """
    Asigna _thumbnail_id y wavi_value a un post (variación o producto padre)
    usando WP-CLI por SSH. Esta es la única forma confiable de tocar wavi_value.

    Args:
        post_id: ID del producto o variación
        main_id: ID de imagen principal
        gallery_ids: lista opcional de IDs de galería

    Returns:
        True si se ejecutó (o sería ejecutado en dry-run).
    """
    if DRY_RUN:
        log.info(f"[DRY] post {post_id}: _thumbnail={main_id}, gallery={gallery_ids}")
        return True

    client = ssh_connect()
    if not client:
        return False
    try:
        ssh_exec(client, f"wp post meta update {post_id} _thumbnail_id {main_id}")
        if gallery_ids:
            gallery_str = ",".join(str(i) for i in gallery_ids)
            ssh_exec(client, f"wp post meta update {post_id} wavi_value '{gallery_str}'")
        log.info(f"Meta imágenes asignado a post {post_id}")
        return True
    finally:
        client.close()


# ============================================================================
# Utilidad: extraer atributos de una variación
# ============================================================================
def extract_variation_attrs(variation: dict) -> dict:
    """Convierte la lista de attributes de WC en dict {nombre: valor}."""
    return {a["name"]: a.get("option") for a in variation.get("attributes", [])}


def get_talla(variation: dict) -> Optional[str]:
    """Extrae talla. El proyecto usa el atributo 'Tallas' (plural)."""
    attrs = extract_variation_attrs(variation)
    return attrs.get("Tallas") or attrs.get("Talla")  # fallback singular


def get_calidad(variation: dict) -> Optional[str]:
    """Extrae calidad. Si el producto no tiene atributo Calidad, devuelve None."""
    attrs = extract_variation_attrs(variation)
    return attrs.get("Calidad")
