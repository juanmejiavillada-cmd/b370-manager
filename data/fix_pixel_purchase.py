import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko
import json
import re

SSH_HOST = "195.35.15.241"
SSH_PORT = 65002
SSH_USER = "u122447978"
SSH_PASS = "Operacionesb370."
WP_PATH = "~/domains/b370sports.com/public_html"

def ssh_exec(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS, timeout=20)
print("[SSH] Conectado OK")

# 1. Ver opciones de PixelYourSite en la base de datos
cmd_list = f"cd {WP_PATH} && wp option list --search='pys*' --fields=option_name,option_value --format=json 2>/dev/null | head -c 5000"
out, err = ssh_exec(client, cmd_list, timeout=30)
print("\n=== PYS OPTIONS (primeras) ===")
print(out[:3000] if out else f"ERROR: {err}")

# 2. Buscar la opción principal de Facebook/Meta
cmd_fb = f"cd {WP_PATH} && wp option get pys_facebook_settings --format=json 2>/dev/null"
out_fb, err_fb = ssh_exec(client, cmd_fb, timeout=30)
print("\n=== pys_facebook_settings ===")
print(out_fb[:3000] if out_fb else f"No encontrada / Error: {err_fb}")

# 3. Buscar opción de pixel ID directamente
cmd_pid = f"cd {WP_PATH} && wp option list --search='*pixel*' --fields=option_name,option_value --format=json 2>/dev/null"
out_pid, err_pid = ssh_exec(client, cmd_pid, timeout=30)
print("\n=== OPTIONS con 'pixel' ===")
print(out_pid[:2000] if out_pid else f"No encontradas / Error: {err_pid}")

# 4. Ver si PixelYourSite tiene tabla propia en la DB
cmd_tables = f"cd {WP_PATH} && wp db query \"SHOW TABLES LIKE '%pys%'\" 2>/dev/null"
out_t, err_t = ssh_exec(client, cmd_tables, timeout=30)
print("\n=== TABLAS pys* en DB ===")
print(out_t if out_t else f"Ninguna / Error: {err_t}")

# 5. Listar todos los plugins activos
cmd_plugins = f"cd {WP_PATH} && wp plugin list --status=active --fields=name,version --format=table 2>/dev/null"
out_p, err_p = ssh_exec(client, cmd_plugins, timeout=30)
print("\n=== PLUGINS ACTIVOS ===")
print(out_p[:2000] if out_p else f"Error: {err_p}")

client.close()
print("\n[SSH] Desconectado")
