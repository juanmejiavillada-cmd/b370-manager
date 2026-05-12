import requests
from requests.auth import HTTPBasicAuth
import json

wc_url = "https://b370sports.com"
ck = "ck_820f0c1aded087d593791f97abbdeec382b15492"
cs = "cs_6a5f94897927878d28d8d76096e9758e2b103c49"
auth = HTTPBasicAuth(ck, cs)

product_id = 3170

# SKUs from Quenti - only L has SKU for Tipo original con dorsal
skus = {
    "S": None,
    "M": None,
    "L": "2100036967204",
    "XL": None,
    "XXL": None,
}

# Stock from Quenti - L has 1 unit
stock = {
    "S": 0,
    "M": 0,
    "L": 1,
    "XL": 0,
    "XXL": 0,
}

tallas = ["S", "M", "L", "XL", "XXL"]
precio = "109900"

results = []

for talla in tallas:
    variation_data = {
        "regular_price": precio,
        "status": "publish",
        "manage_stock": True,
        "stock_quantity": stock[talla],
        "attributes": [
            {
                "name": "Tallas",
                "option": talla
            },
            {
                "name": "Calidad",
                "option": "Tipo original"
            }
        ]
    }
    if skus[talla]:
        variation_data["sku"] = skus[talla]

    resp = requests.post(
        f"{wc_url}/wp-json/wc/v3/products/{product_id}/variations",
        auth=auth,
        json=variation_data
    )
    var = resp.json()
    var_id = var.get("id")
    results.append({
        "talla": talla,
        "variation_id": var_id,
        "sku": skus[talla],
        "stock": stock[talla],
        "precio": precio,
        "status": resp.status_code
    })
    print(f"Talla {talla}: ID={var_id} SKU={skus[talla]} Stock={stock[talla]} Status={resp.status_code}")

print()
print("=== RESUMEN VARIACIONES ===")
for r in results:
    sku_str = r["sku"] if r["sku"] else "SIN SKU"
    print(f"  {r['talla']}: VariationID={r['variation_id']} | SKU={sku_str} | Stock={r['stock']} | Precio=$109.900")
