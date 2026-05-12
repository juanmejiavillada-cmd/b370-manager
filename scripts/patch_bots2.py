#!/usr/bin/env python3
import os, sys, paramiko
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

HOST = os.getenv("SSH_HOST"); PORT = int(os.getenv("SSH_PORT", 22))
USER = os.getenv("SSH_USER"); PWD  = os.getenv("SSH_PASS")
MU   = f"/home/{USER}/domains/b370sports.com/public_html/wp-content/mu-plugins"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)
sftp = c.open_sftp()

with sftp.open(f"{MU}/b370-colombia-override.php", "rb") as f:
    content = f.read().decode("utf-8")

lines = content.split("\n")
print(f"L137: {lines[137]}")
print(f"L222: {lines[222]}")

# Reemplazar en L137: buscar el span de WhatsApp y quitar "Sin bots"
# El trust bar WhatsApp está en L137 condensado - reemplazar toda la línea
lines[137] = lines[137].replace(
    "<strong>Atenci&oacute;n por WhatsApp</strong><span>Persona real. Sin bots. Siempre.</span>",
    "<strong>Atenci&oacute;n por WhatsApp</strong><span>Resolvemos tus dudas antes de pedir. Siempre hay alguien del equipo.</span>"
)

# Reemplazar en L222: quitar "Sin bots"
lines[222] = lines[222].replace(
    "Tallas, colores, despachos. Te respondemos en minutos. Sin bots.",
    "Tallas, colores, despachos. Te respondemos en minutos."
)

new_content = "\n".join(lines)
ok1 = "Sin bots" not in new_content
print(f"\nBots eliminado de ambos lugares: {'OK' if ok1 else 'FALLO'}")

with sftp.open(f"{MU}/b370-colombia-override.php", "wb") as f:
    f.write(new_content.encode("utf-8"))
sftp.close()

def run(cmd):
    _, stdout, _ = c.exec_command(cmd)
    return stdout.read().decode("utf-8", errors="replace").strip()

out = run(f"php -l {MU}/b370-colombia-override.php 2>&1")
print(f"PHP: {out[:60]}")
c.close()
print("Listo. Ctrl+Shift+R.")
