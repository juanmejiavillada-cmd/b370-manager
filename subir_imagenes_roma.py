"""
Subir imagenes ROMA-RETRO via SCP y asignarlas en WooCommerce
"""
import subprocess, json, os, time, requests
from dotenv import load_dotenv

load_dotenv()
WC_URL  = os.getenv('WC_URL')
WC_CK   = os.getenv('WC_CK')
WC_CS   = os.getenv('WC_CS')
SSH_HOST = os.getenv('SSH_HOST')
SSH_PORT = os.getenv('SSH_PORT')
SSH_USER = os.getenv('SSH_USER')
SSH_PASS = os.getenv('SSH_PASS')
AUTH    = (WC_CK, WC_CS)
BASE    = WC_URL + '/wp-json/wc/v3'
WP_PATH = '/home/u723505263/domains/b370sports.com/public_html'
REMOTE_DIR = '/home/u723505263/domains/b370sports.com/public_html/wp-content/uploads/b370/'
LOCAL_DIR  = r'C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\imagenes\para-subir'

IMAGES = [f'ROMA-RETRO_{i}.jpg' for i in range(1, 7)]

with open('roma_retro_ids.json') as f:
    ids = json.load(f)
PRODUCT_ID   = ids['product_id']
VARIATION_IDS = ids['variation_ids']

# ---- 1. SCP upload ----
print('=== SUBIENDO IMAGENES VIA SCP ===')
for img in IMAGES:
    local_path = os.path.join(LOCAL_DIR, img)
    cmd = [
        'scp',
        '-P', str(SSH_PORT),
        '-o', 'StrictHostKeyChecking=no',
        '-o', f'SshpassWord={SSH_PASS}',
        local_path,
        f'{SSH_USER}@{SSH_HOST}:{REMOTE_DIR}{img}'
    ]
    # Use sshpass if available, otherwise plink/pscp
    cmd_sshpass = [
        'sshpass', '-p', SSH_PASS,
        'scp', '-P', str(SSH_PORT),
        '-o', 'StrictHostKeyChecking=no',
        local_path,
        f'{SSH_USER}@{SSH_HOST}:{REMOTE_DIR}{img}'
    ]
    # Try pscp (PuTTY) which handles password
    cmd_pscp = [
        'pscp',
        '-P', str(SSH_PORT),
        '-pw', SSH_PASS,
        '-batch',
        local_path,
        f'{SSH_USER}@{SSH_HOST}:{REMOTE_DIR}{img}'
    ]
    result = subprocess.run(cmd_pscp, capture_output=True, text=True)
    if result.returncode == 0:
        print(f'  OK: {img}')
    else:
        print(f'  ERROR {img}: {result.stderr[:200]}')

# ---- 2. WP CLI import ----
print('\n=== IMPORTANDO A WP MEDIA LIBRARY ===')
wp_ids = {}
for img in IMAGES:
    remote_path = REMOTE_DIR + img
    wp_cmd = f'wp media import {remote_path} --path={WP_PATH} --porcelain --allow-root'
    ssh_import = [
        'plink',
        '-P', str(SSH_PORT),
        '-pw', SSH_PASS,
        '-batch',
        f'{SSH_USER}@{SSH_HOST}',
        wp_cmd
    ]
    result = subprocess.run(ssh_import, capture_output=True, text=True)
    out = result.stdout.strip()
    err = result.stderr.strip()
    if out.isdigit():
        wp_id = int(out)
        wp_ids[img] = wp_id
        print(f'  {img} -> WP Media ID: {wp_id}')
    else:
        # Try extracting ID from output
        lines = out.split('\n')
        found = False
        for line in lines:
            line = line.strip()
            if line.isdigit():
                wp_id = int(line)
                wp_ids[img] = wp_id
                print(f'  {img} -> WP Media ID: {wp_id}')
                found = True
                break
        if not found:
            print(f'  ERROR importando {img}: stdout={out[:200]} stderr={err[:200]}')

print('\nIDs WP Media obtenidos:', wp_ids)

# ---- 3. Asignar imagenes en WooCommerce ----
print('\n=== ASIGNANDO IMAGENES EN WOOCOMMERCE ===')

# Imagen portada (ROMA-RETRO_1.jpg) al producto padre
img1_key = 'ROMA-RETRO_1.jpg'
if img1_key in wp_ids:
    wp_main_id = wp_ids[img1_key]
    # Galeria: todas las imagenes
    gallery_ids = [wp_ids[f'ROMA-RETRO_{i}.jpg'] for i in range(2, 7) if f'ROMA-RETRO_{i}.jpg' in wp_ids]

    images_payload = [{'id': wp_main_id}]
    for gid in gallery_ids:
        images_payload.append({'id': gid})

    r = requests.post(f'{BASE}/products/{PRODUCT_ID}', json={'images': images_payload}, auth=AUTH)
    if r.status_code in (200, 201):
        print(f'  Producto {PRODUCT_ID}: portada ID={wp_main_id}, galeria={gallery_ids}')
    else:
        print(f'  ERROR asignando imagenes al producto: {r.status_code} {r.text[:200]}')

    # Asignar portada a cada variacion
    for talla, var_id in VARIATION_IDS.items():
        rv = requests.post(f'{BASE}/products/{PRODUCT_ID}/variations/{var_id}',
                           json={'image': {'id': wp_main_id}}, auth=AUTH)
        if rv.status_code in (200, 201):
            print(f'  Variacion {talla} (ID={var_id}): imagen ID={wp_main_id}')
        else:
            print(f'  ERROR variacion {talla}: {rv.status_code} {rv.text[:200]}')
else:
    print(f'  ADVERTENCIA: No se obtuvo ID WP para {img1_key}')

# Guardar resultado final
result_data = {
    'product_id': PRODUCT_ID,
    'variation_ids': VARIATION_IDS,
    'wp_image_ids': wp_ids
}
with open('roma_retro_resultado.json', 'w') as f:
    json.dump(result_data, f, indent=2)

print('\n=== RESULTADO FINAL ===')
print(f'Producto ID: {PRODUCT_ID}')
print(f'Calidad: 1.1 | Precio: $119.900')
print('Variaciones:', json.dumps(VARIATION_IDS, indent=2))
print('WP Media IDs:', json.dumps(wp_ids, indent=2))
print('Resultado guardado en roma_retro_resultado.json')
