"""
Script de importación de inventario Quenti — 1 Mayo 2026
Ejecuta en producción (B370_DRY_RUN=false en .env).

Correcciones vs versión anterior:
- SKUs float -> int -> str (elimina .0)
- wc_get con **kwargs en lugar de params={}
- Reintentos con backoff en errores de conexion SSL
"""
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from b370_mcp import core
import pandas as pd
import requests as req_lib

EXCEL_PRINCIPAL = PROJECT_ROOT / "data" / "INVENTARIO_ACTUALIZADO_1_MAYO.xlsx"
EXCEL_FALLBACK  = PROJECT_ROOT / "data" / "INVENTARIO 1 MAYO.xlsx"
MAX_RETRIES = 3
RETRY_DELAY = 2.0  # segundos entre reintentos


def wc_get_con_retry(path: str, **kwargs):
    """wc_get con reintentos en errores de conexion."""
    for intento in range(MAX_RETRIES):
        try:
            r = core.wc_get(path, **kwargs)
            return r
        except (req_lib.exceptions.ConnectionError, req_lib.exceptions.Timeout) as e:
            if intento < MAX_RETRIES - 1:
                print(f"    [conexion] reintento {intento+1}/{MAX_RETRIES}: {type(e).__name__}")
                time.sleep(RETRY_DELAY * (intento + 1))
            else:
                raise


def wc_put_con_retry(path: str, payload: dict):
    """wc_put con reintentos en errores de conexion."""
    for intento in range(MAX_RETRIES):
        try:
            r = core.wc_put(path, payload)
            return r
        except (req_lib.exceptions.ConnectionError, req_lib.exceptions.Timeout) as e:
            if intento < MAX_RETRIES - 1:
                print(f"    [conexion] reintento {intento+1}/{MAX_RETRIES}: {type(e).__name__}")
                time.sleep(RETRY_DELAY * (intento + 1))
            else:
                raise


print("=== B370 Importacion Inventario Quenti ===")
print(f"DRY_RUN: {core.DRY_RUN}")
print(f"WC_URL:  {core.WC_URL}")
print()

# 1. Verificar archivo
if EXCEL_PRINCIPAL.exists():
    excel_path = EXCEL_PRINCIPAL
elif EXCEL_FALLBACK.exists():
    excel_path = EXCEL_FALLBACK
else:
    print("ERROR: No se encontro ningun archivo Excel")
    sys.exit(1)

print(f"Archivo: {excel_path.name}")

# 2. Leer y normalizar Excel
print("\n--- Procesando Excel ---")
df = pd.read_excel(excel_path)
df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]
print(f"Filas totales: {len(df)}")

# Normalizar SKUs: float 2100000990905.0 -> string "2100000990905"
def normalizar_sku(val):
    if pd.isna(val):
        return ""
    try:
        return str(int(float(str(val).strip())))
    except (ValueError, OverflowError):
        return str(val).strip()

df["sku_norm"] = df["codigo_barras"].apply(normalizar_sku)
df["existencias_int"] = (
    df["existencias"]
    .apply(lambda x: x if str(x).replace(".", "").replace("-", "").isdigit() else 0)
    .astype(float).fillna(0).astype(int)
)

# Solo filas con SKU real (>= 10 chars, no nan)
df_valido = df[
    (df["sku_norm"] != "") &
    (df["sku_norm"] != "nan") &
    (df["sku_norm"].str.len() >= 10)
].copy()

stock_map = dict(zip(df_valido["sku_norm"], df_valido["existencias_int"]))
print(f"SKUs validos en Excel: {len(stock_map)}")
print(f"Muestra (5 SKUs): {dict(list(stock_map.items())[:5])}")

# 3. Obtener todos los product_ids de WC
print("\n--- Obteniendo productos de WooCommerce ---")
all_product_ids = []
page = 1
while True:
    resp = wc_get_con_retry("products", status="publish", per_page=100, page=page)
    if resp.status_code != 200:
        print(f"ERROR obteniendo productos (pagina {page}): {resp.status_code}")
        break
    batch = resp.json()
    if not batch:
        break
    for p in batch:
        all_product_ids.append(p["id"])
    print(f"  Pagina {page}: {len(batch)} productos (acumulado: {len(all_product_ids)})")
    if len(batch) < 100:
        break
    page += 1
    time.sleep(0.5)

print(f"Total productos WC: {len(all_product_ids)}")

if not all_product_ids:
    print("ERROR: No se pudieron obtener productos de WC")
    sys.exit(1)

# 4. Obtener todas las variaciones con sus SKUs
print("\n--- Escaneando variaciones ---")
variaciones_totales = []
for i, pid in enumerate(all_product_ids):
    try:
        vresp = wc_get_con_retry(f"products/{pid}/variations", per_page=100)
        if vresp.status_code != 200:
            print(f"  WARN: producto {pid} -> HTTP {vresp.status_code}")
            continue
        vars_prod = vresp.json()
        for v in vars_prod:
            variaciones_totales.append({
                "product_id": pid,
                "variation_id": v["id"],
                "sku": (v.get("sku") or "").strip(),
                "stock_actual": v.get("stock_quantity"),
            })
        time.sleep(0.4)
    except Exception as e:
        print(f"  ERROR producto {pid}: {e}")
        continue

    if (i + 1) % 5 == 0 or (i + 1) == len(all_product_ids):
        print(f"  {i+1}/{len(all_product_ids)} productos escaneados, {len(variaciones_totales)} variaciones total")

print(f"\nTotal variaciones encontradas: {len(variaciones_totales)}")

# 5. Cruzar SKUs
con_match = [(v, stock_map[v["sku"]]) for v in variaciones_totales if v["sku"] and v["sku"] in stock_map]
sin_match  = [v for v in variaciones_totales if not v["sku"] or v["sku"] not in stock_map]

print(f"Con match SKU:  {len(con_match)}")
print(f"Sin match SKU:  {len(sin_match)}")

# 6. Actualizar stock
print(f"\n--- Actualizando stock (DRY_RUN={core.DRY_RUN}) ---")
total_ok = 0
total_err = 0
detalle_err = []

for idx, (v, qty) in enumerate(con_match):
    pid = v["product_id"]
    vid = v["variation_id"]
    sku = v["sku"]
    payload = {
        "manage_stock": True,
        "stock_quantity": qty,
        "stock_status": "instock" if qty > 0 else "outofstock",
    }
    try:
        r = wc_put_con_retry(f"products/{pid}/variations/{vid}", payload)
        if r.status_code == 200:
            total_ok += 1
            print(f"  OK  [{idx+1}/{len(con_match)}] SKU {sku} -> stock {qty}")
        else:
            total_err += 1
            detalle_err.append({"sku": sku, "var": vid, "status": r.status_code, "body": r.text[:100]})
            print(f"  ERR [{idx+1}/{len(con_match)}] SKU {sku} -> HTTP {r.status_code}")
    except Exception as e:
        total_err += 1
        detalle_err.append({"sku": sku, "var": vid, "error": str(e)[:120]})
        print(f"  ERR [{idx+1}/{len(con_match)}] SKU {sku} -> {type(e).__name__}: {str(e)[:80]}")
    time.sleep(core.DELAY)

# 7. Resultado final
print("\n=== RESULTADO FINAL ===")
print(f"Archivo:                  {excel_path.name}")
print(f"Filas en Excel:           {len(df)}")
print(f"SKUs validos en Excel:    {len(stock_map)}")
print(f"Productos WC:             {len(all_product_ids)}")
print(f"Variaciones totales WC:   {len(variaciones_totales)}")
print(f"Variaciones actualizadas: {total_ok}")
print(f"Sin match SKU:            {len(sin_match)}")
print(f"Errores:                  {total_err}")

if detalle_err:
    print("\nVariaciones con error:")
    for e in detalle_err[:20]:
        print(f"  SKU {e.get('sku')} | var {e.get('var')} | {e.get('status', e.get('error', '?'))}")
