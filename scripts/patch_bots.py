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

# Buscar líneas que contengan "bot"
print("=== Líneas con 'bot' o 'WhatsApp' en trust/wa:")
for i, line in enumerate(content.split("\n")):
    if "bot" in line.lower() or ("whatsapp" in line.lower() and "span" in line.lower()):
        print(f"  L{i}: {line.strip()[:120]}")

