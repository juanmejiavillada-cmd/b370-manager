#!/usr/bin/env python3
"""B370 — Completar los 5 productos del grupo B (Calidad + precio)."""
import os, sys, time, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
try: sys.stdout.reconfigure(encoding="utf-8")
except: pass
load_dotenv()
AUTH = HTTPBasicAuth(os.getenv("WC_CK"), os.getenv("WC_CS"))
API  = f"{os.getenv('WC_URL','https://b370sports.com')}/wp-json/wc/v3"

PLAN = {
    1368: {"calidad": "1.1",           "precio": "120000"},
    1568: {"calidad": "Tipo original", "precio": "110000"},
    1600: {"calidad": "Tipo original", "precio": "110000"},
    1609: {"calidad": "Tipo original", "precio": "110000"},
    1814: {"calidad": "1.1",           "precio": "130000"},
}

def set_calidad(pid, valor):
    r = requests.get(f"{API}/products/{pid}", auth=AUTH)
    if r.status_code != 200: return False
    attrs = r.json().get("attributes", [])
    found = False
    for a in attrs:
        if a.get("name") == "Calidad":
            a["options"] = [valor]; a["visible"] = True; found = True; break
    if not found:
        attrs.append({"name":"Calidad","options":[valor],"visible":True,"variation":False})
    r = requests.put(f"{API}/products/{pid}", auth=AUTH, json={"attributes": attrs})
    return r.status_code in (200,201)

def set_precio(pid, precio):
    # producto base
    requests.put(f"{API}/products/{pid}", auth=AUTH, json={"regular_price": precio})
    # variaciones si existen
    vars_ = requests.get(f"{API}/products/{pid}/variations", auth=AUTH, params={"per_page":100}).json()
    ok = 0
    for v in vars_ if isinstance(vars_, list) else []:
        r = requests.put(f"{API}/products/{pid}/variations/{v['id']}",
                         auth=AUTH, json={"regular_price": precio})
        if r.status_code in (200,201): ok += 1
        time.sleep(0.2)
    return ok

confirm = input("¿Ejecuto sobre PRODUCCIÓN? (SI): ").strip().upper()
if confirm != "SI":
    print("Cancelado."); raise SystemExit

for pid, cfg in PLAN.items():
    print(f"\n#{pid}  →  {cfg['calidad']}  @  ${int(cfg['precio']):,}".replace(",","."))
    print(f"   calidad: {'✅' if set_calidad(pid, cfg['calidad']) else '❌'}")
    n = set_precio(pid, cfg["precio"])
    print(f"   precio producto ✅  + {n} variaciones")
    time.sleep(0.3)

print("\n✅ Listo.")
input("ENTER para cerrar...")
