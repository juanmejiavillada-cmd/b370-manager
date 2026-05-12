#!/usr/bin/env python3
"""
B370 — Creador de variaciones por talla con SKU de Quenti v2
============================================================
Lee credenciales del .env
Ejecutar: python b370_crear_variaciones.py
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

PRODUCT_MAP = {
    670:  {"attr2_name":"Calidad","data":{"1.1":{"S":"2100000722704","M":"2100000722803","L":"2100000722902","XL":"2100000723008","XXL":"2100000723107"},"Tipo jugador":{"S":"2100000721608","M":"2100000721707","L":"2100000721806","XL":"2100000721905","XXL":"2100000722001"}}},
    686:  {"attr2_name":"Calidad","data":{"Tipo fan":{"S":"2100002004204","M":"2100002004105","L":"2100002004303","XL":"2100002021003"},"Tipo jugador":{"S":"2100000754705","M":"2100000754804","L":"2100000754903","XL":"2100000755009","XXL":"2100000755108"}}},
    691:  {"attr2_name":"Calidad","data":{"Tipo jugador":{"S":"2100000756204","M":"2100000756303","L":"2100000756402","XL":"2100000756501","XXL":"2100000756600"},"Tipo fan":{"S":"2100000921800","M":"2100000921909","L":"2100000922005","XL":"2100000922104","XXL":"2100000754865"}}},
    1251: {"attr2_name":"Calidad","data":{"1.1":{"S":"2100000723206","M":"2100000723305","L":"2100000723404","XL":"2100000723503","XXL":"2100000723602"},"Tipo jugador":{"S":"2100000727006","M":"2100000727105","L":"2100000727204","XL":"2100000727303","XXL":"2100000727402"}}},
    1368: {"attr2_name":None,"data":{None:{"S":"2100000909600","M":"2100000909709","L":"2100000909808","XL":"2100002002804","XXL":"2100000909907"}}},
    1374: {"attr2_name":"Calidad","data":{"Tipo fan":{"S":"2100001071801","M":"2100001050202","L":"2100001050301","XL":"2100001050400","XXL":"2100001050509"},"Tipo jugador":{"S":"2100001009309","M":"2100001009606","L":"2100001009705","XL":"2100001009507","XXL":"2100001009408"}}},
    1378: {"attr2_name":None,"data":{None:{"S":"2100000773706","M":"2100001067309","L":"2100001067408","XL":"2100002031002","XXL":"2100002031101"}}},
    1431: {"attr2_name":None,"data":{None:{"S":"2100000920902","M":"2100000921008","L":"2100000921107","XL":"2100000921206"}}},
    1432: {"attr2_name":None,"data":{None:{"M":"2100001015300","L":"2100000996907","XL":"2100000997003","XXL":"2100000997102"}}},
    1558: {"attr2_name":None,"data":{None:{"M":"2100002003603","L":"2100001058802","XL":"2100002003702","XXL":"2100002003801"}}},
    1566: {"attr2_name":None,"data":{None:{"S":"2100000975605","M":"2100000975704","L":"2100000975803","XL":"2100000975902","XXL":"2100000976008"}}},
    1568: {"attr2_name":None,"data":{None:{"S":"2100002040400","M":"2100002040509","L":"2100002040608","XL":"2100002040707","XXL":"2100002040806"}}},
    1582: {"attr2_name":"Calidad","data":{"Tipo jugador":{"S":"2100002008301","M":"2100002008400","L":"2100002008509","XL":"2100002008608","XXL":"2100002008707"},"Tipo fan":{"S":"2100000806206","M":"2100000806305","L":"2100000806404","XL":"2100001037500"}}},
    1600: {"attr2_name":None,"data":{None:{"S":"2100002040040","M":"2100002040059","L":"2100002040068","XL":"2100002047007","XXL":"2100002040860"}}},
    1609: {"attr2_name":None,"data":{None:{"S":"2100000752701","M":"2100000752800","L":"2100000752909","XL":"2100000753005","XXL":"2100000753104"}}},
    1737: {"attr2_name":None,"data":{None:{"S":"2100002190101","M":"2100002195801","L":"2100006570002","XL":"2100004870101","XXL":"2100003290101"}}},
    1770: {"attr2_name":"Color","data":{"Verde":{"S":"2100000715508","M":"2100000715607","L":"2100000715706","XL":"2100000715805","XXL":"2100000715904"},"Blanca":{"S":"2100000718301","M":"2100000718400","L":"2100000718509","XL":"2100000718608","XXL":"2100000718707"},"Negra":{"S":"2100001035803","M":"2100001035902","L":"2100001036008","XL":"2100001036107","XXL":"2100001036206"}}},
    1784: {"attr2_name":None,"data":{None:{"S":"2100001045703","M":"2100000714808","L":"2100000952804","XL":"2100000715003","XXL":"2100000715102"}}},
    1791: {"attr2_name":"Tipo","data":{"Verde":{"S":"2100000719902","M":"2100000720007","L":"2100000720106","XL":"2100000720205","XXL":"2100000720304"},"Blanca":{"S":"2100000719100","M":"2100000719209","L":"2100000719308","XL":"2100000719407","XXL":"2100000719506"}}},
    1803: {"attr2_name":None,"data":{None:{"S":"2100002003009","M":"2100002003108","L":"2100002003207","XL":"2100002003306","XXL":"2100002003405"}}},
    1814: {"attr2_name":None,"data":{None:{"M":"2100001047608","L":"2100001047707","XL":"2100001047806","XXL":"2100002003504"}}},
    1820: {"attr2_name":None,"data":{None:{"S":"2100001044201","M":"2100001044201","L":"2100001044201","XL":"2100001044201"}}},
    1866: {"attr2_name":None,"data":{None:{"S":"2100000957502","M":"2100000957601","L":"2100000957700","XL":"2100000957809","XXL":"2100000957908"}}},
    1868: {"attr2_name":"Tipo","data":{"Azul":{"S":"2100000770606","M":"2100000770705","L":"2100000770804","XL":"2100000770903"},"Blanca":{"S":"2100000910309","M":"2100000910200","L":"2100000771207","XL":"2100000771306"}}},
    1872: {"attr2_name":None,"data":{None:{"S":"2100002027807","M":"2100002027708","L":"2100002027609","XL":"2100000999700","XXL":"2100002027906"}}},
    1875: {"attr2_name":None,"data":{None:{"M":"2100000992701","L":"2100000992800","XL":"2100000992909","XXL":"2100000993005"}}},
    1877: {"attr2_name":None,"data":{None:{"S":"2100002013206","M":"2100002013305","L":"2100002013404","XL":"2100002013503","XXL":"2100002013602"}}},
}

def get_product(pid):
    r = requests.get(f"{API_BASE}/products/{pid}", auth=AUTH)
    return r.json() if r.status_code == 200 else {}

def update_product_attributes(pid, config):
    tallas = []
    for tipo, td in config["data"].items():
        for t in td.keys():
            if t not in tallas: tallas.append(t)
    orden = ["S","M","L","XL","XXL"]
    tallas = sorted(tallas, key=lambda x: orden.index(x) if x in orden else 99)
    attrs = [{"name":"Tallas","visible":True,"variation":True,"options":tallas}]
    if config["attr2_name"]:
        attrs.append({"name":config["attr2_name"],"visible":True,"variation":True,"options":list(config["data"].keys())})
    r = requests.put(f"{API_BASE}/products/{pid}", auth=AUTH, json={"attributes":attrs})
    return r.status_code in (200,201)

def get_existing_variations(pid):
    r = requests.get(f"{API_BASE}/products/{pid}/variations", auth=AUTH, params={"per_page":100})
    return r.json() if r.status_code == 200 else []

def delete_variation(pid, vid):
    r = requests.delete(f"{API_BASE}/products/{pid}/variations/{vid}", auth=AUTH, params={"force":True})
    return r.status_code in (200,204)

def create_variation(pid, attrs, sku, price=""):
    payload = {"attributes":attrs,"sku":sku}
    if price: payload["regular_price"] = str(price)
    r = requests.post(f"{API_BASE}/products/{pid}/variations", auth=AUTH, json=payload)
    return r.status_code in (200,201), r

def process_product(pid, config):
    print(f"\n{'─'*55}")
    print(f"🟡 Producto ID {pid}")
    product = get_product(pid)
    price = product.get("regular_price") or product.get("price") or ""
    ok_attrs = update_product_attributes(pid, config)
    print(f"   {'✅' if ok_attrs else '❌'} Atributos actualizados")
    time.sleep(0.5)
    existing = get_existing_variations(pid)
    print(f"   Eliminando {len(existing)} variaciones existentes...")
    for v in existing:
        delete_variation(pid, v["id"])
        time.sleep(0.3)
    created = errors = 0
    for tipo, tallas in config["data"].items():
        for talla, sku in tallas.items():
            attrs = [{"name":"Tallas","option":talla}]
            if config["attr2_name"] and tipo:
                attrs.append({"name":config["attr2_name"],"option":tipo})
            label = f"{tipo}/{talla}" if tipo else talla
            ok, resp = create_variation(pid, attrs, sku, price)
            new_id = resp.json().get("id","?") if ok else "?"
            print(f"   {'✅' if ok else '❌'} {label} — SKU:{sku} (ID:{new_id})")
            if ok: created += 1
            else: errors += 1
            time.sleep(0.4)
    print(f"   → {created} creadas, {errors} errores")
    return created, errors

def main():
    print("="*55)
    print("  B370 — CREAR VARIACIONES CON SKU QUENTI")
    print("="*55)
    total_ok = total_err = 0
    for pid, config in PRODUCT_MAP.items():
        try:
            c, e = process_product(pid, config)
            total_ok += c; total_err += e
        except Exception as ex:
            print(f"   ⚠️  Error producto {pid}: {ex}")
    print(f"\n  ✅ LISTO: {total_ok} variaciones creadas")
    if total_err: print(f"  ❌ Errores: {total_err}")
    input("\n  Presiona ENTER para cerrar...")

if __name__ == "__main__":
    main()
