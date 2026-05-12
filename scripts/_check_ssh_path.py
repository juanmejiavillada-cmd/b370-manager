#!/usr/bin/env python3
import os, paramiko, sys
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT", 65002))
SSH_USER = os.getenv("SSH_USER")
SSH_PASS = os.getenv("SSH_PASS")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS, timeout=15)
print(f"Conectado como: {SSH_USER}")

_, out, _ = client.exec_command("echo $HOME && pwd && whoami")
print(out.read().decode())

_, out, _ = client.exec_command("ls /home/ 2>/dev/null | head -5")
print("Homes:", out.read().decode())

_, out, _ = client.exec_command("ls ~/domains/ 2>/dev/null")
print("Dominios:", out.read().decode())

client.close()
