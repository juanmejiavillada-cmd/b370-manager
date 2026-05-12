#!/usr/bin/env python3
"""
B370 — EJECUCIÓN: Normalización Calidad + precios Tipo fan
Aplica cambios reales vía WooCommerce REST API.

Reglas finales (acordadas con Juanjo 2026-04-21):
  1) Rename Calidad "Tipo jugador" → "Tipo original" (2 productos)
  2) Inferir Calidad en 24 productos sin atributo (por nombre + precio)
  3) Variaciones Tipo fan → $68.000
     EXCEPCIONES:
       - #1868 TIPO POLO COLOMBIA  → NO TOCAR (queda como está)
       - #2775 RETRO MANCHESTER UNITED 2008 → queda en $75.000 (no bajar)
  4) Retro Colombia #1875 y #1877 → precio $75.000
  5) Productos Retro por nombre → Calidad=Retro, no tocar precio
"""

import os, sys, time, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

load_dotenv()
WC_URL = os.getenv("WC_URL", "https://b370sports.com")
AUTH   = HTTPBasicAuth(os.getenv("WC_CK"), os.getenv("WC_CS"))
API    = f"{WC_URL}/wp-json/wc/v3"

FAN_PRICE_TARGET = "68000"
SKIP_KEYWORDS    = ("BUZO","BUSO","GABAN","GABÁN","GUAYO","CHAQUETA","PANTALON","PANTALÓN","ENTRENO")

# Excluidos de cualquier cambio de precio
PRICE_EXCLUDE_IDS = {1868, 2775}

# Override: productos Retro Colombia con precio $75.000
RETRO_COLOMBIA_75K = {1875, 1877}

def get_all_products():
    out, page = [], 1
    while True:
        r = requests.get(f"{API}/products", auth=AUTH,
                         params={"per_page":100,"page":page,"status":"publish"})
        if r.status_code != 200: break
        data = r.json()
        if not data: break
        out.extend(data); page += 1
    return out

def get_variaciones(pid):
    r = requests.get(f"{API}/products/{pid}/variations", auth=AUTH, params={"per_page":100})
    return r.json() if r.status_code == 200 else []

def calidad_value(p):
    for a in p.get("attributes", []):
        if a.get("name") == "Calidad":
            opts = a.get("options", [])
            return opts[0] if opts else None
    return None

def infer_line(name, price):
    n = (name or "").upper()
    if any(k in n for k in SKIP_KEYWORDS): return None
    if "RETRO" in n: return "Retro"
    try: pr = float(price or 0)
    except: pr = 0
    if pr and pr <= 80000: return "Tipo fan"
    if pr and pr >= 100000: return "Tipo original"
    return None

def set_product_calidad(p, nuevo_valor):
    """Asigna/renombra la Calidad de un producto (atributo a nivel product)."""
    pid = p["id"]
    attrs = p.get("attributes", [])
    found = False
    for a in attrs:
        if a.get("name") == "Calidad":
            a["options"] = [nuevo_valor]
            a["visible"] = True
            found = True
            break
    if not found:
        attrs.append({
            "name": "Calidad",
            "options": [nuevo_valor],
            "visible": True,
            "variation": False,
        })
    r = requests.put(f"{API}/products/{pid}", auth=AUTH, json={"attributes": attrs})
    return r.status_code in (200, 201)

def update_var_price(pid, vid, precio):
    r = requests.put(f"{API}/products/{pid}/variations/{vid}",
                     auth=AUTH, json={"regular_price": str(precio)})
    return r.status_code in (200, 201)

def update_product_price(pid, precio):
    r = requests.put(f"{API}/products/{pid}", auth=AUTH,
                     json={"regular_price": str(precio)})
    return r.status_code in (200, 201)

def main():
    print("="*70)
    print("  B370 — EJECUTANDO normalización de Calidad + precios")
    print("="*70)
    confirm = input("\n  ¿Confirmas ejecución sobre PRODUCCIÓN? (escribe SI): ").strip().upper()
    if confirm != "SI":
        print("  ❌ Cancelado."); return

    products = get_all_products()
    print(f"\n  📦 Productos publicados: {len(products)}\n")

    ok_rename = ok_infer = ok_price_var = ok_price_prod = err = 0

    for p in products:
        pid, name = p["id"], p["name"]
        cal = calidad_value(p)
        price = p.get("price") or p.get("regular_price")

        # ── 1) RENAME Tipo jugador → Tipo original ─────────────────
        if cal == "Tipo jugador":
            if set_product_calidad(p, "Tipo original"):
                print(f"   🔁 #{pid} rename → Tipo original  ({name})")
                ok_rename += 1; cal = "Tipo original"
            else:
                print(f"   ❌ #{pid} error rename  ({name})"); err += 1
            time.sleep(0.3)

        # ── 2) INFERIR Calidad ─────────────────────────────────────
        if cal is None:
            inferred = infer_line(name, price)
            if inferred:
                if set_product_calidad(p, inferred):
                    print(f"   🧩 #{pid} calidad={inferred:<14} ({name})")
                    ok_infer += 1; cal = inferred
                else:
                    print(f"   ❌ #{pid} error inferir  ({name})"); err += 1
                time.sleep(0.3)

        # ── 4) Retro Colombia con precio $75.000 ───────────────────
        if pid in RETRO_COLOMBIA_75K:
            # setear precio a nivel producto (son simples)
            if update_product_price(pid, 75000):
                print(f"   💲 #{pid} precio producto → $75.000  ({name})")
                ok_price_prod += 1
            time.sleep(0.3)

        # ── 3) Precios Tipo fan → $68.000 ──────────────────────────
        if pid in PRICE_EXCLUDE_IDS:
            continue  # no tocar precios de #1868 ni #2775
        if cal != "Tipo fan":
            continue

        for v in get_variaciones(pid):
            vid = v["id"]
            vprice = v.get("regular_price") or v.get("price")
            vcal = next((a["option"] for a in v.get("attributes",[]) if a["name"]=="Calidad"), None)
            is_fan_var = (vcal == "Tipo fan") or (vcal is None)  # si el producto es Tipo fan puro
            if not is_fan_var: continue
            if str(vprice) == FAN_PRICE_TARGET: continue
            if update_var_price(pid, vid, FAN_PRICE_TARGET):
                print(f"   💲 #{pid} var#{vid} ${vprice} → $68.000  ({name})")
                ok_price_var += 1
            else:
                err += 1
            time.sleep(0.25)

    print("\n" + "="*70)
    print(f"  ✅ Renombrados:     {ok_rename}")
    print(f"  ✅ Calidad inferida:{ok_infer}")
    print(f"  ✅ Precios var:     {ok_price_var}")
    print(f"  ✅ Precios prod:    {ok_price_prod}")
    if err: print(f"  ❌ Errores:         {err}")
    print("="*70)
    input("\n  ENTER para cerrar...")

if __name__ == "__main__":
    main()
