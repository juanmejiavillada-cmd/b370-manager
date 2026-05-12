import requests
from requests.auth import HTTPBasicAuth
import json

WC_URL = 'https://b370sports.com'
WC_CK = 'ck_820f0c1aded087d593791f97abbdeec382b15492'
WC_CS = 'cs_6a5f94897927878d28d8d76096e9758e2b103c49'

auth = HTTPBasicAuth(WC_CK, WC_CS)
headers = {'Content-Type': 'application/json'}

# WP Media IDs from import
media_ids = [3214, 3215, 3216, 3217, 3218, 3219, 3220]

# SKUs from Quenti (Tipo Original)
skus = {
    'M':   '2100002026701',
    'L':   '2100002026800',
    'XL':  '2100002026909',
    'XXL': '2100002027005',
    'S':   None,  # Not in Quenti
}

# Step 1: Create parent product
product_data = {
    "name": "Bayern Munich Tercera Equipación",
    "type": "variable",
    "status": "publish",
    "catalog_visibility": "visible",
    "categories": [{"id": 91}],
    "images": [{"id": mid} for mid in media_ids],
    "short_description": '<img src="https://b370sports.com/wp-content/uploads/2025/11/GUIA-DE-TALLAS.png" alt="Guía de tallas B370" style="max-width:100%;height:auto;" />',
    "attributes": [
        {
            "name": "Tallas",
            "position": 0,
            "visible": True,
            "variation": True,
            "options": ["S", "M", "L", "XL", "XXL"]
        },
        {
            "name": "Calidad",
            "position": 1,
            "visible": True,
            "variation": True,
            "options": ["Tipo original"]
        }
    ]
}

print('=== PASO 4: Crear producto padre ===')
resp = requests.post(
    f'{WC_URL}/wp-json/wc/v3/products',
    json=product_data,
    auth=auth,
    headers=headers
)
print(f'Status: {resp.status_code}')

if resp.status_code not in (200, 201):
    print(f'ERROR: {resp.text[:500]}')
    exit(1)

product = resp.json()
product_id = product['id']
print(f'Product ID: {product_id}')
print(f'Product URL: {product.get("permalink", "")}')

# Step 2: Create variations
print('\n=== PASO 5: Crear variaciones ===')
tallas = ['S', 'M', 'L', 'XL', 'XXL']
variation_ids = {}
skus_faltantes = []

for talla in tallas:
    sku = skus.get(talla)
    variation_data = {
        "status": "publish",
        "price": "109900",
        "regular_price": "109900",
        "attributes": [
            {"name": "Tallas", "option": talla},
            {"name": "Calidad", "option": "Tipo original"}
        ],
        "manage_stock": True,
        "stock_quantity": 0,
    }
    if sku:
        variation_data["sku"] = sku
    else:
        skus_faltantes.append(talla)

    resp_var = requests.post(
        f'{WC_URL}/wp-json/wc/v3/products/{product_id}/variations',
        json=variation_data,
        auth=auth,
        headers=headers
    )
    if resp_var.status_code in (200, 201):
        var = resp_var.json()
        variation_ids[talla] = var['id']
        print(f'  Talla {talla} -> Var ID: {var["id"]}, SKU: {sku or "(sin SKU)"}')
    else:
        print(f'  ERROR talla {talla}: {resp_var.text[:300]}')

print('\n=== RESULTADO FINAL ===')
print(f'WC Product ID: {product_id}')
print(f'WP Media IDs: {media_ids}')
print(f'Portada (thumbnail): {media_ids[0]}')
print(f'Galeria: {media_ids[1:]}')
print()
print('Variaciones:')
for talla, var_id in variation_ids.items():
    sku = skus.get(talla)
    print(f'  {talla}: Var ID {var_id}, SKU: {sku or "SIN SKU"}')
print()
if skus_faltantes:
    print(f'SKUs faltantes (no en Quenti): {skus_faltantes}')
else:
    print('Todos los SKUs asignados')
