import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, paramiko, requests
from datetime import datetime, timezone

SSH_HOST = "195.35.15.241"
SSH_PORT = 65002
SSH_USER = "u122447978"
SSH_PASS = "Operacionesb370."
WP_PATH = "~/domains/b370sports.com/public_html"

LOCAL_IMAGE = os.path.join(os.path.dirname(__file__), '..', 'data', 'images', 'PACK3-2026_1.jpg')
REMOTE_TMP = "/tmp/PACK3-2026_1.jpg"
PRODUCT_ID = 3310

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    env = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

env = load_env()
WC_URL = env['WC_URL']
WC_CK  = env['WC_CK']
WC_CS  = env['WC_CS']

print("[1] Conectando SSH...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS, timeout=20)
print("    OK")

print("[2] Subiendo imagen vía SFTP...")
sftp = client.open_sftp()
sftp.put(LOCAL_IMAGE, REMOTE_TMP)
sftp.close()
print("    OK")

print("[3] Importando a la librería de medios con WP-CLI...")
cmd = f"cd {WP_PATH} && wp media import {REMOTE_TMP} --title='Pack 3 Camisetas B370 Nacional 2026' --porcelain 2>/dev/null"
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
attachment_id = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()

if not attachment_id.isdigit():
    print(f"    ERROR WP-CLI: {err}")
    print(f"    Output: {attachment_id}")
    client.close()
    sys.exit(1)

print(f"    Attachment ID: {attachment_id}")

print("[4] Limpiando archivo temporal...")
client.exec_command(f"rm {REMOTE_TMP}")
client.close()

print("[5] Asignando imagen al producto vía WooCommerce API...")
r = requests.put(
    f"{WC_URL}/wp-json/wc/v3/products/{PRODUCT_ID}",
    auth=(WC_CK, WC_CS),
    json={"images": [{"id": int(attachment_id)}]}
)
data = r.json()

if r.status_code == 200:
    imgs = data.get('images', [])
    if imgs:
        print(f"    Imagen asignada: {imgs[0].get('src', '')}")
    print(f"\n LISTO — Producto {PRODUCT_ID} actualizado con imagen ID {attachment_id}")
else:
    print(f"    ERROR WC API: {r.status_code} — {data}")
