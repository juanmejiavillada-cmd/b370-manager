import requests
from requests.auth import HTTPBasicAuth
import json

WC_URL = "https://b370sports.com"
WC_CK = "ck_820f0c1aded087d593791f97abbdeec382b15492"
WC_CS = "cs_6a5f94897927878d28d8d76096e9758e2b103c49"

auth = HTTPBasicAuth(WC_CK, WC_CS)
headers = {"Content-Type": "application/json"}

guia_tallas_html = '<img src="https://b370sports.com/wp-content/uploads/2025/11/GUIA-DE-TALLAS.png" alt="Guía de tallas B370" style="max-width:100%;height:auto;" />'

product_data = {
    "name": "Manchester United Local",
    "type": "variable",
    "status": "publish",
    "catalog_visibility": "visible",
    "categories": [{"id": 93}],
    "short_description": guia_tallas_html,
    "images": [
        {"id": 3239},
        {"id": 3240},
        {"id": 3241},
        {"id": 3242},
        {"id": 3243},
        {"id": 3244},
    ],
    "attributes": [
        {
            "name": "Tallas",
            "slug": "tallas",
            "position": 0,
            "visible": True,
            "variation": True,
            "options": ["S", "M", "L", "XL", "XXL"],
        },
        {
            "name": "Calidad",
            "slug": "calidad",
            "position": 1,
            "visible": True,
            "variation": True,
            "options": ["Tipo original"],
        },
    ],
}

url = f"{WC_URL}/wp-json/wc/v3/products"
resp = requests.post(url, auth=auth, headers=headers, json=product_data)
print("Status:", resp.status_code)
data = resp.json()
if resp.status_code in (200, 201):
    print("Product ID:", data["id"])
    print("Name:", data["name"])
    print("Status:", data["status"])
else:
    print("ERROR:", json.dumps(data, indent=2))
