#!/usr/bin/env python3
"""
B370 -- Crear BAYER MUNICH VISITANTE TIPO ORIGINAL
====================================================
Flujo completo:
  1. Verificar que el producto no exista en WC
  2. Subir 5 imagenes via SCP al servidor
  3. Importar imagenes a WordPress Media via WP-CLI
  4. Crear producto padre variable en WooCommerce
  5. Crear 5 variaciones (S, M, L, XL, XXL) con SKUs de Quenti
  6. Asignar imagenes al padre y variaciones via WP-CLI

Datos de Quenti (CUENTI INVENTARIO 6 ABRIL.xlsx):
  S   -> sin SKU               | stock: 0
  M   -> SKU: 2100001032000    | stock: 0
  L   -> SKU: 2100001001501    | stock: 1
  XL  -> SKU: 2100001001600    | stock: 0
  XXL -> SKU: 2100001001709    | stock: 0

Categoria WooCommerce: BAYERN MUNICH (ID 91)
B370_DRY_RUN=false -> ejecuta en produccion
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

load_dotenv()

WC_URL       = os.getenv("WC_URL", "https://b370sports.com")
CK           = os.getenv("WC_CK")
CS           = os.getenv("WC_CS")
SSH_HOST     = os.getenv("SSH_HOST")
SSH_PORT     = int(os.getenv("SSH_PORT", 65002))
SSH_USER     = os.getenv("SSH_USER")
SSH_PASS     = os.getenv("SSH_PASS")
SSH_PATH     = os.getenv("SSH_PATH", "~/domains/b370sports.com/public_html")
SSH_PATH_ABS = f"/home/{SSH_USER}/domains/b370sports.com/public_html"

AUTH     = HTTPBasicAuth(CK, CS)
API_BASE = f"{WC_URL}/wp-json/wc/v3"
DELAY    = 0.4

IMAGES_LOCAL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "imagenes", "para-subir"
)

PRODUCTO = {
    "nombre_wc":     "Bayer Munich Visitante Tipo Original",
    "nombre_imagen": "BAYER-MUNICH-VISITANTE-TIPO-ORIGINAL",
    "calidad":       "Tipo original",
    "tallas":        ["S", "M", "L", "XL", "XXL"],
    "precio":        109900,
    "categoria_id":  91,
    "categoria":     "BAYERN MUNICH",
    # SKUs de Quenti (codigo de barras 13 digitos). None = sin SKU
    "skus": {
        "S":   None,
        "M":   "2100001032000",
        "L":   "2100001001501",
        "XL":  "2100001001600",
        "XXL": "2100001001709",
    },
    "stock": {
        "S":   0,
        "M":   0,
        "L":   1,
        "XL":  0,
        "XXL": 0,
    },
}

N_IMAGENES = 5  # _1.jpg a _5.jpg


# -- SSH -----------------------------------------------------------------------

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER,
                   password=SSH_PASS, timeout=15)
    print(f"  OK Conectado al servidor SSH ({SSH_USER}@{SSH_HOST}:{SSH_PORT})")
    return client


def ssh_exec(client, cmd, cwd=None):
    base = f"cd {cwd or SSH_PATH} && " if cwd else ""
    full = base + cmd
    _, stdout, stderr = client.exec_command(full)
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    return out, err


# -- PASO 1+2: Subir e importar imagenes --------------------------------------

def subir_e_importar_imagenes(client, nombre_imagen, n_imgs):
    sftp = client.open_sftp()
    remote_tmp = f"{SSH_PATH_ABS}/wp-content/uploads/b370-import"

    try:
        sftp.mkdir(remote_tmp)
        print(f"  OK Carpeta remota creada: {remote_tmp}")
    except IOError:
        print(f"  OK Carpeta remota ya existe: {remote_tmp}")

    archivos_subidos = []
    for i in range(1, n_imgs + 1):
        nombre_archivo = f"{nombre_imagen}_{i}.jpg"
        local_path     = os.path.join(IMAGES_LOCAL_DIR, nombre_archivo)
        remote_path    = f"{remote_tmp}/{nombre_archivo}"

        if not os.path.exists(local_path):
            print(f"  ADVERTENCIA Archivo no encontrado localmente: {local_path}")
            continue

        print(f"  Subiendo {nombre_archivo}...")
        sftp.put(local_path, remote_path)
        archivos_subidos.append((nombre_archivo, remote_path))
        print(f"  OK {nombre_archivo} subido")

    sftp.close()

    if not archivos_subidos:
        print("  ERROR No se subio ningun archivo")
        return []

    print(f"\n  Importando {len(archivos_subidos)} imagenes a WordPress Media...")
    wp_ids = []
    for nombre_archivo, remote_path in archivos_subidos:
        cmd = (
            f"wp media import {remote_path} "
            f"--title='{nombre_archivo}' "
            f"--path={SSH_PATH_ABS} "
            f"--allow-root --porcelain 2>/dev/null"
        )
        out, err = ssh_exec(client, cmd)
        if out.strip().isdigit():
            wp_id = int(out.strip())
            wp_ids.append(wp_id)
            print(f"  OK {nombre_archivo} -> WP Media ID: {wp_id}")
        else:
            print(f"  ERROR Importando {nombre_archivo}: {out} | {err}")
        time.sleep(0.5)

    print(f"\n  Limpiando archivos temporales en servidor...")
    for nombre_archivo, remote_path in archivos_subidos:
        ssh_exec(client, f"rm -f {remote_path}")
    ssh_exec(client, f"rmdir {remote_tmp} 2>/dev/null || true")

    print(f"  OK {len(wp_ids)} imagenes importadas a WordPress")
    return wp_ids


# -- PASO 3: Producto padre ----------------------------------------------------

def product_exists(nombre):
    r = requests.get(f"{API_BASE}/products", auth=AUTH,
                     params={"search": nombre, "per_page": 10})
    if r.status_code == 200:
        for p in r.json():
            if p["name"].strip().lower() == nombre.strip().lower():
                return p["id"]
    return None


def create_parent_product(producto, image_ids):
    attrs = [
        {"name": "Tallas",  "visible": True, "variation": True,
         "options": producto["tallas"]},
        {"name": "Calidad", "visible": True, "variation": True,
         "options": [producto["calidad"]]},
    ]
    payload = {
        "name":       producto["nombre_wc"],
        "type":       "variable",
        "status":     "publish",
        "categories": [{"id": producto["categoria_id"]}],
        "attributes": attrs,
    }
    if image_ids:
        payload["images"] = [{"id": image_ids[0]}]

    r = requests.post(f"{API_BASE}/products", auth=AUTH, json=payload)
    if r.status_code in (200, 201):
        return r.json()["id"]
    print(f"  ERROR Creando producto padre: {r.text[:300]}")
    return None


# -- PASO 4: Variaciones -------------------------------------------------------

def create_variations(product_id, producto):
    variation_ids = []
    for talla in producto["tallas"]:
        sku   = producto["skus"].get(talla) or ""
        stock = producto["stock"].get(talla, 0)

        attrs = [
            {"name": "Tallas",  "option": talla},
            {"name": "Calidad", "option": producto["calidad"]},
        ]
        payload = {
            "attributes":     attrs,
            "regular_price":  str(producto["precio"]),
            "manage_stock":   True,
            "stock_quantity": stock,
            "stock_status":   "instock" if stock > 0 else "outofstock",
        }
        if sku:
            payload["sku"] = sku

        r = requests.post(
            f"{API_BASE}/products/{product_id}/variations",
            auth=AUTH, json=payload
        )
        if r.status_code in (200, 201):
            vid = r.json()["id"]
            variation_ids.append(vid)
            estado    = "instock" if stock > 0 else "agotado"
            sku_label = sku if sku else "(sin SKU)"
            print(f"  OK {talla:4s} | SKU: {sku_label:22s} | Stock: {stock} ({estado}) | ID: {vid}")
        else:
            print(f"  ERROR {talla}: {r.text[:180]}")
        time.sleep(DELAY)

    return variation_ids


# -- PASO 5: Asignar imagenes --------------------------------------------------

def assign_images_to_product(client, product_id, variation_ids, image_ids):
    if not image_ids:
        print("  ADVERTENCIA Sin imagenes para asignar")
        return

    main_id     = image_ids[0]
    gallery_ids = image_ids[1:]
    gallery_str = ",".join(str(i) for i in gallery_ids)

    # Imagen principal del producto padre
    ssh_exec(client,
             f"wp post meta update {product_id} _thumbnail_id {main_id} "
             f"--path={SSH_PATH_ABS} --allow-root")
    print(f"  OK Padre (ID {product_id}) -> _thumbnail_id: {main_id}")

    # Galeria del producto padre
    if gallery_str:
        ssh_exec(client,
                 f"wp post meta update {product_id} _product_image_gallery '{gallery_str}' "
                 f"--path={SSH_PATH_ABS} --allow-root")
        print(f"  OK Padre (ID {product_id}) -> galeria: [{gallery_str}]")

    # Variaciones: thumbnail + wavi_value
    for vid in variation_ids:
        ssh_exec(client,
                 f"wp post meta update {vid} _thumbnail_id {main_id} "
                 f"--path={SSH_PATH_ABS} --allow-root")
        if gallery_str:
            ssh_exec(client,
                     f"wp post meta update {vid} wavi_value '{gallery_str}' "
                     f"--path={SSH_PATH_ABS} --allow-root")

    print(f"  OK {len(variation_ids)} variaciones -> _thumbnail_id: {main_id}"
          + (f" | galeria: [{gallery_str}]" if gallery_str else ""))


# -- PROCESO PRINCIPAL ---------------------------------------------------------

def main():
    print("\n" + "=" * 62)
    print("  B370 -- BAYER MUNICH VISITANTE TIPO ORIGINAL")
    print("  MODO: PRODUCCION (B370_DRY_RUN=false)")
    print("=" * 62)
    print(f"  Tienda  : {WC_URL}")
    print(f"  Precio  : ${PRODUCTO['precio']:,}")
    print(f"  Calidad : {PRODUCTO['calidad']}")
    print(f"  Tallas  : {', '.join(PRODUCTO['tallas'])}")
    print(f"  Cat ID  : {PRODUCTO['categoria_id']} ({PRODUCTO['categoria']})")
    print(f"  Imagenes: {N_IMAGENES}")
    print(f"  SSH path: {SSH_PATH_ABS}")
    print()

    # Verificar imagenes locales
    print("VERIFICANDO IMAGENES LOCALES...")
    faltantes = []
    for i in range(1, N_IMAGENES + 1):
        nombre = f"{PRODUCTO['nombre_imagen']}_{i}.jpg"
        ruta   = os.path.join(IMAGES_LOCAL_DIR, nombre)
        if os.path.exists(ruta):
            print(f"  OK {nombre}")
        else:
            print(f"  FALTA {nombre}")
            faltantes.append(nombre)
    if faltantes:
        print(f"\n  ERROR Faltan {len(faltantes)} imagen(es). Abortando.")
        return

    # Conectar SSH
    print(f"\nCONECTANDO SSH a {SSH_HOST}:{SSH_PORT}...")
    try:
        client = ssh_connect()
    except Exception as e:
        print(f"  ERROR SSH: {e}")
        return

    # PASO 1+2: Subir e importar imagenes
    print(f"\n[PASO 1+2] SUBIR E IMPORTAR {N_IMAGENES} IMAGENES...")
    image_ids = subir_e_importar_imagenes(client, PRODUCTO["nombre_imagen"], N_IMAGENES)
    if len(image_ids) < N_IMAGENES:
        print(f"  ADVERTENCIA Solo se importaron {len(image_ids)} de {N_IMAGENES} imagenes")

    # PASO 3: Verificar + crear producto padre
    print(f"\nVERIFICANDO si '{PRODUCTO['nombre_wc']}' ya existe...")
    existing_id = product_exists(PRODUCTO["nombre_wc"])
    if existing_id:
        print(f"  ADVERTENCIA Producto ya existe en WooCommerce (ID: {existing_id}) -- abortando")
        client.close()
        return
    print("  OK Producto no existe -- procediendo a crear")
    time.sleep(DELAY)

    print(f"\n[PASO 3] CREANDO PRODUCTO PADRE...")
    product_id = create_parent_product(PRODUCTO, image_ids)
    if not product_id:
        print("  ERROR No se pudo crear el producto padre")
        client.close()
        return
    print(f"  OK Producto padre creado (ID: {product_id})")
    time.sleep(DELAY)

    # PASO 4: Crear variaciones
    print(f"\n[PASO 4] CREANDO {len(PRODUCTO['tallas'])} VARIACIONES...")
    variation_ids = create_variations(product_id, PRODUCTO)
    print(f"  -> {len(variation_ids)} de {len(PRODUCTO['tallas'])} variaciones creadas")

    # PASO 5: Asignar imagenes
    if image_ids and variation_ids:
        print(f"\n[PASO 5] ASIGNANDO IMAGENES...")
        assign_images_to_product(client, product_id, variation_ids, image_ids)

    client.close()

    # REPORTE FINAL
    print(f"\n{'='*62}")
    print("  REPORTE FINAL")
    print(f"{'='*62}")
    print(f"  Producto padre ID : {product_id}")
    print(f"  Variaciones IDs   : {variation_ids}")
    print(f"  Imagenes WP IDs   : {image_ids}")
    print(f"  URL Admin         : {WC_URL}/wp-admin/post.php?post={product_id}&action=edit")
    print(f"{'='*62}")


if __name__ == "__main__":
    main()
