#!/usr/bin/env python3
"""
B370 — Asignación de imágenes por color/tipo a variaciones
Ejecutar: python b370_imagenes_variaciones.py
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

# Agregar más productos aquí con sus IDs de imagen
PRODUCT_IMAGE_MAP = {
    1770: {"attr":"Color","imagenes":{"Verde":1783,"Blanca":1776,"Negra":1812}},
    1791: {"attr":"Tipo","imagenes":{"Verde":1796,"Blanca":1792}},
    1868: {"attr":"Tipo","imagenes":{"Azul":1844}},
}

def get_variaciones(pid):
    r = requests.get(f"{API_BASE}/products/{pid}/variations", auth=AUTH, params={"per_page":100})
    return r.json() if r.status_code == 200 else []

def asignar_imagen(pid, vid, image_id):
    r = requests.put(f"{API_BASE}/products/{pid}/variations/{vid}", auth=AUTH, json={"image":{"id":image_id}})
    return r.status_code in (200,201)

def main():
    print("="*55)
    print("  B370 — ASIGNACIÓN DE IMÁGENES POR VARIACIÓN")
    print("="*55)
    total_ok = total_err = 0
    for pid, config in PRODUCT_IMAGE_MAP.items():
        print(f"\n🟡 Producto ID {pid}")
        for v in get_variaciones(pid):
            vid   = v["id"]
            talla = next((a["option"] for a in v.get("attributes",[]) if a["name"]=="Tallas"),"?")
            valor = next((a["option"] for a in v.get("attributes",[]) if a["name"]==config["attr"]),None)
            if not valor or valor not in config["imagenes"]:
                print(f"   ⏭️  Sin imagen para '{valor}' talla {talla}"); continue
            ok = asignar_imagen(pid, vid, config["imagenes"][valor])
            print(f"   {'✅' if ok else '❌'} {valor}/{talla} → imagen {config['imagenes'][valor]}")
            if ok: total_ok += 1
            else: total_err += 1
            time.sleep(0.3)
    print(f"\n  ✅ {total_ok} variaciones con imagen asignada")
    if total_err: print(f"  ❌ {total_err} errores")
    input("\n  Presiona ENTER para cerrar...")

if __name__ == "__main__":
    main()
