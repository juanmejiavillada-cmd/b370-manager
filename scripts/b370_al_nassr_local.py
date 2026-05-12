#!/usr/bin/env python3
"""
B370 — Crear AL NASSR LOCAL (flujo completo)
=============================================
1. Sube las 6 imagenes via SCP a /tmp/ en el servidor
2. Las importa a WP Media via WP-CLI
3. Obtiene los WP Media IDs
4. Crea el producto padre en WooCommerce
5. Crea las variaciones con SKU de Quenti
6. Asigna imagen principal + galeria al producto padre

SKUs de Quenti (CUENTI INVENTARIO 6 ABRIL.xlsx):
  S   -> sin SKU
  M   -> 2100002038605  (stock: 1)
  L   -> sin SKU
  XL  -> 2100002038704  (stock: 0)
  XXL -> sin SKU
"""

import os
import sys
import time
import paramiko
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(
    dotenv_path=r"C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\.env"
)

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

IMAGES_DIR = r"C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\imagenes\para-subir"

PRODUCT = {
    "nombre_wc":     "Al Nassr Local",
    "nombre_imagen": "AL-NASSR-LOCAL",
    "calidad":       "Tipo original",
    "tallas":        ["S", "M", "L", "XL", "XXL"],
    "precio":        109900,
    "categoria":     "Al Nassr",
    "short_description": (
        '<img src="https://b370sports.com/wp-content/uploads/2025/11/GUIA-DE-TALLAS.png" '
        'alt="Guia de tallas B370" style="max-width:100%;height:auto;" />'
    ),
    "skus": {
        "S":   "",
        "M":   "2100002038605",
        "L":   "",
        "XL":  "2100002038704",
        "XXL": "",
    },
    "stock": {
        "S":   0,
        "M":   1,
        "L":   0,
        "XL":  0,
        "XXL": 0,
    },
    "imagenes": [
        "AL-NASSR-LOCAL_1.jpg",
        "AL-NASSR-LOCAL_2.jpg",
        "AL-NASSR-LOCAL_3.jpg",
        "AL-NASSR-LOCAL_4.jpg",
        "AL-NASSR-LOCAL_5.jpg",
        "AL-NASSR-LOCAL_6.jpg",
    ],
}


# ─── SSH ──────────────────────────────────────────────────────────────────────

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


def upload_images_scp(ssh_client):
    """Sube las imagenes a /tmp/ via SFTP."""
    sftp = ssh_client.open_sftp()
    uploaded = []
    for fname in PRODUCT["imagenes"]:
        local_path = os.path.join(IMAGES_DIR, fname)
        remote_path = f"/tmp/{fname}"
        if not os.path.exists(local_path):
            print(f"  ADVERTENCIA: No se encontro {local_path}")
            continue
        print(f"  Subiendo {fname} ...")
        sftp.put(local_path, remote_path)
        uploaded.append(fname)
        print(f"  OK -> /tmp/{fname}")
    sftp.close()
    return uploaded


def import_to_wp_media(ssh_client, uploaded_files):
    """Importa cada imagen a WP Media con WP-CLI y retorna dict fname->wp_id."""
    media_ids = {}
    for i, fname in enumerate(uploaded_files, start=1):
        remote_path = f"/tmp/{fname}"
        title = f"Al Nassr Local {i}"
        cmd = (
            f"wp media import {remote_path} "
            f'--title="{title}" '
            f"--path={SSH_PATH} 2>&1"
        )
        out, _ = ssh_exec(ssh_client, cmd)
        print(f"  WP-CLI import {fname}: {out[:120]}")
        # WP-CLI devuelve algo como: Imported file '/tmp/X.jpg' as attachment ID 1234.
        import re
        match = re.search(r"attachment ID (\d+)", out)
        if match:
            wp_id = int(match.group(1))
            media_ids[fname] = wp_id
            print(f"  -> WP Media ID: {wp_id}")
        else:
            print(f"  ADVERTENCIA: No se pudo extraer el WP Media ID de: {out[:200]}")
        time.sleep(0.5)
    return media_ids


def get_image_ids_from_wp(ssh_client):
    """Obtiene los IDs de WP Media para las imagenes AL-NASSR-LOCAL via grep."""
    cmd = (
        f"wp post list --post_type=attachment --fields=ID,guid "
        f"--format=csv --posts_per_page=9999 "
        f"--path={SSH_PATH} 2>/dev/null | grep -i 'AL-NASSR-LOCAL'"
    )
    out, _ = ssh_exec(ssh_client, cmd)
    import re
    ids = []
    for line in out.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(",", 1)
        if parts[0].strip().isdigit():
            ids.append(int(parts[0].strip()))
    return sorted(ids)


# ─── WOOCOMMERCE API ──────────────────────────────────────────────────────────

def get_or_create_category(nombre):
    r = requests.get(f"{API_BASE}/products/categories", auth=AUTH,
                     params={"search": nombre, "per_page": 20})
    if r.status_code == 200:
        for cat in r.json():
            if cat["name"].strip().lower() == nombre.strip().lower():
                print(f"  Categoria existente: {nombre} (ID: {cat['id']})")
                return cat["id"]
    # Crear
    r = requests.post(f"{API_BASE}/products/categories", auth=AUTH,
                      json={"name": nombre})
    if r.status_code in (200, 201):
        cat_id = r.json()["id"]
        print(f"  Categoria creada: {nombre} (ID: {cat_id})")
        return cat_id
    print(f"  ERROR creando categoria '{nombre}': {r.text[:150]}")
    return None


def product_exists(nombre):
    r = requests.get(f"{API_BASE}/products", auth=AUTH,
                     params={"search": nombre, "per_page": 10})
    if r.status_code == 200:
        for p in r.json():
            if p["name"].strip().lower() == nombre.strip().lower():
                return p["id"]
    return None


def create_parent_product(cat_id, image_ids):
    attrs = [
        {"name": "Tallas", "visible": True, "variation": True,
         "options": PRODUCT["tallas"]},
        {"name": "Calidad", "visible": True, "variation": True,
         "options": [PRODUCT["calidad"]]},
    ]
    images = []
    if image_ids:
        for wp_id in image_ids:
            images.append({"id": wp_id})

    payload = {
        "name":              PRODUCT["nombre_wc"],
        "type":              "variable",
        "status":            "publish",
        "categories":        [{"id": cat_id}] if cat_id else [],
        "attributes":        attrs,
        "short_description": PRODUCT["short_description"],
        "images":            images,
    }

    r = requests.post(f"{API_BASE}/products", auth=AUTH, json=payload)
    if r.status_code in (200, 201):
        prod_id = r.json()["id"]
        print(f"  Producto padre creado: {PRODUCT['nombre_wc']} (ID: {prod_id})")
        return prod_id
    print(f"  ERROR creando producto padre: {r.text[:200]}")
    return None


def create_variations(product_id):
    variation_ids = {}
    for talla in PRODUCT["tallas"]:
        sku   = PRODUCT["skus"].get(talla, "")
        stock = PRODUCT["stock"].get(talla, 0)

        attrs = [
            {"name": "Tallas",  "option": talla},
            {"name": "Calidad", "option": PRODUCT["calidad"]},
        ]

        payload = {
            "attributes":     attrs,
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
            vid = r.json()["id"]
            variation_ids[talla] = vid
            estado = "instock" if stock > 0 else "agotado"
            sku_display = sku if sku else "(sin SKU)"
            print(f"  {talla:4s} | SKU: {sku_display:20s} | Stock: {stock} ({estado}) | ID: {vid}")
        else:
            print(f"  ERROR {talla}: {r.text[:100]}")
        time.sleep(DELAY)

    return variation_ids


def assign_images_ssh(ssh_client, product_id, variation_ids_dict, image_ids):
    """Asigna _thumbnail_id y _product_image_gallery al producto padre."""
    if not image_ids:
        print("  ADVERTENCIA: Sin imagenes, asigna manualmente")
        return

    main_id     = image_ids[0]
    gallery_ids = image_ids[1:]
    gallery_str = ",".join(str(i) for i in gallery_ids)

    # Imagen destacada del padre
    cmd = f"wp post meta update {product_id} _thumbnail_id {main_id} --path={SSH_PATH}"
    out, _ = ssh_exec(ssh_client, cmd)
    print(f"  Padre _thumbnail_id -> {main_id} | {out[:60]}")

    # Galeria del padre
    if gallery_str:
        cmd = f"wp post meta update {product_id} _product_image_gallery '{gallery_str}' --path={SSH_PATH}"
        out, _ = ssh_exec(ssh_client, cmd)
        print(f"  Padre _product_image_gallery -> {gallery_str} | {out[:60]}")

    # Variaciones
    for talla, vid in variation_ids_dict.items():
        cmd = f"wp post meta update {vid} _thumbnail_id {main_id} --path={SSH_PATH}"
        ssh_exec(ssh_client, cmd)
        if gallery_str:
            cmd = f"wp post meta update {vid} wavi_value '{gallery_str}' --path={SSH_PATH}"
            ssh_exec(ssh_client, cmd)

    print(f"  {len(variation_ids_dict)} variaciones -> _thumbnail_id: {main_id}"
          + (f" | wavi_value: {gallery_str}" if gallery_str else ""))


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 62)
    print("  B370 — AL NASSR LOCAL — FLUJO COMPLETO")
    print("=" * 62)
    print(f"  Producto : {PRODUCT['nombre_wc']}")
    print(f"  Calidad  : {PRODUCT['calidad']}")
    print(f"  Precio   : ${PRODUCT['precio']:,}")
    print(f"  Tallas   : {', '.join(PRODUCT['tallas'])}")
    print("=" * 62)

    # ── 1. Conectar SSH ──────────────────────────────────────────────────────
    print("\n[1] Conectando SSH ...")
    try:
        ssh = ssh_connect()
        print(f"  Conectado a {SSH_HOST}:{SSH_PORT}")
    except Exception as e:
        print(f"  ERROR SSH: {e}")
        sys.exit(1)

    # ── 2. Subir imagenes ────────────────────────────────────────────────────
    print("\n[2] Subiendo imagenes a /tmp/ via SFTP ...")
    uploaded = upload_images_scp(ssh)
    print(f"  {len(uploaded)}/6 imagenes subidas")

    # ── 3. Importar a WP Media ───────────────────────────────────────────────
    print("\n[3] Importando a WP Media Library via WP-CLI ...")
    media_map = import_to_wp_media(ssh, uploaded)

    # Verificar IDs via grep como respaldo
    print("\n[3b] Verificando IDs en WP Media via grep ...")
    image_ids = get_image_ids_from_wp(ssh)
    if image_ids:
        print(f"  IDs encontrados: {image_ids}")
    else:
        # Usar los IDs que retorno wp media import
        image_ids = sorted(media_map.values())
        print(f"  IDs desde import: {image_ids}")

    # ── 4. Categoria ─────────────────────────────────────────────────────────
    print("\n[4] Categoria WooCommerce ...")
    cat_id = get_or_create_category(PRODUCT["categoria"])
    time.sleep(DELAY)

    # ── 5. Verificar si ya existe ────────────────────────────────────────────
    print("\n[5] Verificando si el producto ya existe ...")
    existing = product_exists(PRODUCT["nombre_wc"])
    if existing:
        print(f"  Ya existe: ID {existing} — abortando para no duplicar")
        ssh.close()
        sys.exit(0)
    print("  No existe — procediendo a crear")

    # ── 6. Crear producto padre ──────────────────────────────────────────────
    print("\n[6] Creando producto padre ...")
    product_id = create_parent_product(cat_id, image_ids)
    if not product_id:
        print("  ERROR critico — no se pudo crear el producto padre")
        ssh.close()
        sys.exit(1)
    time.sleep(DELAY)

    # ── 7. Crear variaciones ─────────────────────────────────────────────────
    print(f"\n[7] Creando {len(PRODUCT['tallas'])} variaciones ...")
    variation_ids = create_variations(product_id)
    print(f"  {len(variation_ids)}/{len(PRODUCT['tallas'])} variaciones creadas")

    # ── 8. Asignar imagenes ──────────────────────────────────────────────────
    print("\n[8] Asignando imagenes via SSH + WP-CLI ...")
    if image_ids:
        assign_images_ssh(ssh, product_id, variation_ids, image_ids)
    else:
        print("  Sin IDs de imagen disponibles — asigna manualmente")

    ssh.close()

    # ── RESUMEN ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 62)
    print("  RESUMEN FINAL")
    print("=" * 62)
    print(f"  Producto WC ID   : {product_id}")
    print(f"  WP Media IDs     : {image_ids}")
    print(f"  Variaciones:")
    for talla in PRODUCT["tallas"]:
        vid  = variation_ids.get(talla, "ERROR")
        sku  = PRODUCT["skus"].get(talla, "") or "(sin SKU)"
        stk  = PRODUCT["stock"].get(talla, 0)
        print(f"    {talla:4s} | ID: {vid} | SKU: {sku} | Stock: {stk}")
    skus_faltantes = [t for t in PRODUCT["tallas"] if not PRODUCT["skus"].get(t)]
    if skus_faltantes:
        print(f"  SKUs faltantes   : {', '.join(skus_faltantes)}")
    print("=" * 62)
    print(f"  URL: {WC_URL}/?p={product_id}")
    print("=" * 62)


if __name__ == "__main__":
    main()
