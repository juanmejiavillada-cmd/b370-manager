"""
Subir imagenes ARSENAL-RETRO via paramiko SFTP, importar con WP-CLI, asignar en WooCommerce.
4 imagenes: ARSENAL-RETRO_1.jpg (portada), _2, _3, _4 (galeria)
"""
import paramiko, json, os, requests
from dotenv import load_dotenv

load_dotenv(r'C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\.env')
WC_URL   = os.getenv('WC_URL')
WC_CK    = os.getenv('WC_CK')
WC_CS    = os.getenv('WC_CS')
SSH_HOST = os.getenv('SSH_HOST')
SSH_PORT = int(os.getenv('SSH_PORT', 65002))
SSH_USER = os.getenv('SSH_USER')
SSH_PASS = os.getenv('SSH_PASS')
AUTH     = (WC_CK, WC_CS)
BASE     = WC_URL + '/wp-json/wc/v3'

WP_PATH    = '/home/u122447978/domains/b370sports.com/public_html'
REMOTE_DIR = '/home/u122447978/domains/b370sports.com/public_html/wp-content/uploads/b370/'
LOCAL_DIR  = r'C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\imagenes\para-subir'

IMAGES = [f'ARSENAL-RETRO_{i}.jpg' for i in range(1, 5)]

with open(r'C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\arsenal_retro_ids.json') as f:
    ids = json.load(f)
PRODUCT_ID    = ids['product_id']
VARIATION_IDS = ids['variation_ids']

# ---- 1. SSH connect ----
print('=== CONECTANDO POR SSH ===')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS, timeout=30)
print(f'  Conectado a {SSH_HOST}:{SSH_PORT} como {SSH_USER}')

# Asegurar que el directorio b370 exista
stdin, stdout, stderr = ssh.exec_command(f'mkdir -p {REMOTE_DIR}')
stdout.channel.recv_exit_status()

# ---- 2. SFTP upload ----
print('\n=== SUBIENDO IMAGENES VIA SFTP ===')
sftp = ssh.open_sftp()
for img in IMAGES:
    local_path = os.path.join(LOCAL_DIR, img)
    remote_path = REMOTE_DIR + img
    sftp.put(local_path, remote_path)
    print(f'  Subido: {img}')
sftp.close()
print('  Todas las imagenes subidas.')

# ---- 3. WP-CLI import ----
print('\n=== IMPORTANDO A WP MEDIA LIBRARY ===')
wp_ids = {}
for img in IMAGES:
    remote_path = REMOTE_DIR + img
    cmd = f'wp media import {remote_path} --path={WP_PATH} --porcelain --allow-root 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()

    found_id = None
    for line in out.split('\n'):
        line = line.strip()
        if line.isdigit():
            found_id = int(line)
            break

    if found_id:
        wp_ids[img] = found_id
        print(f'  {img} -> WP Media ID: {found_id}')
    else:
        print(f'  ERROR {img}:')
        if out: print(f'    stdout: {out[:300]}')
        if err: print(f'    stderr: {err[:300]}')

ssh.close()
print(f'\nWP Media IDs: {wp_ids}')

if len(wp_ids) == 0:
    print('ERROR CRITICO: No se obtuvieron IDs de WP Media. Abortando.')
    exit(1)

# ---- 4. Asignar imagenes en WooCommerce ----
print('\n=== ASIGNANDO IMAGENES EN WOOCOMMERCE ===')

img1_key = 'ARSENAL-RETRO_1.jpg'
if img1_key not in wp_ids:
    print(f'ERROR: No hay ID para imagen principal {img1_key}')
    exit(1)

wp_main_id  = wp_ids[img1_key]
gallery_ids = [wp_ids[f'ARSENAL-RETRO_{i}.jpg'] for i in range(2, 5) if f'ARSENAL-RETRO_{i}.jpg' in wp_ids]

# Portada + galeria al producto padre
images_payload = [{'id': wp_main_id}] + [{'id': gid} for gid in gallery_ids]
r = requests.post(f'{BASE}/products/{PRODUCT_ID}', json={'images': images_payload}, auth=AUTH)
if r.status_code in (200, 201):
    print(f'  Producto {PRODUCT_ID}: portada={wp_main_id}, galeria={gallery_ids}')
else:
    print(f'  ERROR producto: {r.status_code} {r.text[:300]}')

# Portada a cada variacion
for talla, var_id in VARIATION_IDS.items():
    rv = requests.post(
        f'{BASE}/products/{PRODUCT_ID}/variations/{var_id}',
        json={'image': {'id': wp_main_id}},
        auth=AUTH
    )
    if rv.status_code in (200, 201):
        print(f'  Variacion {talla} (ID={var_id}): imagen={wp_main_id}')
    else:
        print(f'  ERROR variacion {talla}: {rv.status_code} {rv.text[:200]}')

# Guardar resultado final
result_data = {
    'product_id': PRODUCT_ID,
    'variation_ids': VARIATION_IDS,
    'wp_image_ids': wp_ids
}
with open(r'C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\arsenal_retro_resultado.json', 'w') as f:
    json.dump(result_data, f, indent=2)

print('\n=== RESULTADO FINAL ===')
print(f'Producto ID: {PRODUCT_ID}')
print(f'Calidad: 1.1 | Precio: $119.900')
print('Variaciones:', json.dumps(VARIATION_IDS, indent=2))
print('WP Media IDs:', json.dumps(wp_ids, indent=2))
print('Resultado guardado en arsenal_retro_resultado.json')
