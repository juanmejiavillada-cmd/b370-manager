#!/usr/bin/env python3
"""Busca el cache de LiteSpeed y lo purga a nivel de archivos."""
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

# 1. Buscar TODOS los directorios de cache posibles
print("=== Buscando directorios de cache...")
out, _ = run(f"find /home/{USER} -name 'cache' -type d -maxdepth 6 2>/dev/null | head -20")
print("Directorios 'cache':", out or "(ninguno)")

# 2. Buscar archivos .html que sean del cache
print("\n=== Buscando archivos cache colombia...")
out2, _ = run(f"find /home/{USER} -name '*colombia*' -maxdepth 8 2>/dev/null | head -20")
print(out2 or "(ninguno)")

# 3. Buscar config LiteSpeed del plugin
print("\n=== Config LiteSpeed Cache plugin...")
out3, _ = run(f"cat {WP}/wp-content/plugins/litespeed-cache/readme.txt 2>/dev/null | head -3")
print("Plugin instalado:", "SI" if out3 else "NO")

# 4. Verificar si hay .htaccess con cache rules
print("\n=== .htaccess actual (primeras 30 lineas)...")
out4, _ = run(f"head -30 {WP}/.htaccess 2>/dev/null")
print(out4[:500])

# 5. Intentar purge via WP-CLI correctamente
print("\n=== WP-CLI purge desde directorio WP...")
out5, err5 = run(f"cd {WP} && /usr/local/bin/php -d error_reporting=0 /usr/local/bin/wp litespeed-purge all --allow-root --path={WP} 2>&1 | grep -v 'Warning\\|Notice\\|Deprecated' | head -10")
if not out5:
    out5, err5 = run(f"php80 {WP}/wp-content/plugins/litespeed-cache/bin/litespeed_helper.php purgeAll 2>&1 | head -5")
print("WP-CLI:", out5[:300] or "(sin output)")

# 6. Forzar no-cache en .htaccess para la página Colombia
print("\n=== Agregando regla cache-bypass para Colombia...")
bypass_rule = """
# B370 Colombia no-cache bypass
<IfModule LiteSpeed>
RewriteEngine On
RewriteCond %{REQUEST_URI} ^/colombia-mundial-2026
RewriteRule .* - [E=Cache-Control:no-cache]
</IfModule>
"""
out6, _ = run(f"cat {WP}/.htaccess")
if "B370 Colombia no-cache" not in out6:
    # Insertar después de la primera línea
    lines = out6.split("\n")
    lines.insert(1, bypass_rule)
    new_htaccess = "\n".join(lines)
    sftp = c.open_sftp()
    with sftp.open(f"{WP}/.htaccess", "wb") as f:
        f.write(new_htaccess.encode("utf-8"))
    sftp.close()
    print("Regla agregada al .htaccess")
else:
    print("Regla ya existe")

# 7. Verificar con curl forzando no-cache
print("\n=== Verificando HTML con no-cache...")
out7, _ = run(
    "curl -s -H 'Cache-Control: no-cache, no-store' "
    "-H 'Pragma: no-cache' "
    "-H 'X-LiteSpeed-Purge: *' "
    "'https://b370sports.com/colombia-mundial-2026/' --max-time 20 "
    "| grep -o 'b370-col-[a-z-]*' | sort -u | head -15"
)
print("Clases b370-col:", out7 or "(NINGUNA)")

# 8. Ver qué muestra EXACTLY el servidor en el body
out8, _ = run(
    "curl -s 'https://b370sports.com/colombia-mundial-2026/' --max-time 20 "
    "| grep -A2 'b370-col\\|COLOMBIA AL MUNDIAL\\|col-hero' | head -20"
)
print("\nPrimer match en HTML servido:", out8[:400] or "(nada)")

c.close()
print("\nFin del diagnostico.")
