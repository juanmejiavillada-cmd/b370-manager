"""
Creación completa de Medellin Arquero Morada en WooCommerce b370sports.com

Flujo:
  1. Verificar que no exista el producto
  2. Buscar categoría "Medellin" (o equipos colombianos) en WC
  3. Subir 5 imágenes vía SCP al servidor
  4. Importar imágenes a WP Media Library vía WP-CLI por SSH
  5. Crear producto variable padre
  6. Crear 5 variaciones (S, M, L, XL, XXL) con SKUs de Quenti a $119.900
  7. Asignar imagen principal (_thumbnail_id) y galería (wavi_value) via WP-CLI

SKUs de Quenti (CUENTI INVENTARIO 6 ABRIL.xlsx):
  S   → 2100000917209
  M   → 2100000917308
  L   → 2100000917506
  XL  → 2100000917704
  XXL → 2100000917902

Ejecutar: python scripts/crear_medellin_arquero_morada.py
"""

import sys
import time
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from b370_mcp import core

# ─── Configuración del producto ──────────────────────────────────────────────
NOMBRE_WC       = "Medellin Arquero Morada"
NOMBRE_IMAGEN   = "MEDELLIN-ARQUERO-MORADA"
CALIDAD         = "1.1"
TALLAS          = ["S", "M", "L", "XL", "XXL"]
PRECIO          = 119900
CATEGORIA_BUSCAR = "Medellin"

SKUS = {
    "S":   "2100000917209",
    "M":   "2100000917308",
    "L":   "2100000917506",
    "XL":  "2100000917704",
    "XXL": "2100000917902",
}

STOCK = {
    "S":   0,
    "M":   0,
    "L":   0,
    "XL":  0,
    "XXL": 2,
}

IMAGENES_DIR     = PROJECT_ROOT / "imagenes" / "para-subir"
SSH_DEST_PATH    = "/home/u122447978/domains/b370sports.com/public_html/wp-content/uploads/b370/"
WP_CLI_PATH      = "/home/u122447978/domains/b370sports.com/public_html"

log = core.log


# ─── 1. Verificar existencia ─────────────────────────────────────────────────
print("\n=== PASO 1: Verificar existencia del producto ===")
existing_id = core.product_exists(NOMBRE_WC)
if existing_id:
    print(f"  ERROR: Ya existe el producto '{NOMBRE_WC}' con ID {existing_id}")
    print("  Aborting. Usa consultar_producto para ver el estado actual.")
    sys.exit(1)
print(f"  OK: Producto '{NOMBRE_WC}' no existe. Procedemos.")


# ─── 2. Buscar categoría ─────────────────────────────────────────────────────
print("\n=== PASO 2: Buscar categoría de Medellin ===")
r = core.wc_get("products/categories", search=CATEGORIA_BUSCAR, per_page=20)
cat_id = None
if r.status_code == 200:
    for cat in r.json():
        print(f"  Encontrada: id={cat['id']} name={cat['name']}")
        if cat["name"].lower() in ("medellin", "medellín", "atlético medellín", "atletico medellin"):
            cat_id = cat["id"]
            print(f"  >> Usando categoría: {cat['name']} (id={cat_id})")
            break
    if not cat_id and r.json():
        # Usar la primera que contenga medellin
        cat_id = r.json()[0]["id"]
        print(f"  >> Usando primera encontrada: {r.json()[0]['name']} (id={cat_id})")

if not cat_id:
    # Crear categoría si no existe
    print(f"  No encontrada. Creando categoría '{CATEGORIA_BUSCAR}'...")
    r2 = core.wc_post("products/categories", {"name": CATEGORIA_BUSCAR})
    if r2.status_code in (200, 201):
        cat_id = r2.json()["id"]
        print(f"  Categoría creada: id={cat_id}")
    else:
        print(f"  ERROR creando categoría: {r2.status_code} {r2.text[:100]}")
        cat_id = None

print(f"  cat_id final = {cat_id}")


# ─── 3. Subir imágenes vía SCP ───────────────────────────────────────────────
print("\n=== PASO 3: Subir imágenes vía SCP ===")
imagenes = sorted(IMAGENES_DIR.glob(f"{NOMBRE_IMAGEN}_*.jpg"))
print(f"  Encontradas {len(imagenes)} imágenes locales:")
for img in imagenes:
    print(f"    {img.name}")

# SCP usando plink/pscp o paramiko
import paramiko

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        core.SSH_HOST,
        port=core.SSH_PORT,
        username=core.SSH_USER,
        password=core.SSH_PASS,
        timeout=30,
    )
    return client

# Usar paramiko para subir archivos
print(f"  Conectando SSH a {core.SSH_HOST}:{core.SSH_PORT}...")
try:
    ssh = get_ssh_client()
    print("  SSH conectado OK")

    # Crear directorio destino si no existe
    mkdir_cmd = f"mkdir -p {SSH_DEST_PATH}"
    print(f"  Creando directorio: {mkdir_cmd}")
    _, stdout, stderr = ssh.exec_command(mkdir_cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"  mkdir stdout: '{out}' stderr: '{err[:100]}'")
    time.sleep(1)

    # Subir vía SFTP
    sftp = ssh.open_sftp()
    for img in imagenes:
        dest = SSH_DEST_PATH + img.name
        print(f"  Subiendo {img.name} -> {dest}...")
        sftp.put(str(img), dest)
        print(f"    OK")
    sftp.close()
    print("  Todas las imágenes subidas via SFTP.")
    ssh.close()
except Exception as e:
    print(f"  ERROR en SFTP: {e}")
    print("  Abortando.")
    sys.exit(1)


# ─── 4. Importar a WP Media Library ─────────────────────────────────────────
print("\n=== PASO 4: Importar imágenes a WP Media Library ===")
wp_image_ids = []

try:
    ssh = get_ssh_client()
    for img in imagenes:
        src_path = SSH_DEST_PATH + img.name
        cmd = f"wp media import {src_path} --path={WP_CLI_PATH} --porcelain 2>/dev/null"
        full_cmd = f"cd {WP_CLI_PATH} && {cmd}"
        print(f"  Importando {img.name}...")
        _, stdout, stderr = ssh.exec_command(full_cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if out.isdigit():
            wp_id = int(out)
            wp_image_ids.append(wp_id)
            print(f"    WP Media ID: {wp_id}")
        else:
            print(f"    WARN: salida inesperada: '{out}' | err: '{err[:100]}'")
            # Intentar extraer el ID con grep
            cmd2 = f"wp media import {src_path} --path={WP_CLI_PATH} 2>/dev/null | grep -oP 'ID \\K[0-9]+'"
            _, stdout2, _ = ssh.exec_command(f"cd {WP_CLI_PATH} && {cmd2}")
            out2 = stdout2.read().decode().strip()
            if out2.isdigit():
                wp_image_ids.append(int(out2))
                print(f"    WP Media ID (método 2): {int(out2)}")
        time.sleep(0.5)
    ssh.close()
except Exception as e:
    print(f"  ERROR en WP-CLI import: {e}")
    sys.exit(1)

print(f"\n  WP Image IDs importados: {wp_image_ids}")
if len(wp_image_ids) < 5:
    print("  WARN: No se importaron todas las imágenes. Continuamos con las disponibles.")

if not wp_image_ids:
    print("  ERROR CRÍTICO: No hay IDs de imagen. Abortando.")
    sys.exit(1)

main_image_id   = wp_image_ids[0]
gallery_ids     = wp_image_ids[1:]
print(f"  Principal: {main_image_id} | Galería: {gallery_ids}")


# ─── 5. Crear producto variable padre ────────────────────────────────────────
print("\n=== PASO 5: Crear producto variable padre ===")
attrs = [
    {"name": "Tallas", "visible": True, "variation": True, "options": TALLAS},
    {"name": "Calidad", "visible": True, "variation": True, "options": [CALIDAD]},
]

payload_padre = {
    "name": NOMBRE_WC,
    "type": "variable",
    "status": "publish",
    "categories": [{"id": cat_id}] if cat_id else [],
    "attributes": attrs,
    "images": [{"id": main_image_id}],
}

r = core.wc_post("products", payload_padre)
if r.status_code not in (200, 201):
    print(f"  ERROR creando producto: {r.status_code} {r.text[:200]}")
    sys.exit(1)

producto = r.json()
product_id = producto["id"]
print(f"  Producto creado: ID={product_id} name={producto['name']}")
print(f"  Permalink: {producto.get('permalink')}")
time.sleep(core.DELAY)


# ─── 6. Crear variaciones ────────────────────────────────────────────────────
print("\n=== PASO 6: Crear variaciones ===")
variation_ids = []

for talla in TALLAS:
    payload_var = {
        "attributes": [
            {"name": "Tallas", "option": talla},
            {"name": "Calidad", "option": CALIDAD},
        ],
        "sku": SKUS[talla],
        "regular_price": str(PRECIO),
        "manage_stock": True,
        "stock_quantity": STOCK.get(talla, 0),
        "stock_status": "instock" if STOCK.get(talla, 0) > 0 else "outofstock",
    }
    r = core.wc_post(f"products/{product_id}/variations", payload_var)
    if r.status_code in (200, 201):
        v = r.json()
        variation_ids.append(v["id"])
        print(f"  Variacion {talla}: ID={v['id']} SKU={SKUS[talla]} precio={PRECIO} stock={STOCK.get(talla,0)}")
    else:
        print(f"  ERROR variacion {talla}: {r.status_code} {r.text[:150]}")
    time.sleep(core.DELAY)

print(f"\n  Variaciones creadas: {len(variation_ids)} de {len(TALLAS)}")
print(f"  IDs: {variation_ids}")


# ─── 7. Asignar imágenes ─────────────────────────────────────────────────────
print("\n=== PASO 7: Asignar imágenes via WP-CLI ===")

try:
    ssh = get_ssh_client()

    gallery_str = ",".join(str(i) for i in gallery_ids)

    # Asignar al producto padre
    print(f"  Padre (ID={product_id}): _thumbnail_id={main_image_id}, gallery={gallery_str}")
    cmd1 = f"wp post meta update {product_id} _thumbnail_id {main_image_id} --path={WP_CLI_PATH} 2>/dev/null"
    _, stdout, _ = ssh.exec_command(f"cd {WP_CLI_PATH} && {cmd1}")
    stdout.read()

    if gallery_ids:
        # Galería del producto padre via _product_image_gallery
        cmd_gallery = f"wp post meta update {product_id} _product_image_gallery '{gallery_str}' --path={WP_CLI_PATH} 2>/dev/null"
        _, stdout, _ = ssh.exec_command(f"cd {WP_CLI_PATH} && {cmd_gallery}")
        stdout.read()
        # wavi_value también
        cmd_wavi = f"wp post meta update {product_id} wavi_value '{gallery_str}' --path={WP_CLI_PATH} 2>/dev/null"
        _, stdout, _ = ssh.exec_command(f"cd {WP_CLI_PATH} && {cmd_wavi}")
        stdout.read()

    # Asignar a cada variación
    for vid in variation_ids:
        print(f"  Variacion ID={vid}: _thumbnail_id={main_image_id}")
        cmd_v1 = f"wp post meta update {vid} _thumbnail_id {main_image_id} --path={WP_CLI_PATH} 2>/dev/null"
        _, stdout, _ = ssh.exec_command(f"cd {WP_CLI_PATH} && {cmd_v1}")
        stdout.read()
        if gallery_ids:
            cmd_v2 = f"wp post meta update {vid} wavi_value '{gallery_str}' --path={WP_CLI_PATH} 2>/dev/null"
            _, stdout, _ = ssh.exec_command(f"cd {WP_CLI_PATH} && {cmd_v2}")
            stdout.read()
        time.sleep(0.2)

    # También asignar via REST API la imagen a cada variación
    print("  Asignando imagen via REST API a variaciones...")
    for vid in variation_ids:
        r = core.wc_put(f"products/{product_id}/variations/{vid}", {"image": {"id": main_image_id}})
        if r.status_code == 200:
            print(f"    Variacion {vid}: imagen REST OK")
        else:
            print(f"    Variacion {vid}: REST WARN {r.status_code}")
        time.sleep(0.2)

    ssh.close()
    print("  Imágenes asignadas correctamente.")

except Exception as e:
    print(f"  ERROR en asignación de imágenes: {e}")


# ─── Resumen final ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("RESUMEN FINAL — Medellin Arquero Morada")
print("="*60)
print(f"  Producto ID:      {product_id}")
print(f"  Nombre WC:        {NOMBRE_WC}")
print(f"  Categoría ID:     {cat_id}")
print(f"  Precio:           ${PRECIO:,}")
print(f"  Calidad:          {CALIDAD}")
print(f"  WP Image IDs:     {wp_image_ids}")
print(f"  Principal img ID: {main_image_id}")
print(f"  Galería IDs:      {gallery_ids}")
print()
print("  Variaciones:")
print(f"  {'Talla':<6} {'Variacion ID':<14} {'SKU':<16} {'Stock':<6}")
print(f"  {'-'*50}")
for talla, vid in zip(TALLAS, variation_ids):
    print(f"  {talla:<6} {vid:<14} {SKUS[talla]:<16} {STOCK.get(talla, 0):<6}")
print()
print(f"  URL: https://b370sports.com/?p={product_id}")
print("="*60)
