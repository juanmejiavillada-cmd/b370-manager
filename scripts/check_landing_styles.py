#!/usr/bin/env python3
"""Verifica el mu-plugin de estilos para la página Colombia."""
import os, sys, paramiko
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

HOST = os.getenv("SSH_HOST")
PORT = int(os.getenv("SSH_PORT", 22))
USER = os.getenv("SSH_USER")
PWD  = os.getenv("SSH_PASS")
MU   = f"/home/{USER}/domains/b370sports.com/public_html/wp-content/mu-plugins"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)

def run(cmd):
    _, stdout, _ = c.exec_command(cmd)
    return stdout.read().decode("utf-8", errors="replace").strip()

# Ver qué mu-plugins existen
print("=== Mu-plugins en el servidor:")
out = run(f"ls -la {MU}/")
print(out)

print("\n=== Contenido de b370-landing-styles.php:")
out2 = run(f"cat {MU}/b370-landing-styles.php 2>/dev/null || echo '(NO EXISTE)'")
print(out2[:1500])

print("\n=== Primeras 5 lineas del override:")
out3 = run(f"head -5 {MU}/b370-colombia-override.php 2>/dev/null")
print(out3)

c.close()
