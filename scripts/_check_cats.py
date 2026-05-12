#!/usr/bin/env python3
import os, requests, sys
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
CK = os.getenv("WC_CK"); CS = os.getenv("WC_CS"); URL = os.getenv("WC_URL")
auth = HTTPBasicAuth(CK, CS)

r = requests.get(f"{URL}/wp-json/wc/v3/products/categories", auth=auth, params={"per_page": 100})
cats = r.json()

print("=== CATEGORIAS RELACIONADAS ===")
for c in cats:
    n = c["name"].upper()
    if any(k in n for k in ["BAYER", "MUNICH", "GERMANY", "ALEMANIA", "EUROPA", "EUROPEO", "BUNDESLIGA"]):
        print(f"  ID:{c['id']:4d}  {c['name']}  (count:{c['count']})")

print()
print("=== TODAS LAS CATEGORIAS ===")
for c in sorted(cats, key=lambda x: x["name"]):
    print(f"  ID:{c['id']:4d}  {c['name']}")
