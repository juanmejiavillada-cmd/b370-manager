#!/usr/bin/env python3
"""
B370 — Actualización masiva de precios por tipo
Ejecutar: python b370_actualizar_precios.py
"""

import requests, time
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

load_dotenv()
WC_URL   = os.getenv("WC_URL", "https://b370sports.com")
CK       = os.getenv("WC_CK")
CS       = os.getenv("WC_CS")
AUTH     = HTTPBasicAuth(CK, CS)
API_BASE = f"{WC_URL}/wp-json/wc/v3"

PRODUCT_PRICES = {
    670:  {"attr":"Calidad","precios":{"1.1":"120000","Tipo jugador":"110000"}},
    686:  {"attr":"Calidad","precios":{"Tipo fan":"80000","Tipo jugador":"110000"}},
    691:  {"attr":"Calidad","precios":{"Tipo jugador":"110000","Tipo fan":"80000"}},
    1251: {"attr":"Calidad","precios":{"1.1":"120000","Tipo jugador":"110000"}},
    1368: {"attr":None,"precios":{None:"120000"}},
    1374: {"attr":"Calidad","precios":{"Tipo fan":"80000","Tipo jugador":"110000"}},
    1378: {"attr":None,"precios":{None:"120000"}},
    1431: {"attr":None,"precios":{None:"120000"}},
    1432: {"attr":None,"precios":{None:"110000"}},
    1558: {"attr":None,"precios":{None:"80000"}},
    1566: {"attr":None,"precios":{None:"90000"}},
    1568: {"attr":None,"precios":{None:"120000"}},
    1582: {"attr":"Calidad","precios":{"Tipo jugador":"120000","Tipo fan":"80000"}},
    1600: {"attr":None,"precios":{None:"120000"}},
    1609: {"attr":None,"precios":{None:"110000"}},
    1737: {"attr":None,"precios":{None:"120000"}},
    1770: {"attr":None,"precios":{None:"80000"}},
    1784: {"attr":None,"precios":{None:"80000"}},
    1791: {"attr":None,"precios":{None:"80000"}},
    1803: {"attr":None,"precios":{None:"120000"}},
    1820: {"attr":None,"precios":{None:"150000"}},
    1825: {"attr":None,"precios":{None:"95000"}},
    1866: {"attr":None,"precios":{None:"80000"}},
    1872: {"attr":None,"precios":{None:"80000"}},
    1875: {"attr":None,"precios":{None:"80000"}},
    1877: {"attr":None,"precios":{None:"80000"}},
}

def get_variaciones(pid):
    r = requests.get(f"{API_BASE}/products/{pid}/variations", auth=AUTH, params={"per_page":100})
    return r.json() if r.status_code == 200 else []

def update_precio(pid, vid, precio):
    r = requests.put(f"{API_BASE}/products/{pid}/variations/{vid}", auth=AUTH, json={"regular_price":precio})
    return r.status_code in (200,201)

def main():
    print("="*55)
    print("  B370 — ACTUALIZACIÓN MASIVA DE PRECIOS")
    print("="*55)
    total_ok = total_err = 0
    for pid, config in PRODUCT_PRICES.items():
        print(f"\n🟡 Producto ID {pid}")
        for v in get_variaciones(pid):
            vid  = v["id"]
            talla = next((a["option"] for a in v.get("attributes",[]) if a["name"]=="Tallas"),"?")
            valor = next((a["option"] for a in v.get("attributes",[]) if a["name"]==config["attr"]),"") if config["attr"] else None
            precio = config["precios"].get(valor or None)
            if not precio: continue
            ok = update_precio(pid, vid, precio)
            label = f"{valor}/{talla}" if valor else talla
            print(f"   {'✅' if ok else '❌'} {label} → ${int(precio):,}".replace(",","."))
            if ok: total_ok += 1
            else: total_err += 1
            time.sleep(0.3)
    print(f"\n  ✅ {total_ok} variaciones con precio actualizado")
    if total_err: print(f"  ❌ {total_err} errores")
    input("\n  Presiona ENTER para cerrar...")

if __name__ == "__main__":
    main()
