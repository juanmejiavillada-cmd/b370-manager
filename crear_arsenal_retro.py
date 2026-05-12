"""
Crear producto Arsenal Retro 1.1 en WooCommerce b370sports.com
Calidad: 1.1 | Precio: $119.900 | Categoria: 102 (Arsenal)
SKUs desde Quenti (CAMISETA DE ARSENAL RETRO 1,1 DE HOMBRE):
  S   -> sin SKU (no encontrado en Excel)
  M   -> 2100001030402
  L   -> 2100001030303
  XL  -> sin SKU (no encontrado en Excel)
  XXL -> 2100001030501
"""
import requests, json, os
from dotenv import load_dotenv

load_dotenv(r'C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\.env')
WC_URL = os.getenv('WC_URL')
WC_CK  = os.getenv('WC_CK')
WC_CS  = os.getenv('WC_CS')
AUTH   = (WC_CK, WC_CS)
BASE   = WC_URL + '/wp-json/wc/v3'

PRICE  = '119900'
TALLAS = ['S', 'M', 'L', 'XL', 'XXL']
SKUS   = {
    'S':   '',
    'M':   '2100001030402',
    'L':   '2100001030303',
    'XL':  '',
    'XXL': '2100001030501'
}
CAT_ID = 102

# 0. Verificar que no exista ya el producto
print('=== VERIFICANDO EXISTENCIA EN WC ===')
r_check = requests.get(
    BASE + '/products',
    params={'search': 'Arsenal Retro 1.1', 'per_page': 10},
    auth=AUTH
)
if r_check.status_code == 200:
    existing = r_check.json()
    for p in existing:
        if 'arsenal retro 1.1' in p['name'].lower():
            print(f'ADVERTENCIA: Ya existe: ID={p["id"]} | Nombre={p["name"]}')
            print('Abortando para evitar duplicado.')
            exit(1)
    print('  OK - No existe producto con ese nombre.')
else:
    print(f'  No se pudo verificar: {r_check.status_code}')

# 1. Crear producto variable
product_data = {
    'name': 'Arsenal Retro 1.1',
    'type': 'variable',
    'status': 'publish',
    'catalog_visibility': 'visible',
    'categories': [{'id': CAT_ID}],
    'attributes': [
        {
            'name': 'Tallas',
            'position': 0,
            'visible': True,
            'variation': True,
            'options': TALLAS
        },
        {
            'name': 'Calidad',
            'position': 1,
            'visible': True,
            'variation': True,
            'options': ['1.1']
        }
    ],
    'default_attributes': []
}

print('\n=== CREANDO PRODUCTO VARIABLE ===')
r = requests.post(BASE + '/products', json=product_data, auth=AUTH)
print('Status:', r.status_code)
if r.status_code not in (200, 201):
    print('ERROR:', r.text)
    exit(1)
product = r.json()
PRODUCT_ID = product['id']
print(f'Producto creado: ID={PRODUCT_ID} | Nombre={product["name"]}')

# 2. Crear variaciones
print('\n=== CREANDO VARIACIONES ===')
variation_ids = {}
for talla in TALLAS:
    var_data = {
        'status': 'publish',
        'regular_price': PRICE,
        'sku': SKUS[talla],
        'attributes': [
            {'name': 'Tallas', 'option': talla},
            {'name': 'Calidad', 'option': '1.1'}
        ],
        'manage_stock': False
    }
    rv = requests.post(f'{BASE}/products/{PRODUCT_ID}/variations', json=var_data, auth=AUTH)
    if rv.status_code in (200, 201):
        var = rv.json()
        variation_ids[talla] = var['id']
        print(f'  Variacion {talla}: ID={var["id"]} | SKU={SKUS[talla] or "(sin SKU)"} | Precio=${PRICE}')
    else:
        print(f'  ERROR {talla}: {rv.status_code} | {rv.text[:300]}')

print('\n=== RESUMEN ===')
print(f'Producto ID: {PRODUCT_ID}')
print(f'Calidad: 1.1')
print(f'Precio: ${PRICE}')
print(f'Categoria: {CAT_ID} (Arsenal)')
print('Variaciones:')
for t, vid in variation_ids.items():
    print(f'  {t}: ID={vid} | SKU={SKUS[t] or "(sin SKU)"}')

# Guardar IDs para siguiente paso
with open(r'C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\arsenal_retro_ids.json', 'w') as f:
    json.dump({'product_id': PRODUCT_ID, 'variation_ids': variation_ids, 'skus': SKUS}, f, indent=2)
print('\nIDs guardados en arsenal_retro_ids.json')
