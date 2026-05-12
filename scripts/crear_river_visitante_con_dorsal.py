#!/usr/bin/env python3
"""
B370 — Crear RIVER VISITANTE TIPO ORIGINAL CON DORSAL
======================================================
Flujo completo:
  1. Sube 7 imagenes via SCP
  2. Importa a WP Media via wp media import
  3. Crea producto padre variable
  4. Crea 5 variaciones (S, M, L, XL, XXL) con SKUs
  5. Asigna imagenes: _thumbnail_id + wavi_value

SKUs segun Excel Quenti (6 abril 2026):
  S, M, L, XL -> no encontrados en Excel -> SKU vacio
  XXL (2XL)   -> 2100111939508 (stock 1)
"""

import os
import sys
import time
import glob
import paramiko
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

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

# Rutas locales
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
MANAGER_DIR  = os.path.dirname(SCRIPT_DIR)
IMAGENES_DIR = os.path.join(MANAGER_DIR, "imagenes", "para-subir")

PRODUCT = {
    "nombre_wc":     "RIVER VISITANTE TIPO ORIGINAL CON DORSAL",
    "nombre_quenti": "CAMISETA DE RIVER VISITANTE TIPO ORIGINAL CON DORSAL DE HOMBRE",
    "nombre_imagen": "RIVER-VISITANTE-TIPO-ORIGINAL-CON-DORSAL",
    "calidad":       "Tipo original",
    "tallas":        ["S", "M", "L", "XL", "XXL"],
    "precio":        109900,
    "categoria":     "River Plate",
    # Solo XXL tiene SKU en el Excel de Quenti (6 abril 2026)
    # S, M, L, XL se crean con SKU vacio para asignar manualmente
    "skus":  {
        "S":   "",
        "M":   "",
        "L":   "",
        "XL":  "",
        "XXL": "2100111939508",
    },
    "stock": {
        "S":   0,
        "M":   0,
        "L":   0,
        "XL":  0,
        "XXL": 1,
    },
}

WP_UPLOADS_PATH = "~/domains/b370sports.com/public_html/wp-content/uploads"
WP_ROOT         = "~/domains/b370sports.com/public_html"


# ── SSH ───────────────────────────────────────────────────────────────────────

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS, timeout=20)
    print("  OK Conectado SSH")
    return client


def ssh_exec(client, cmd):
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    return out, err


# ── SUBIR IMAGENES ────────────────────────────────────────────────────────────

def upload_images(client, nombre_imagen):
    """Sube via SCP las imagenes _1.jpg a _7.jpg al servidor."""
    pattern = os.path.join(IMAGENES_DIR, f"{nombre_imagen}_*.jpg")
    local_files = sorted(glob.glob(pattern))

    if not local_files:
        print(f"  WARN No se encontraron imagenes con patron: {pattern}")
        return []

    print(f"\n  Subiendo {len(local_files)} imagenes via SCP...")
    sftp = client.open_sftp()
    remote_dir = WP_UPLOADS_PATH.replace("~", f"/home/{SSH_USER}")

    uploaded = []
    for local_path in local_files:
        fname = os.path.basename(local_path)
        remote_path = f"{remote_dir}/{fname}"
        try:
            sftp.put(local_path, remote_path)
            print(f"  OK  Subido: {fname}")
            uploaded.append(fname)
        except Exception as e:
            print(f"  ERR No se pudo subir {fname}: {e}")
    sftp.close()
    return uploaded


# ── IMPORTAR A WP MEDIA ───────────────────────────────────────────────────────

def import_to_wp_media(client, nombre_imagen):
    """Importa las imagenes a la biblioteca de medios de WordPress via WP-CLI."""
    print(f"\n  Importando imagenes a WP Media...")
    pattern = f"{WP_UPLOADS_PATH}/{nombre_imagen}_*.jpg"
    cmd = (
        f"cd {WP_ROOT} && "
        f"wp media import {pattern} --path={WP_ROOT} --porcelain 2>&1"
    )
    out, err = ssh_exec(client, cmd)
    print(f"  WP-CLI output: {out[:500]}")
    if err and "error" in err.lower():
        print(f"  WARN stderr: {err[:300]}")

    # Parsear IDs retornados por --porcelain (un ID por linea)
    ids = []
    for line in out.split("\n"):
        line = line.strip()
        if line.isdigit():
            ids.append(int(line))
    return ids


def get_image_ids_from_wp(client, nombre_imagen):
    """Alternativa: busca los attachment IDs por nombre de archivo en WP."""
    cmd = (
        f"cd {WP_ROOT} && "
        f"wp post list --post_type=attachment --fields=ID,guid "
        f"--format=csv --posts_per_page=9999 2>/dev/null "
        f"| grep -i '{nombre_imagen}'"
    )
    out, _ = ssh_exec(client, cmd)
    ids = []
    for line in out.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(",", 1)
        if parts[0].strip().isdigit():
            ids.append(int(parts[0].strip()))
    return sorted(ids)


# ── WOOCOMMERCE ───────────────────────────────────────────────────────────────

def get_or_create_category(nombre):
    r = requests.get(f"{API_BASE}/products/categories", auth=AUTH,
                     params={"search": nombre, "per_page": 20})
    if r.status_code == 200:
        for cat in r.json():
            if cat["name"].strip().lower() == nombre.strip().lower():
                print(f"  OK  Categoria existente: {nombre} (ID: {cat['id']})")
                return cat["id"]
    # Crear
    r = requests.post(f"{API_BASE}/products/categories", auth=AUTH,
                      json={"name": nombre})
    if r.status_code in (200, 201):
        cid = r.json()["id"]
        print(f"  OK  Categoria creada: {nombre} (ID: {cid})")
        return cid
    print(f"  ERR Creando categoria '{nombre}': {r.text[:150]}")
    return None


def product_exists(nombre):
    r = requests.get(f"{API_BASE}/products", auth=AUTH,
                     params={"search": nombre, "per_page": 10})
    if r.status_code == 200:
        for p in r.json():
            if p["name"].strip().lower() == nombre.strip().lower():
                return p["id"]
    return None


def create_parent_product(product, cat_id, main_image_id=None):
    attrs = [
        {"name": "Tallas",  "visible": True, "variation": True, "options": product["tallas"]},
        {"name": "Calidad", "visible": True, "variation": True, "options": [product["calidad"]]},
    ]
    payload = {
        "name":       product["nombre_wc"],
        "type":       "variable",
        "status":     "publish",
        "categories": [{"id": cat_id}] if cat_id else [],
        "attributes": attrs,
    }
    if main_image_id:
        payload["images"] = [{"id": main_image_id}]

    r = requests.post(f"{API_BASE}/products", auth=AUTH, json=payload)
    if r.status_code in (200, 201):
        pid = r.json()["id"]
        print(f"  OK  Producto padre creado (ID: {pid})")
        return pid
    print(f"  ERR Creando producto padre: {r.text[:300]}")
    return None


def create_variations(product_id, product):
    variation_ids = []
    for talla in product["tallas"]:
        sku   = product["skus"].get(talla, "")
        stock = product["stock"].get(talla, 0)

        attrs = [
            {"name": "Tallas",  "option": talla},
            {"name": "Calidad", "option": product["calidad"]},
        ]
        payload = {
            "attributes":     attrs,
            "sku":            sku,
            "regular_price":  str(product["precio"]),
            "manage_stock":   True,
            "stock_quantity": stock,
            "stock_status":   "instock" if stock > 0 else "outofstock",
        }

        r = requests.post(
            f"{API_BASE}/products/{product_id}/variations",
            auth=AUTH, json=payload
        )
        if r.status_code in (200, 201):
            vid = r.json()["id"]
            variation_ids.append(vid)
            sku_label = sku if sku else "(sin SKU)"
            estado    = "instock" if stock > 0 else "agotado"
            print(f"  OK  {talla:5s} -> SKU: {sku_label:22s} | Stock: {stock} ({estado}) | ID var: {vid}")
        else:
            print(f"  ERR {talla:5s} -> {r.text[:120]}")
        time.sleep(DELAY)

    return variation_ids


def assign_images_ssh(client, product_id, variation_ids, image_ids):
    """Asigna _thumbnail_id y wavi_value via WP-CLI."""
    if not image_ids:
        print("  WARN Sin image_ids — asigna imagenes manualmente")
        return

    main_id    = image_ids[0]
    gallery    = image_ids[1:]
    gallery_str = ",".join(str(i) for i in gallery)

    # Padre
    cmd = f"cd {WP_ROOT} && wp post meta update {product_id} _thumbnail_id {main_id}"
    ssh_exec(client, cmd)
    print(f"  OK  Padre _thumbnail_id -> {main_id}")

    # Variaciones
    for vid in variation_ids:
        ssh_exec(client, f"cd {WP_ROOT} && wp post meta update {vid} _thumbnail_id {main_id}")
        if gallery_str:
            ssh_exec(client, f"cd {WP_ROOT} && wp post meta update {vid} wavi_value '{gallery_str}'")

    print(f"  OK  Variaciones _thumbnail_id -> {main_id}" +
          (f" | wavi_value -> {gallery_str}" if gallery_str else ""))


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*64)
    print("  B370 — RIVER VISITANTE TIPO ORIGINAL CON DORSAL")
    print("="*64)
    print(f"  Tienda : {WC_URL}")
    print(f"  Precio : ${PRODUCT['precio']:,.0f} COP")
    print(f"  Calidad: {PRODUCT['calidad']}")
    print("="*64)

    # 1. Verificar duplicado
    print(f"\n[1] Verificando si el producto ya existe...")
    existing = product_exists(PRODUCT["nombre_wc"])
    if existing:
        print(f"  WARN Producto ya existe en WC (ID: {existing}) — abortando para no duplicar")
        return

    # 2. Conectar SSH
    print(f"\n[2] Conectando SSH a {SSH_HOST}:{SSH_PORT}...")
    try:
        client = ssh_connect()
    except Exception as e:
        print(f"  ERR SSH: {e}")
        client = None

    image_ids = []

    if client:
        # 3. Subir imagenes
        print(f"\n[3] Subiendo imagenes...")
        uploaded = upload_images(client, PRODUCT["nombre_imagen"])

        if uploaded:
            # 4. Importar a WP Media
            print(f"\n[4] Importando a WP Media...")
            image_ids = import_to_wp_media(client, PRODUCT["nombre_imagen"])
            if not image_ids:
                print("  WARN wp media import no retorno IDs — buscando por nombre...")
                image_ids = get_image_ids_from_wp(client, PRODUCT["nombre_imagen"])

            print(f"\n  Imagenes WP Media IDs: {image_ids}")
        else:
            print("  WARN No se subieron imagenes")
    else:
        print("\n[3/4] Sin SSH — saltando subida de imagenes")

    # 5. Categoria
    print(f"\n[5] Verificando/creando categoria '{PRODUCT['categoria']}'...")
    cat_id = get_or_create_category(PRODUCT["categoria"])
    time.sleep(DELAY)

    # 6. Crear producto padre
    print(f"\n[6] Creando producto padre...")
    main_img = image_ids[0] if image_ids else None
    product_id = create_parent_product(PRODUCT, cat_id, main_img)
    if not product_id:
        print("  ERR No se pudo crear el producto padre — abortando")
        if client:
            client.close()
        return
    time.sleep(DELAY)

    # 7. Crear variaciones
    print(f"\n[7] Creando {len(PRODUCT['tallas'])} variaciones...")
    variation_ids = create_variations(product_id, PRODUCT)

    # 8. Asignar imagenes
    if client and variation_ids and image_ids:
        print(f"\n[8] Asignando imagenes a variaciones via WP-CLI...")
        assign_images_ssh(client, product_id, variation_ids, image_ids)
    elif not image_ids:
        print(f"\n[8] PENDIENTE: Asigna imagenes manualmente en WordPress")

    if client:
        client.close()

    # Reporte final
    print(f"\n{'='*64}")
    print("  RESULTADO FINAL")
    print(f"{'='*64}")
    print(f"  Producto padre ID : {product_id}")
    print(f"  Variaciones IDs   : {variation_ids}")
    print(f"  Imagenes WP IDs   : {image_ids}")
    print(f"  URL tienda        : {WC_URL}/?p={product_id}")
    print(f"\n  ADVERTENCIA: Tallas S, M, L, XL creadas SIN SKU.")
    print(f"  Asigna los codigos de barras de Quenti manualmente.")
    print(f"  Solo XXL tiene SKU: 2100111939508 (stock: 1)")
    print("="*64)


if __name__ == "__main__":
    main()
