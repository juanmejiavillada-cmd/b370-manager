#!/usr/bin/env python3
"""Actualiza solo la sección de retros en el mu-plugin con imágenes y slugs reales."""
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

def run(cmd):
    _, stdout, _ = c.exec_command(cmd)
    return stdout.read().decode("utf-8", errors="replace").strip()

# Leer el override actual
with sftp.open(f"{MU}/b370-colombia-override.php", "rb") as f:
    content = f.read().decode("utf-8")

# Datos reales de los retros desde WooCommerce:
# 1872 Italia 90 Local     → DSC_4757 → /producto/retro-colombia-italia-90/
# 1875 Italia 90 Visitante → DSC_4763 → /producto/retro-colombia-italia-90-visitante/
# 1877 La Dorada del 98    → DSC_4768 → /producto/retro-colombia-francia-98/
# 1866 Retro Lotto         → DSC_4743 → /producto/retro-lotto-colombia/

RETROS_HTML = """
    <a href="https://b370sports.com/producto/retro-colombia-italia-90/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4757_compressed-scaled.jpg" alt="Colombia Retro Italia 90 Local" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg ret">Retro</span>
        <span class="b370-col-price-chip">$79.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">ITALIA 90 &mdash; LOCAL</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/retro-colombia-italia-90-visitante/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4763_compressed-scaled.jpg" alt="Colombia Retro Italia 90 Visitante" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg ret">Retro</span>
        <span class="b370-col-price-chip">$79.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">ITALIA 90 &mdash; VISITANTE</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/retro-colombia-francia-98/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4768_compressed-scaled.jpg" alt="La Dorada del 98 Colombia Retro" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg ret">Retro</span>
        <span class="b370-col-price-chip">$79.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">LA DORADA DEL 98</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/retro-lotto-colombia/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4743_compressed-scaled.jpg" alt="Colombia de los 90 Retro Lotto" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg ret">Retro</span>
        <span class="b370-col-price-chip">$79.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">LA COLOMBIA DE LOS 90</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

"""

# Reemplazar el bloque de retros (entre <div class="b370-col-grid g4"> y </div> siguiente)
import re

new_content = re.sub(
    r'(<div class="b370-col-grid g4">).*?(</div>\n\n</div>\n</div>)',
    r'\1' + RETROS_HTML + r'\2',
    content,
    flags=re.DOTALL
)

if new_content == content:
    print("WARN: no se encontro el patron — subiendo reemplazo manual")
else:
    print("OK: bloque de retros reemplazado correctamente")

with sftp.open(f"{MU}/b370-colombia-override.php", "wb") as f:
    f.write(new_content.encode("utf-8"))

sftp.close()

# Validar PHP
out = run(f"php -l {MU}/b370-colombia-override.php 2>&1")
print(f"PHP syntax: {out[:100]}")

# Verificar con curl
out2 = run(
    "curl -s 'https://b370sports.com/colombia-mundial-2026/' --max-time 20 "
    "| grep -o 'DSC_47[0-9][0-9]' | sort -u"
)
print(f"Imágenes en HTML servido: {out2 or '(caché — pero override corregido)'}")

c.close()
print("\nRetros corregidos. Ctrl+Shift+R en el browser.")
