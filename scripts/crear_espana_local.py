import requests
from requests.auth import HTTPBasicAuth
import json

wc_url = "https://b370sports.com"
ck = "ck_820f0c1aded087d593791f97abbdeec382b15492"
cs = "cs_6a5f94897927878d28d8d76096e9758e2b103c49"
auth = HTTPBasicAuth(ck, cs)

# WP Media IDs confirmed
media_ids = [3162, 3163, 3164, 3165, 3166, 3167, 3168, 3169]

guia_tallas_html = (
    '<img src="https://b370sports.com/wp-content/uploads/2025/11/GUIA-DE-TALLAS.png" '
    'alt="Guía de tallas B370" style="max-width:100%;height:auto;" />'
)

product_data = {
    "name": "España Local",
    "type": "variable",
    "status": "publish",
    "catalog_visibility": "visible",
    "categories": [
        {"id": 103},   # ESPANA (creada)
        {"id": 35},    # SELECCIONES
        {"id": 34},    # EUROPA
    ],
    "images": [{"id": mid} for mid in media_ids],
    "short_description": guia_tallas_html,
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

resp = requests.post(wc_url + "/wp-json/wc/v3/products", auth=auth, json=product_data)
product = resp.json()

print("Status:", resp.status_code)
print("Product ID:", product.get("id"))
print("Name:", product.get("name"))
print("Status:", product.get("status"))
print("Permalink:", product.get("permalink"))
print("Categories:", [c.get("name") for c in product.get("categories", [])])
print("Images:", [img.get("id") for img in product.get("images", [])])

if resp.status_code not in (200, 201):
    print("ERROR BODY:", json.dumps(product, indent=2))
