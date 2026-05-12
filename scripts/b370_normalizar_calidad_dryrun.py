#!/usr/bin/env python3
"""
B370 — DRY RUN: Normalización de atributo Calidad + precios Tipo fan
No ejecuta cambios. Solo muestra el plan.

Reglas:
  1) Productos con Calidad="Tipo jugador"  → renombrar a "Tipo original"
  2) Productos SIN Calidad (inferencia por nombre + precio):
        - nombre contiene "RETRO"                    → Retro          (NO tocar precio)
        - precio ≤ 80000 y no es buzo/gaban/guayo    → Tipo fan
        - precio ≥ 100000                            → Tipo original
        - buzos/gabanes/guayos                       → SKIP
  3) Todas las variaciones con Calidad="Tipo fan"  → precio $68.000
  4) Retro: NUNCA se toca precio
"""

import os, sys, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()
WC_URL = os.getenv("WC_URL", "https://b370sports.com")
AUTH   = HTTPBasicAuth(os.getenv("WC_CK"), os.getenv("WC_CS"))
API    = f"{WC_URL}/wp-json/wc/v3"

FAN_PRICE_TARGET = "68000"
SKIP_KEYWORDS    = ("BUZO", "GABAN", "GABÁN", "GUAYO", "CHAQUETA", "PANTALON", "PANTALÓN")

def get_all_products():
    out, page = [], 1
    while True:
        r = requests.get(f"{API}/products", auth=AUTH,
                         params={"per_page": 100, "page": page, "status": "publish"})
        if r.status_code != 200: break
        data = r.json()
        if not data: break
        out.extend(data); page += 1
    return out

def get_variaciones(pid):
    r = requests.get(f"{API}/products/{pid}/variations", auth=AUTH, params={"per_page": 100})
    return r.json() if r.status_code == 200 else []

def calidad_value(p):
    for a in p.get("attributes", []):
        if a.get("name") == "Calidad":
            opts = a.get("options", [])
            return opts[0] if opts else None
    return None

def infer_line(name, price):
    n = (name or "").upper()
    if any(k in n for k in SKIP_KEYWORDS):
        return None  # skip
    if "RETRO" in n:
        return "Retro"
    try: pr = float(price or 0)
    except: pr = 0
    if pr and pr <= 80000:
        return "Tipo fan"
    if pr and pr >= 100000:
        return "Tipo original"
    return None

def main():
    print("="*70)
    print("  B370 — DRY RUN: Normalización Calidad + Precios Tipo fan")
    print("="*70)
    products = get_all_products()
    print(f"\n  📦 Productos publicados: {len(products)}\n")

    plan_rename, plan_infer, plan_price, skipped = [], [], [], []

    for p in products:
        pid, name = p["id"], p["name"]
        cal = calidad_value(p)
        price = p.get("price") or p.get("regular_price")

        # 1) Rename Tipo jugador → Tipo original
        if cal == "Tipo jugador":
            plan_rename.append((pid, name))

        # 2) Inferencia para productos sin Calidad
        if cal is None:
            inferred = infer_line(name, price)
            if inferred:
                plan_infer.append((pid, name, price, inferred))
            else:
                skipped.append((pid, name, price))

        # 3) Precios de Tipo fan → 68.000
        current_line = "Tipo original" if cal == "Tipo jugador" else cal
        # también consideramos inferidos como Tipo fan
        if cal is None:
            inferred = infer_line(name, price)
            if inferred == "Tipo fan":
                current_line = "Tipo fan"

        if current_line == "Tipo fan":
            for v in get_variaciones(pid):
                vid = v["id"]
                vprice = v.get("regular_price") or v.get("price")
                # detectar si esta variación es Tipo fan (por atributo o por ser producto inferido)
                vcal = next((a["option"] for a in v.get("attributes", []) if a["name"] == "Calidad"), None)
                is_fan_variation = (vcal == "Tipo fan") or (cal is None and vcal is None)
                if is_fan_variation and str(vprice) != FAN_PRICE_TARGET:
                    plan_price.append((pid, name, vid, vprice, FAN_PRICE_TARGET))

    # ── REPORTE ──────────────────────────────────────
    print("─"*70)
    print(f"  🔁 RENAME  'Tipo jugador' → 'Tipo original'  ({len(plan_rename)})")
    print("─"*70)
    for pid, n in plan_rename:
        print(f"   #{pid:<5} {n}")

    print("\n" + "─"*70)
    print(f"  🧩 INFERIR atributo Calidad  ({len(plan_infer)})")
    print("─"*70)
    for pid, n, pr, line in plan_infer:
        print(f"   #{pid:<5} [{line:<14}] ${pr}  {n}")

    print("\n" + "─"*70)
    print(f"  💲 PRECIO Tipo fan → $68.000  ({len(plan_price)} variaciones)")
    print("─"*70)
    for pid, n, vid, old, new in plan_price[:80]:
        print(f"   #{pid} var#{vid}  ${old} → ${new}  ({n})")
    if len(plan_price) > 80:
        print(f"   ... y {len(plan_price)-80} más")

    print("\n" + "─"*70)
    print(f"  ⏭  SKIP (sin Calidad, no inferible)  ({len(skipped)})")
    print("─"*70)
    for pid, n, pr in skipped:
        print(f"   #{pid:<5} ${pr}  {n}")

    print("\n" + "="*70)
    print(f"  RESUMEN → rename:{len(plan_rename)}  inferir:{len(plan_infer)}  "
          f"precios:{len(plan_price)}  skip:{len(skipped)}")
    print("="*70)
    print("\n  ⚠️  DRY RUN — no se ejecutó ningún cambio.")
    print("  Revisa el plan y dame GO para correr el script de ejecución.\n")

if __name__ == "__main__":
    main()
