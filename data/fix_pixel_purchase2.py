import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko
import json

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

# Leer TODAS las filas de wp_pys_options
cmd = f"cd {WP_PATH} && wp db query \"SELECT option_name, option_value FROM wp_pys_options ORDER BY option_name\" --skip-column-names 2>/dev/null"
out, err = ssh_exec(client, cmd, timeout=30)
print("\n=== wp_pys_options (COMPLETA) ===")
print(out[:8000] if out else f"ERROR: {err}")

client.close()
print("\n[SSH] Desconectado")
