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

# 1. Quitar mención de bots en WhatsApp trust bar
content = content.replace(
    "<span>Persona real. Sin bots. Siempre.</span>",
    "<span>Resolvemos tus dudas antes de pedir. Siempre hay alguien del equipo.</span>"
)

# 2. Reemplazar el perk de calidad en la sección featured
# Antes: "Calidad 1.1 — la mejor relación calidad-precio"
# Ahora: mencionar Tipo Fan y Tipo Original
content = content.replace(
    "<span>Calidad 1.1 &mdash; la mejor relaci&oacute;n calidad-precio</span>",
    "<span>Disponible en <strong>Tipo Fan ($79.900)</strong> y <strong>Tipo Original ($109.900)</strong> &mdash; elige la que se ajuste a tu presupuesto</span>"
)

# Verificar que los cambios aplicaron
ok1 = "Sin bots" not in content
ok2 = "Tipo Fan ($79.900)" in content
print(f"1. Bots eliminado: {'OK' if ok1 else 'FALLO'}")
print(f"2. Calidades agregadas: {'OK' if ok2 else 'FALLO'}")

with sftp.open(f"{MU}/b370-colombia-override.php", "wb") as f:
    f.write(content.encode("utf-8"))
sftp.close()

def run(cmd):
    _, stdout, _ = c.exec_command(cmd)
    return stdout.read().decode("utf-8", errors="replace").strip()

out = run(f"php -l {MU}/b370-colombia-override.php 2>&1")
print(f"PHP: {out[:60]}")
c.close()
print("Listo. Ctrl+Shift+R.")
