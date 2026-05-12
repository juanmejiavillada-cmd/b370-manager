"""Diagnostico: formato de SKUs en Excel vs WooCommerce."""
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from b370_mcp import core
import pandas as pd

# Ver SKUs del Excel (raw antes de normalizar)
print("=== SKUs en Excel (primeros 10 con codigo_barras) ===")
df = pd.read_excel(PROJECT_ROOT / "data" / "INVENTARIO_ACTUALIZADO_1_MAYO.xlsx")
df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]
muestra = df[df["codigo_barras"].notna()]["codigo_barras"].head(10)
for val in muestra:
    print(f"  raw={repr(val)}  ->  str={str(val).strip()}")

# Normalizar como lo hace el tool (strip, astype str)
df["codigo_barras"] = df["codigo_barras"].astype(str).str.strip()
# Eliminar decimales .0
df["codigo_barras_clean"] = df["codigo_barras"].str.replace(r"\.0$", "", regex=True)
print("\nPrimeros 10 SKUs normalizados (con .0 eliminado):")
for val in df[df["codigo_barras_clean"] != "nan"]["codigo_barras_clean"].head(10):
    print(f"  [{val}] len={len(val)}")

# Ver SKUs en WC
print("\n=== SKUs en WooCommerce (primeras 2 variaciones de cada producto) ===")
resp = core.wc_get("products", params={"status": "publish", "per_page": 10, "page": 1})
prods = resp.json()
for p in prods[:5]:
    pid = p["id"]
    nombre = p["name"]
    vresp = core.wc_get(f"products/{pid}/variations", params={"per_page": 5})
    for v in vresp.json()[:3]:
        sku = v.get("sku", "")
        print(f"  prod={nombre[:30]} | var={v['id']} | SKU=[{sku}] len={len(sku)}")
    time.sleep(0.2)
