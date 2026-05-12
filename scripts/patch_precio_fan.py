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

original = content
content = content.replace("Tipo Fan ($79.900)", "Tipo Fan ($67.900)")

changed = content.count("$67.900")
print(f"Reemplazos realizados: {changed} — {'OK' if changed > 0 else 'FALLO'}")

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
