#!/usr/bin/env python3
"""
B370 — Crear Manchester United Visitante (flujo completo)
=========================================================
Pasos:
  1. Subir 6 imágenes via SCP a /tmp/ del servidor
  2. Importar a WP Media Library con WP-CLI (anotando IDs)
  3. Crear producto padre en WooCommerce con categoría Manchester United
  4. Crear 5 variaciones (S, M, L, XL, XXL) × Tipo original @ $109.900
  5. Asignar short_description con guía de tallas
  6. Asignar _thumbnail_id y galería vía SSH

SKUs desde Quenti:
  - 2XL: 2100001034608 (stock 1)
  - S, M, L, XL: sin SKU en Quenti (producto nuevo)
"""

import os
import sys
import time
import paramiko
from scp import SCPClient
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Cargar .env desde el directorio padre del script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH   = os.path.join(SCRIPT_DIR, "..", ".env")
load_dotenv(ENV_PATH)

WC_URL   = os.getenv("WC_URL", "https://b370sports.com")
CK       = os.getenv("WC_CK")
CS       = os.getenv("WC_CS")
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT", 65002))
SSH_USER = os.getenv("SSH_USER")
SSH_PASS = os.getenv("SSH_PASS")
SSH_PATH = os.getenv("SSH_PATH", "~/domains/b370sports.com/public_html")

AUTH     = HTTPBasicAuth(CK, CS)
API_BASE = f"{WC_URL}/wp-json/wc/v3"
DELAY    = 0.4

# ── CONFIGURACION DEL PRODUCTO ────────────────────────────────────────────────
PRODUCT = {
    "nombre_wc":     "Manchester United Visitante",
    "nombre_imagen": "MAN-UNITED-VISITANTE",
    "calidad":       "Tipo original",
    "tallas":        ["S", "M", "L", "XL", "XXL"],
    "precio":        109900,
    "categoria":     "Manchester United",
    "skus": {
        "S":   "",
        "M":   "",
        "L":   "",
        "XL":  "",
        "XXL": "2100001034608",
    },
    "stock": {
        "S":   0,
        "M":   0,
        "L":   0,
        "XL":  0,
        "XXL": 1,
    },
    "short_description": (
        '<img src="https://b370sports.com/wp-content/uploads/2025/11/GUIA-DE-TALLAS.png" '
        'alt="Guia de tallas B370" style="max-width:100%;height:auto;" />'
    ),
}

IMAGES_LOCAL_DIR = os.path.join(SCRIPT_DIR, "..", "imagenes", "para-subir")
IMAGE_FILES = [
    "MAN-UNITED-VISITANTE_1.jpg",
    "MAN-UNITED-VISITANTE_2.jpg",
    "MAN-UNITED-VISITANTE_3.jpg",
    "MAN-UNITED-VISITANTE_4.jpg",
    "MAN-UNITED-VISITANTE_5.jpg",
    "MAN-UNITED-VISITANTE_6.jpg",
]


# ── SSH ───────────────────────────────────────────────────────────────────────

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER,
                   password=SSH_PASS, timeout=20)
    return client


def ssh_exec(client, cmd):
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    return out, err


# ── PASO 3: SUBIR IMAGENES ────────────────────────────────────────────────────

def upload_images(client):
    """Sube las 6 imagenes a /tmp/ via SCP."""
    print("\n[PASO 3] Subiendo imagenes via SCP a /tmp/...")
    uploaded = []
    with SCPClient(client.get_transport()) as scp:
        for fname in IMAGE_FILES:
            local_path = os.path.join(IMAGES_LOCAL_DIR, fname)
            if not os.path.exists(local_path):
                print(f"  ERROR: No existe {local_path}")
                continue
            remote_path = f"/tmp/{fname}"
            scp.put(local_path, remote_path)
            print(f"  OK: {fname} -> {remote_path}")
            uploaded.append(fname)
    return uploaded


def import_to_wp_media(client, uploaded_files):
    """
    Importa cada imagen al WP Media Library via WP-CLI.
    Devuelve dict {filename: wp_media_id}.
    """
    print("\n[PASO 3b] Importando imagenes a WP Media Library...")
    media_ids = {}
    wp_path   = f"--path={SSH_PATH}"

    for i, fname in enumerate(uploaded_files, start=1):
        remote_path = f"/tmp/{fname}"
        title       = f"Manchester United Visitante {i}"
        cmd = (
            f"wp media import {remote_path} "
            f'--title="{title}" '
            f"{wp_path} "
            f"--porcelain 2>/dev/null"
        )
        out, err = ssh_exec(client, cmd)
        if out.strip().isdigit():
            wp_id = int(out.strip())
            media_ids[fname] = wp_id
            print(f"  OK: {fname} -> WP Media ID {wp_id}")
        else:
            print(f"  ERROR importando {fname}: out='{out}' err='{err[:100]}'")

    return media_ids


# ── PASO 4: CREAR PRODUCTO EN WC ──────────────────────────────────────────────

def get_or_create_category(nombre):
    """Obtiene ID de categoria; la crea si no existe."""
    r = requests.get(f"{API_BASE}/products/categories", auth=AUTH,
                     params={"search": nombre, "per_page": 20})
    if r.status_code == 200:
        for cat in r.json():
            if cat["name"].strip().lower() == nombre.strip().lower():
                print(f"  OK: Categoria '{nombre}' encontrada (ID: {cat['id']})")
                return cat["id"]
    # Crear
    r = requests.post(f"{API_BASE}/products/categories", auth=AUTH,
                      json={"name": nombre})
    if r.status_code in (200, 201):
        cat_id = r.json()["id"]
        print(f"  OK: Categoria '{nombre}' creada (ID: {cat_id})")
        return cat_id
    print(f"  ERROR creando categoria '{nombre}': {r.text[:150]}")
    return None


def product_exists(nombre):
    """Verifica si ya existe un producto con ese nombre exacto."""
    r = requests.get(f"{API_BASE}/products", auth=AUTH,
                     params={"search": nombre, "per_page": 10})
    if r.status_code == 200:
        for p in r.json():
            if p["name"].strip().lower() == nombre.strip().lower():
                return p["id"]
    return None


def create_parent_product(cat_id, image_ids_ordered):
    """
    Crea el producto padre variable con:
    - Atributos Tallas y Calidad
    - short_description con guia de tallas
    - Imagen principal (primer ID)
    """
    print("\n[PASO 4] Creando producto padre en WooCommerce...")

    attrs = [
        {"name": "Tallas", "visible": True, "variation": True,
         "options": PRODUCT["tallas"]},
        {"name": "Calidad", "visible": True, "variation": True,
         "options": [PRODUCT["calidad"]]},
    ]

    # Imagenes para el producto (todas, la primera es portada)
    images_payload = [{"id": mid} for mid in image_ids_ordered]

    payload = {
        "name":              PRODUCT["nombre_wc"],
        "type":              "variable",
        "status":            "publish",
        "categories":        [{"id": cat_id}] if cat_id else [],
        "attributes":        attrs,
        "short_description": PRODUCT["short_description"],
        "images":            images_payload,
    }

    r = requests.post(f"{API_BASE}/products", auth=AUTH, json=payload)
    if r.status_code in (200, 201):
        product_id = r.json()["id"]
        print(f"  OK: Producto padre creado -> ID {product_id}")
        return product_id
    print(f"  ERROR creando producto padre: {r.text[:300]}")
    return None


# ── PASO 5: CREAR VARIACIONES ─────────────────────────────────────────────────

def create_variations(product_id):
    """Crea 5 variaciones (S, M, L, XL, XXL) con precio, SKU y stock."""
    print(f"\n[PASO 5] Creando variaciones para producto ID {product_id}...")
    variation_ids = {}

    for talla in PRODUCT["tallas"]:
        sku   = PRODUCT["skus"].get(talla, "")
        stock = PRODUCT["stock"].get(talla, 0)

        payload = {
            "attributes": [
                {"name": "Tallas",  "option": talla},
                {"name": "Calidad", "option": PRODUCT["calidad"]},
            ],
            "sku":            sku,
            "regular_price":  str(PRODUCT["precio"]),
            "manage_stock":   True,
            "stock_quantity": stock,
            "stock_status":   "instock" if stock > 0 else "outofstock",
        }

        r = requests.post(
            f"{API_BASE}/products/{product_id}/variations",
            auth=AUTH, json=payload
        )
        if r.status_code in (200, 201):
            vid    = r.json()["id"]
            estado = "instock" if stock > 0 else "agotado"
            sku_str = sku if sku else "(sin SKU)"
            print(f"  OK: {talla:4s} | SKU: {sku_str:20s} | Stock: {stock} ({estado}) | Var ID: {vid}")
            variation_ids[talla] = vid
        else:
            print(f"  ERROR {talla}: {r.text[:150]}")
        time.sleep(DELAY)

    return variation_ids


# ── PASO 6: ASIGNAR IMAGENES VIA SSH ─────────────────────────────────────────

def assign_images_ssh(client, product_id, variation_ids_dict, image_ids_ordered):
    """
    Asigna _thumbnail_id (imagen _1) y wavi_value (galeria _2 a _6)
    al producto padre y a cada variacion.
    """
    print(f"\n[PASO 6] Asignando imagenes via SSH a producto {product_id}...")

    if not image_ids_ordered:
        print("  ADVERTENCIA: No hay IDs de imagen — omitiendo asignacion SSH")
        return

    main_id     = image_ids_ordered[0]
    gallery_ids = image_ids_ordered[1:]
    gallery_str = ",".join(str(i) for i in gallery_ids)

    # Producto padre — _thumbnail_id
    out, _ = ssh_exec(
        client,
        f"wp post meta update {product_id} _thumbnail_id {main_id} --path={SSH_PATH}"
    )
    print(f"  OK: Padre ({product_id}) _thumbnail_id -> {main_id}")

    # Variaciones
    for talla, vid in variation_ids_dict.items():
        ssh_exec(client,
                 f"wp post meta update {vid} _thumbnail_id {main_id} --path={SSH_PATH}")
        if gallery_str:
            ssh_exec(client,
                     f"wp post meta update {vid} wavi_value '{gallery_str}' --path={SSH_PATH}")
        print(f"  OK: {talla:4s} (var {vid}) -> _thumbnail_id:{main_id}"
              + (f" | wavi_value:{gallery_str}" if gallery_str else ""))


# ── PROCESO PRINCIPAL ─────────────────────────────────────────────────────────

def main():
    print("\n" + "="*65)
    print("  B370 — CREAR MANCHESTER UNITED VISITANTE (FLUJO COMPLETO)")
    print("="*65)
    print(f"  Tienda  : {WC_URL}")
    print(f"  Producto: {PRODUCT['nombre_wc']}")
    print(f"  Calidad : {PRODUCT['calidad']}")
    print(f"  Precio  : ${PRODUCT['precio']:,}".replace(",", "."))
    print("="*65)

    # Verificar que no exista ya
    existing = product_exists(PRODUCT["nombre_wc"])
    if existing:
        print(f"\n  ADVERTENCIA: El producto ya existe en WooCommerce (ID: {existing})")
        print("  Abortando para evitar duplicados.")
        return

    # Conectar SSH
    print("\n[SSH] Conectando a servidor...")
    try:
        client = ssh_connect()
        print(f"  OK: Conectado a {SSH_HOST}:{SSH_PORT}")
    except Exception as e:
        print(f"  ERROR SSH: {e}")
        return

    try:
        # PASO 3a: Subir imagenes
        uploaded = upload_images(client)
        if len(uploaded) < 6:
            print(f"  ADVERTENCIA: Solo se subieron {len(uploaded)}/6 imagenes")

        # PASO 3b: Importar a WP Media
        media_ids = import_to_wp_media(client, uploaded)

        # Ordenar IDs por nombre de archivo (_1 primero, _2 segundo, etc.)
        image_ids_ordered = []
        for fname in IMAGE_FILES:
            if fname in media_ids:
                image_ids_ordered.append(media_ids[fname])

        print(f"\n  WP Media IDs ordenados: {image_ids_ordered}")

        # PASO 4: Categoria
        cat_id = get_or_create_category(PRODUCT["categoria"])
        time.sleep(DELAY)

        # PASO 4: Crear producto padre
        product_id = create_parent_product(cat_id, image_ids_ordered)
        if not product_id:
            print("  ERROR: No se pudo crear el producto padre. Abortando.")
            return
        time.sleep(DELAY)

        # PASO 5: Crear variaciones
        variation_ids = create_variations(product_id)
        print(f"\n  Total variaciones creadas: {len(variation_ids)}/5")

        # PASO 6: Asignar imagenes SSH
        if image_ids_ordered:
            assign_images_ssh(client, product_id, variation_ids, image_ids_ordered)

        # ── RESUMEN FINAL ──────────────────────────────────────────────────────
        print(f"\n{'='*65}")
        print("  RESUMEN FINAL")
        print(f"{'='*65}")
        print(f"  Producto WC ID : {product_id}")
        print(f"  URL producto   : {WC_URL}/?p={product_id}")
        print(f"\n  WP Media IDs:")
        for fname, wid in sorted(media_ids.items()):
            print(f"    {fname}: {wid}")
        print(f"\n  Variaciones:")
        for talla in PRODUCT["tallas"]:
            vid  = variation_ids.get(talla, "ERROR")
            sku  = PRODUCT["skus"].get(talla) or "(sin SKU)"
            stk  = PRODUCT["stock"].get(talla, 0)
            print(f"    {talla:4s} | Var ID: {vid} | SKU: {sku:20s} | Stock: {stk}")
        print(f"\n  SKUs faltantes (no registrados en Quenti):")
        missing = [t for t in PRODUCT["tallas"] if not PRODUCT["skus"].get(t)]
        for t in missing:
            print(f"    {t}")
        print("="*65)

    finally:
        client.close()
        print("\n[SSH] Conexion cerrada.")


if __name__ == "__main__":
    main()
