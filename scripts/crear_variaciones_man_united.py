import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('195.35.15.241', port=65002, username='u122447978', password='Operacionesb370.', timeout=30)

WC_CK = "ck_820f0c1aded087d593791f97abbdeec382b15492"
WC_CS = "cs_6a5f94897927878d28d8d76096e9758e2b103c49"
WC_URL = "https://b370sports.com"
PRODUCT_ID = 3246

# SKUs from Quenti: only 2XL has a SKU (Tipo original with dorsal)
# S, M, L, XL = no SKU found in Quenti for Tipo original
# XXL (2XL) = 2100001034202
tallas_skus = {
    "S":   "",
    "M":   "",
    "L":   "",
    "XL":  "",
    "XXL": "2100001034202",
}

precio = 109900  # Tipo original

created = []
for talla, sku in tallas_skus.items():
    variation = {
        "status": "publish",
        "regular_price": str(precio),
        "sku": sku,
        "manage_stock": True,
        "stock_quantity": 0,
        "attributes": [
            {"name": "Tallas", "option": talla},
            {"name": "Calidad", "option": "Tipo original"},
        ],
    }

    payload_json = json.dumps(variation).replace("'", "'\\''")
    cmd = f"""curl -s -X POST '{WC_URL}/wp-json/wc/v3/products/{PRODUCT_ID}/variations' \\
      -u '{WC_CK}:{WC_CS}' \\
      -H 'Content-Type: application/json' \\
      -d '{payload_json}'"""

    stdin, stdout, stderr = ssh.exec_command(cmd)
    resp = stdout.read().decode().strip()
    try:
        data = json.loads(resp)
        if "id" in data:
            vid = data["id"]
            var_sku = data.get("sku", "")
            var_price = data.get("regular_price", "")
            var_attrs = [(a["name"], a["option"]) for a in data.get("attributes", [])]
            print(f"  Talla {talla}: Variation ID={vid}, SKU={var_sku!r}, Price={var_price}, Attrs={var_attrs}")
            created.append({"talla": talla, "id": vid, "sku": var_sku, "price": var_price})
        else:
            print(f"  Talla {talla}: ERROR - {json.dumps(data, ensure_ascii=False)[:300]}")
    except Exception as e:
        print(f"  Talla {talla}: Parse error - {resp[:200]}")

ssh.close()
print("\nSummary:")
for v in created:
    print(f"  {v['talla']:4s} | ID={v['id']} | SKU={v['sku']!r:25s} | Price=${v['price']}")
