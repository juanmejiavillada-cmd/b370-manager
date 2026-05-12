#!/usr/bin/env python3
"""
B370 — Crear productos nuevos desde cero en WooCommerce
========================================================
Crea producto padre + variaciones + SKU + stock + imágenes + precio.

Uso:
    python b370_crear_producto.py

Requisitos en .env:
    WC_URL, WC_CK, WC_CS, SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS, SSH_PATH
"""

import os
import sys
import time
import paramiko
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Forzar UTF-8 en la salida para que los emojis funcionen en Windows
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
DELAY    = 0.3   # segundos entre llamadas a la API


# ── LISTA DE PRODUCTOS ────────────────────────────────────────────────────────
# Para agregar más productos, añade otro dict a esta lista.
# Campos obligatorios: nombre_wc, nombre_imagen, calidad, tallas, precio,
#                      categoria, skus, stock
# Campo informativo:   nombre_quenti (referencia interna, no se usa en la API)
# ─────────────────────────────────────────────────────────────────────────────
PRODUCTS = [
    {
        "nombre_wc":     "BARCELONA 4A EQUIPACION TIPO ORIGINAL",
        "nombre_quenti": "CAMISETA DE BARCELONA CUARTA EQUIPACION TIPO ORIGINAL",
        "nombre_imagen": "BARCELONA_4_EQUIPACION_TIPO_ORIGINAL",
        "calidad":       "Tipo jugador",
        "tallas":        ["S", "M", "L", "XL", "XXL"],
        "precio":        120000,
        "categoria":     "Barcelona",
        "skus":  {"S": "2100002006109", "M": "2100002006208", "L": "21000020075337",
                  "XL": "2100002006307", "XXL": "2100002004023"},
        "stock": {"S": 1, "M": 0, "L": 2, "XL": 1, "XXL": 0},
    },
    {
        "nombre_wc":     "BARCELONA LOCAL 2026 TIPO ORIGINAL",
        "nombre_quenti": "CAMISETA DE BARCELONA LOCAL TIPO ORIGINAL DE HOMBRE",
        "nombre_imagen": "BARCELONA_LOCAL_2026_TIPO_ORIGINAL",
        "calidad":       "Tipo jugador",
        "tallas":        ["S", "M", "L", "XL", "XXL"],
        "precio":        110000,
        "categoria":     "Barcelona",
        "skus":  {"S": "2100000752701", "M": "2100000752800", "L": "2100000752909",
                  "XL": "2100000753005", "XXL": "2100000753104"},
        "stock": {"S": 0, "M": 3, "L": 1, "XL": 0, "XXL": 0},
    },
    {
        "nombre_wc":     "RETRO PILSEN MEDELLIN",
        "nombre_quenti": "CAMISETA DE MEDELLIN RETRO PILSEN BLANCA DE HOMBRE",
        "nombre_imagen": "RETRO_PILSEN_MEDELLIN",
        "calidad":       "Retro",
        "tallas":        ["S", "M", "L", "XL", "XXL"],
        "precio":        80000,
        "categoria":     "Medellín",
        "skus":  {"S": "2100001063806", "M": "2100001063905", "L": "2100001064001",
                  "XL": "2100001064100", "XXL": "2100001064209"},
        "stock": {"S": 0, "M": 2, "L": 0, "XL": 2, "XXL": 0},
    },
    {
        "nombre_wc":     "MEDELLIN LOCAL 2026 TIPO FAN",
        "nombre_quenti": "CAMISETA DE MEDELLIN LOCAL FAN DE HOMBRE",
        "nombre_imagen": "MEDELLIN_LOCAL_2026_TIPO_FAN",
        "calidad":       "Tipo fan",
        "tallas":        ["S", "M", "L", "XL", "XXL"],
        "precio":        80000,
        "categoria":     "Medellín",
        "skus":  {"S": "2100000781800", "M": "2100000918305", "L": "2100000782005",
                  "XL": "2100000782104", "XXL": "2100000947305"},
        "stock": {"S": 2, "M": 0, "L": 0, "XL": 1, "XXL": 1},
    },
    {
        "nombre_wc":     "RETRO KONGA MEDELLIN",
        "nombre_quenti": "CAMISETA DE MEDELLIN RETRO KONGA ROJA DE HOMBRE",
        "nombre_imagen": "RETRO_KONGA_MEDELLIN",
        "calidad":       "Retro",
        "tallas":        ["S", "M", "L", "XL", "XXL"],
        "precio":        80000,
        "categoria":     "Medellín",
        "skus":  {"S": "2100001015805", "M": "2100001015904", "L": "2100001016000",
                  "XL": "2100001016109", "XXL": "2100001016208"},
        "stock": {"S": 0, "M": 3, "L": 1, "XL": 2, "XXL": 0},
    },
    {
        "nombre_wc":     "CHAPECOENSE 1.1",
        "nombre_quenti": "CAMISETA DE CHAPECOENSE LOCAL 1,1 DE HOMBRE",
        "nombre_imagen": "CHAPECOENSE_1_1",
        "calidad":       "1.1",
        "tallas":        ["S", "M", "L", "XL", "XXL"],
        "precio":        120000,
        "categoria":     "Internacional",
        "skus":  {"S": "2100002002200", "M": "2100002002309", "L": "2100002002408",
                  "XL": "2100002002507", "XXL": "2100002034003"},
        "stock": {"S": 2, "M": 5, "L": 0, "XL": 0, "XXL": 0},
    },
]


# ── SSH ───────────────────────────────────────────────────────────────────────

def ssh_connect():
    """Establece conexión SSH. Devuelve el cliente o None si falla."""
    if not SSH_PASS:
        print("  ⚠️  SSH_PASS no está en el .env — imágenes se asignarán manualmente")
        return None
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS,
                       timeout=15)
        print("  ✅ Conectado al servidor SSH")
        return client
    except Exception as e:
        print(f"  ⚠️  No se pudo conectar por SSH: {e}")
        return None


def ssh_exec(client, cmd):
    """Ejecuta un comando en el servidor SSH y devuelve su salida."""
    full_cmd = f"cd {SSH_PATH} && {cmd}"
    _, stdout, stderr = client.exec_command(full_cmd)
    out = stdout.read().decode(errors="replace").strip()
    return out


def get_image_ids(client, nombre_imagen):
    """
    Busca IDs de imágenes en la biblioteca de medios de WordPress
    filtrando por el nombre de archivo en la URL (guid).
    Devuelve lista de IDs ordenada de menor a mayor:
      IDs[0]  → imagen principal (_1)
      IDs[1:] → galería adicional (_2, _3, ...)
    """
    # Obtenemos todos los attachments y filtramos por nombre de imagen en la URL.
    # Usamos grep sobre el guid porque --search de WP-CLI busca en el título
    # (que WordPress convierte a espacios), no en la URL del archivo.
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
    return sorted(ids)  # menor ID = primera imagen subida = imagen principal


def assign_images_ssh(client, product_id, variation_ids, image_ids):
    """
    Asigna imagen principal y galería a cada variación via WP-CLI:
      _thumbnail_id → ID de la imagen _1
      wavi_value    → IDs de las imágenes _2, _3, ... separados por coma

    También actualiza la imagen destacada del producto padre.
    """
    if not image_ids:
        print("  ⚠️  No se encontraron imágenes — asigna manualmente")
        return

    main_id = image_ids[0]
    gallery_ids = image_ids[1:]
    gallery_str = ",".join(str(i) for i in gallery_ids)

    # Imagen destacada del producto padre
    ssh_exec(client, f"wp post meta update {product_id} _thumbnail_id {main_id}")
    print(f"  ✅ Imagen padre  → _thumbnail_id: {main_id}")

    # Imagen y galería en cada variación
    for vid in variation_ids:
        ssh_exec(client, f"wp post meta update {vid} _thumbnail_id {main_id}")
        if gallery_str:
            ssh_exec(client, f"wp post meta update {vid} wavi_value '{gallery_str}'")

    print(f"  ✅ Variaciones   → _thumbnail_id: {main_id}"
          + (f" | wavi_value: {gallery_str}" if gallery_str else ""))


# ── WOOCOMMERCE API ───────────────────────────────────────────────────────────

def get_or_create_category(nombre):
    """Obtiene el ID de una categoría; la crea si no existe."""
    r = requests.get(f"{API_BASE}/products/categories", auth=AUTH,
                     params={"search": nombre, "per_page": 20})
    if r.status_code == 200:
        for cat in r.json():
            if cat["name"].lower() == nombre.lower():
                return cat["id"]
    # No existe → crear
    r = requests.post(f"{API_BASE}/products/categories", auth=AUTH,
                      json={"name": nombre})
    if r.status_code in (200, 201):
        return r.json()["id"]
    print(f"  ❌ Error creando categoría '{nombre}': {r.text[:150]}")
    return None


def product_exists(nombre):
    """
    Verifica si ya hay un producto con el mismo nombre.
    Devuelve su ID si existe, None en caso contrario.
    """
    r = requests.get(f"{API_BASE}/products", auth=AUTH,
                     params={"search": nombre, "per_page": 10})
    if r.status_code == 200:
        for p in r.json():
            if p["name"].strip().lower() == nombre.strip().lower():
                return p["id"]
    return None


def create_parent_product(product, cat_id, image_ids=None):
    """
    Crea el producto padre de tipo variable en WooCommerce.
    Incluye imagen principal si se proporcionan IDs de imagen.
    Devuelve el ID del producto creado, o None si falla.
    """
    attrs = [
        {"name": "Tallas", "visible": True, "variation": True,
         "options": product["tallas"]}
    ]
    if product.get("calidad"):
        attrs.append(
            {"name": "Calidad", "visible": True, "variation": True,
             "options": [product["calidad"]]}
        )

    payload = {
        "name":       product["nombre_wc"],
        "type":       "variable",
        "status":     "publish",
        "categories": [{"id": cat_id}] if cat_id else [],
        "attributes": attrs,
    }

    # Asignar imagen principal al padre vía API si ya la tenemos
    if image_ids:
        payload["images"] = [{"id": image_ids[0]}]

    r = requests.post(f"{API_BASE}/products", auth=AUTH, json=payload)
    if r.status_code in (200, 201):
        return r.json()["id"]
    print(f"  ❌ Error creando producto padre: {r.text[:200]}")
    return None


def create_variations(product_id, product):
    """
    Crea una variación por cada talla con su SKU, stock y precio.
    Devuelve lista de IDs de las variaciones creadas.
    """
    variation_ids = []
    for talla in product["tallas"]:
        sku   = product["skus"].get(talla, "")
        stock = product["stock"].get(talla, 0)

        attrs = [{"name": "Tallas", "option": talla}]
        if product.get("calidad"):
            attrs.append({"name": "Calidad", "option": product["calidad"]})

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
            estado = "instock" if stock > 0 else "agotado"
            print(f"  ✅ {talla:4s} — SKU: {sku:20s} | Stock: {stock} ({estado}) | ID: {vid}")
        else:
            print(f"  ❌ {talla:4s} — Error: {r.text[:100]}")
        time.sleep(DELAY)

    return variation_ids


# ── PROCESO PRINCIPAL ─────────────────────────────────────────────────────────

def process_product(product, ssh_client):
    """Ejecuta el flujo completo para un producto. Devuelve (ok, n_variaciones)."""
    nombre = product["nombre_wc"]
    print(f"\n{'='*62}")
    print(f"  🟡 {nombre}")
    if product.get("nombre_quenti"):
        print(f"     Quenti: {product['nombre_quenti']}")
    print(f"{'='*62}")

    # 1. ¿Ya existe el producto?
    existing_id = product_exists(nombre)
    if existing_id:
        print(f"  ⚠️  Ya existe en WooCommerce (ID: {existing_id}) — saltando")
        return False, 0

    # 2. Buscar imágenes ANTES de crear el producto (para incluirla en el padre)
    image_ids = []
    if ssh_client:
        print(f"\n  🖼️  Buscando imágenes '{product['nombre_imagen']}' en WordPress...")
        image_ids = get_image_ids(ssh_client, product["nombre_imagen"])
        if image_ids:
            print(f"  ✅ Imágenes encontradas: {image_ids}")
        else:
            print(f"  ⚠️  No se encontraron imágenes para '{product['nombre_imagen']}'")

    # 3. Categoría
    cat_id = get_or_create_category(product["categoria"])
    if cat_id:
        print(f"\n  📁 Categoría: {product['categoria']} (ID: {cat_id})")
    else:
        print(f"\n  ⚠️  No se pudo obtener la categoría '{product['categoria']}'")
    time.sleep(DELAY)

    # 4. Crear producto padre
    product_id = create_parent_product(product, cat_id, image_ids)
    if not product_id:
        print("  ❌ No se pudo crear el producto padre — abortando este producto")
        return False, 0
    print(f"  ✅ Producto padre creado (ID: {product_id})")
    time.sleep(DELAY)

    # 5. Crear variaciones
    print(f"\n  📦 Creando {len(product['tallas'])} variaciones...")
    variation_ids = create_variations(product_id, product)
    print(f"  → {len(variation_ids)} de {len(product['tallas'])} variaciones creadas")

    # 6. Asignar imágenes a variaciones via SSH
    if ssh_client and variation_ids and image_ids:
        print(f"\n  🖼️  Asignando imágenes a variaciones...")
        assign_images_ssh(ssh_client, product_id, variation_ids, image_ids)
    elif not image_ids:
        print(f"\n  ⚠️  Sin imágenes — asigna manualmente en el panel de WordPress")

    return True, len(variation_ids)


def main():
    print("\n" + "="*62)
    print("  B370 — CREAR PRODUCTOS NUEVOS DESDE CERO")
    print("="*62)
    print(f"  Tienda : {WC_URL}")
    print(f"  Total  : {len(PRODUCTS)} productos a procesar")
    print("="*62)

    # Conectar SSH
    print("\n🔌 Conectando a servidor SSH...")
    ssh_client = ssh_connect()

    total_productos   = 0
    total_variaciones = 0
    omitidos          = 0

    for product in PRODUCTS:
        try:
            ok, n_vars = process_product(product, ssh_client)
            if ok:
                total_productos   += 1
                total_variaciones += n_vars
            else:
                omitidos += 1
        except Exception as ex:
            print(f"\n  ❌ Error inesperado procesando '{product['nombre_wc']}': {ex}")
            omitidos += 1
        time.sleep(DELAY)

    if ssh_client:
        ssh_client.close()

    print(f"\n{'='*62}")
    print("  RESUMEN FINAL")
    print(f"{'='*62}")
    print(f"  ✅ Productos creados  : {total_productos}")
    print(f"  ✅ Variaciones creadas: {total_variaciones}")
    if omitidos:
        print(f"  ⚠️  Productos omitidos : {omitidos} (ya existían o fallaron)")
    if not SSH_PASS:
        print(f"\n  ⚠️  PENDIENTE: Agrega SSH_PASS al .env para asignar")
        print(f"     imágenes automáticamente en próximas ejecuciones")
    print("="*62)
    input("\n  Presiona ENTER para cerrar...")


if __name__ == "__main__":
    main()
