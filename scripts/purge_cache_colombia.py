#!/usr/bin/env python3
"""Purga el cache de LiteSpeed para la página Colombia y verifica qué se sirve."""
import os, sys, paramiko
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

HOST = os.getenv("SSH_HOST")
PORT = int(os.getenv("SSH_PORT", 22))
USER = os.getenv("SSH_USER")
PWD  = os.getenv("SSH_PASS")
WP   = f"/home/{USER}/domains/b370sports.com/public_html"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)

def run(cmd):
    _, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    return out.strip(), err.strip()

# 1. Encontrar el directorio de caché LiteSpeed
print("=== Buscando directorio de caché LiteSpeed...")
out, _ = run(f"find {WP}/wp-content/cache -maxdepth 3 -name 'colombia*' 2>/dev/null | head -20")
print(out or "(sin archivos colombia en cache)")

out2, _ = run(f"ls {WP}/wp-content/cache/ 2>/dev/null")
print("Subdirectorios de cache:", out2[:300])

# 2. Borrar cache LiteSpeed completo
print("\n=== Borrando cache LiteSpeed...")
out3, err3 = run(f"rm -rf {WP}/wp-content/cache/lscache/ 2>&1; echo 'lscache borrado'")
print(out3[:200])

# También intentar via WP-CLI con ruta completa
out4, err4 = run(f"cd {WP} && php -d error_reporting=0 wp litespeed-purge all --allow-root 2>&1 | grep -v Warning | grep -v Notice | head -5")
print("WP-CLI purge:", out4[:200])

# 3. Verificar qué sirve el servidor con curl
print("\n=== Verificando HTML servido (curl)...")
out5, _ = run("curl -s -L 'https://b370sports.com/colombia-mundial-2026/' --max-time 15 | grep -o 'b370-col[a-z-]*' | sort -u | head -30")
if out5:
    print("CLASES b370-col encontradas:", out5)
else:
    print("(ninguna clase b370-col encontrada — aun sirve HTML viejo)")

# Verificar título
out6, _ = run("curl -s -L 'https://b370sports.com/colombia-mundial-2026/' --max-time 15 | grep -o '<h1[^>]*>[^<]*</h1>' | head -3")
print("H1 en la pagina:", out6[:200] or "(no encontrado)")

c.close()
print("\nDiagnostico completado.")
