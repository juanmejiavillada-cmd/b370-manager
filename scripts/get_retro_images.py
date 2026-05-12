#!/usr/bin/env python3
"""Obtiene las URLs de imágenes de los productos retro de Colombia."""
import os, sys, requests
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

WC_URL = os.getenv("WC_URL")
WC_CK  = os.getenv("WC_CK")
WC_CS  = os.getenv("WC_CS")

auth = (WC_CK, WC_CS)

# Buscar todos los productos retro de Colombia
r = requests.get(
    f"{WC_URL}/wp-json/wc/v3/products",
    params={"search": "colombia", "per_page": 50, "status": "publish"},
    auth=auth, timeout=20
)
products = r.json()

print(f"Productos encontrados: {len(products)}\n")
for p in products:
    name = p.get("name", "")
    pid  = p.get("id", "")
    slug = p.get("slug", "")
    img  = p.get("images", [{}])[0].get("src", "(sin imagen)")
    cats = [c["name"] for c in p.get("categories", [])]
    print(f"ID {pid} | {name}")
    print(f"  SLUG: {slug}")
    print(f"  IMG:  {img}")
    print(f"  CATS: {cats}")
    print()
