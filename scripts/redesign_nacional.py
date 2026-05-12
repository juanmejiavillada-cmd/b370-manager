import paramiko, os

host = "195.35.15.241"
port = 65002
user = "u122447978"
password = "Operacionesb370."
wp_path = "/home/u122447978/domains/b370sports.com/public_html"

html_content = """<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&display=swap');
*,*::before,*::after{box-sizing:border-box}
.b370-nac{font-family:'Inter',system-ui,sans-serif;color:#111827;line-height:1.5}
.b370-hero{background:linear-gradient(140deg,#0D1B2A 0%,#0a3d2e 55%,#006A4E 100%);color:#fff;padding:72px 20px 64px;text-align:center;position:relative;overflow:hidden}
.b370-hero::before{content:"";position:absolute;top:-60px;right:-60px;width:380px;height:380px;background:radial-gradient(circle,rgba(255,215,0,.09) 0%,transparent 70%);border-radius:50%}
.b370-eyebrow{display:inline-block;background:#FFD700;color:#0D1B2A;font-size:.68rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;padding:4px 14px;border-radius:100px;margin-bottom:18px}
.b370-hero h1{font-family:'Bebas Neue',Impact,sans-serif;font-size:clamp(3rem,9vw,6rem);line-height:.95;letter-spacing:.02em;color:#fff;margin-bottom:12px;position:relative}
.b370-hero-sub{font-size:clamp(.95rem,2.5vw,1.15rem);color:rgba(255,255,255,.8);margin-bottom:36px;max-width:500px;margin-left:auto;margin-right:auto;position:relative}
.b370-btn-hero{display:inline-block;background:#FFD700;color:#0D1B2A;font-weight:800;font-size:.95rem;padding:15px 36px;border-radius:8px;text-decoration:none;min-height:50px;line-height:1.2;position:relative;transition:transform .15s ease-out,box-shadow .15s ease-out}
.b370-btn-hero:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(255,215,0,.35)}
.b370-sec{padding:60px 20px;max-width:1120px;margin:0 auto}
.b370-secwrap-gray{background:#F9FAFB}
.b370-secwrap-dark{background:#0D1B2A}
.b370-h2{font-family:'Bebas Neue',Impact,sans-serif;font-size:clamp(1.9rem,5vw,3rem);letter-spacing:.03em;color:#111827;text-align:center;margin-bottom:6px}
.b370-h2.inv{color:#fff}
.b370-h2-sub{text-align:center;color:#4B5563;font-size:.92rem;margin-bottom:40px}
.b370-h2-sub.inv{color:rgba(255,255,255,.6)}
.b370-grid{display:grid;grid-template-columns:1fr;gap:24px}
@media(min-width:580px){.b370-grid{grid-template-columns:1fr 1fr}}
@media(min-width:860px){.b370-grid.g3{grid-template-columns:1fr 1fr 1fr}}
.b370-card{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 14px rgba(0,0,0,.08);transition:transform .2s ease-out,box-shadow .2s ease-out;display:flex;flex-direction:column;text-decoration:none;color:inherit}
.b370-card:hover{transform:translateY(-5px);box-shadow:0 14px 36px rgba(0,0,0,.14)}
.b370-iw{position:relative;overflow:hidden;background:#F3F4F6;aspect-ratio:4/5}
.b370-iw img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .35s ease-out}
.b370-card:hover .b370-iw img{transform:scale(1.05)}
.b370-bdg{position:absolute;top:12px;left:12px;background:#006A4E;color:#fff;font-size:.65rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;padding:4px 12px;border-radius:100px}
.b370-bdg.gld{background:#FFD700;color:#0D1B2A}
.b370-cb{padding:16px 16px 20px;display:flex;flex-direction:column;gap:6px;flex:1}
.b370-tm{font-size:.73rem;font-weight:600;color:#9CA3AF;text-transform:uppercase;letter-spacing:.08em}
.b370-cn{font-size:.9rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em;color:#111827;line-height:1.2}
.b370-pr{font-family:'Bebas Neue',Impact,sans-serif;font-size:1.65rem;color:#006A4E;letter-spacing:.02em;margin-top:2px}
.b370-dl{font-size:.73rem;color:#9CA3AF;margin-top:-2px}
.b370-cbtn{display:flex;align-items:center;justify-content:center;background:#006A4E;color:#fff;font-weight:700;font-size:.88rem;padding:12px 16px;border-radius:8px;margin-top:auto;min-height:44px;transition:background .15s}
.b370-card:hover .b370-cbtn{background:#00593e}
.b370-trust{display:grid;grid-template-columns:1fr;gap:24px;text-align:center}
@media(min-width:640px){.b370-trust{grid-template-columns:1fr 1fr 1fr;text-align:left}}
.b370-ti{display:flex;flex-direction:column;align-items:center;gap:12px}
@media(min-width:640px){.b370-ti{flex-direction:row;align-items:flex-start}}
.b370-tico{width:46px;height:46px;background:rgba(255,255,255,.08);border:1px solid rgba(255,215,0,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;color:#FFD700}
.b370-ttxt strong{display:block;color:#fff;font-size:.9rem;font-weight:700;margin-bottom:3px}
.b370-ttxt span{font-size:.78rem;color:rgba(255,255,255,.55)}
.b370-wa{background:linear-gradient(135deg,#006A4E 0%,#00A86B 100%);padding:64px 20px;text-align:center;color:#fff}
.b370-wa h2{font-family:'Bebas Neue',Impact,sans-serif;font-size:clamp(1.9rem,5vw,2.8rem);letter-spacing:.03em;margin-bottom:10px}
.b370-wa p{font-size:.95rem;color:rgba(255,255,255,.82);margin-bottom:32px;max-width:440px;margin-left:auto;margin-right:auto}
.b370-btn-wa{display:inline-flex;align-items:center;gap:10px;background:#fff;color:#006A4E;font-weight:800;font-size:1rem;padding:16px 36px;border-radius:8px;text-decoration:none;min-height:52px;transition:transform .15s,box-shadow .15s}
.b370-btn-wa:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,.2)}
.b370-fnote{text-align:center;padding:24px 20px;font-size:.8rem;color:#9CA3AF;font-style:italic}
</style>

<div class="b370-nac">

<div class="b370-hero">
  <div style="position:relative;z-index:1">
    <span class="b370-eyebrow">Temporada 2026</span>
    <h1>Atl&eacute;tico Nacional</h1>
    <p class="b370-hero-sub">La colecci&oacute;n oficial del Verde Eterno.<br>Tres camisetas, un solo amor. Env&iacute;o a todo Colombia.</p>
    <a href="#b370-productos" class="b370-btn-hero">Ver camisetas 2026</a>
  </div>
</div>

<div id="b370-productos">
<div class="b370-sec">
  <h2 class="b370-h2">CAMISETAS DE TEMPORADA</h2>
  <p class="b370-h2-sub">Local y Visitante: <strong>$109.900</strong> &nbsp;&bull;&nbsp; Tercera: <strong>$119.900</strong> &nbsp;&bull;&nbsp; Tallas S &ndash; XXL</p>
  <div class="b370-grid g3">

    <a href="https://b370sports.com/producto/local-hombre-2026/" class="b370-card">
      <div class="b370-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_5011_compressed-scaled.jpg" alt="Atletico Nacional Local 2026 B370" loading="lazy" width="600" height="750">
        <span class="b370-bdg">Local</span>
      </div>
      <div class="b370-cb">
        <span class="b370-tm">Atl&eacute;tico Nacional</span>
        <span class="b370-cn">LOCAL 2026</span>
        <span class="b370-pr">$109.900</span>
        <span class="b370-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-cbtn">Pedir esta camiseta</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/visitante-2026-hombre/" class="b370-card">
      <div class="b370-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_5021_compressed-scaled.jpg" alt="Atletico Nacional Visitante 2026 B370" loading="lazy" width="600" height="750">
        <span class="b370-bdg">Visitante</span>
      </div>
      <div class="b370-cb">
        <span class="b370-tm">Atl&eacute;tico Nacional</span>
        <span class="b370-cn">VISITANTE 2026</span>
        <span class="b370-pr">$109.900</span>
        <span class="b370-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-cbtn">Pedir esta camiseta</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/tercera-hombre-2026/" class="b370-card">
      <div class="b370-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_5025_compressed-scaled.jpg" alt="Atletico Nacional Tercera 2026 B370" loading="lazy" width="600" height="750">
        <span class="b370-bdg gld">Tercera</span>
      </div>
      <div class="b370-cb">
        <span class="b370-tm">Atl&eacute;tico Nacional</span>
        <span class="b370-cn">TERCERA 2026</span>
        <span class="b370-pr">$119.900</span>
        <span class="b370-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-cbtn">Pedir esta camiseta</span>
      </div>
    </a>

  </div>
</div>
</div>

<div class="b370-secwrap-dark">
<div class="b370-sec">
  <div class="b370-trust">
    <div class="b370-ti">
      <div class="b370-tico"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg></div>
      <div class="b370-ttxt"><strong>Env&iacute;o a todo Colombia</strong><span>Llega en 2 a 5 d&iacute;as h&aacute;biles, a cualquier ciudad</span></div>
    </div>
    <div class="b370-ti">
      <div class="b370-tico"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div>
      <div class="b370-ttxt"><strong>Paga al recibir</strong><span>Contra-entrega disponible. Sin riesgo para ti</span></div>
    </div>
    <div class="b370-ti">
      <div class="b370-tico"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg></div>
      <div class="b370-ttxt"><strong>Atenci&oacute;n por WhatsApp</strong><span>Un humano real te responde siempre</span></div>
    </div>
  </div>
</div>
</div>

<div class="b370-secwrap-gray">
<div class="b370-sec">
  <h2 class="b370-h2">COMPLETA EL LOOK VERDE</h2>
  <p class="b370-h2-sub">Para los que van un paso m&aacute;s all&aacute; con el Verde Eterno</p>
  <div class="b370-grid">

    <a href="https://b370sports.com/producto/chaqueta-de-nacional-calentadora/" class="b370-card">
      <div class="b370-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/04/CHAQUETA-NACIONAL-CALENTADORA_1-1-scaled.jpg" alt="Chaqueta Nacional Calentadora B370" loading="lazy" width="600" height="750">
        <span class="b370-bdg">Calentadora</span>
      </div>
      <div class="b370-cb">
        <span class="b370-tm">Atl&eacute;tico Nacional</span>
        <span class="b370-cn">CHAQUETA CALENTADORA</span>
        <span class="b370-pr">$130.000</span>
        <span class="b370-dl">Tallas M &ndash; 3XL &bull; Gris y Negra</span>
        <span class="b370-cbtn">Ver chaqueta</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/atletico-nacional-nfl/" class="b370-card">
      <div class="b370-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4693_compressed-scaled.jpg" alt="Atletico Nacional NFL Edicion Especial B370" loading="lazy" width="600" height="750">
        <span class="b370-bdg gld">Edici&oacute;n especial</span>
      </div>
      <div class="b370-cb">
        <span class="b370-tm">Atl&eacute;tico Nacional</span>
        <span class="b370-cn">EDICI&Oacute;N ESPECIAL NFL</span>
        <span class="b370-pr">$138.000</span>
        <span class="b370-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-cbtn">Ver edici&oacute;n especial</span>
      </div>
    </a>

  </div>
</div>
</div>

<div class="b370-wa">
  <h2>&iquest;DUDAS SOBRE TALLAS O PEDIDOS?</h2>
  <p>Esc&iacute;benos. Un humano real te responde r&aacute;pido y resuelve todo antes de que pidas.</p>
  <a href="https://wa.me/573504094524?text=Hola%20B370%2C%20quiero%20pedir%20una%20camiseta%20de%20Atletico%20Nacional%202026" class="b370-btn-wa" target="_blank" rel="noopener">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12.004 2.003A9.997 9.997 0 002 12c0 1.763.463 3.417 1.27 4.855L2 22l5.282-1.243A9.953 9.953 0 0012.004 22C17.524 22 22 17.523 22 12c0-5.522-4.476-9.997-9.996-9.997zm0 18.188a8.18 8.18 0 01-4.17-1.143l-.299-.178-3.134.737.764-3.038-.195-.311A8.158 8.158 0 013.818 12c0-4.519 3.667-8.185 8.186-8.185 4.519 0 8.186 3.666 8.186 8.185 0 4.52-3.667 8.186-8.186 8.186z"/></svg>
    Pedir por WhatsApp
  </a>
</div>

<p class="b370-fnote">En B370, vestimos la pasi&oacute;n.</p>
</div>"""

php_script = """<?php
require_once('/home/u122447978/domains/b370sports.com/public_html/wp-load.php');
$html = file_get_contents('/tmp/nacional_html.txt');
$content = '<!-- wp:html -->' . $html . '<!-- /wp:html -->';
$r = wp_update_post(array(
    'ID'           => 3295,
    'post_title'   => 'Camisetas Atletico Nacional 2026 - Local, Visitante y Tercera | B370',
    'post_content' => $content,
));
echo is_wp_error($r) ? 'ERR:'.$r->get_error_message() : 'OK:'.$r;
"""

tmp_html = os.path.join(os.path.dirname(__file__), "nacional_html.txt")
tmp_php  = os.path.join(os.path.dirname(__file__), "update_nac.php")

with open(tmp_html, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(tmp_php, "w", encoding="utf-8") as f:
    f.write(php_script)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port=port, username=user, password=password)

sftp = ssh.open_sftp()
sftp.put(tmp_html, "/tmp/nacional_html.txt")
sftp.put(tmp_php, "/tmp/update_nac.php")
sftp.close()

stdin, stdout, stderr = ssh.exec_command("php /tmp/update_nac.php 2>/dev/null")
result = stdout.read().decode().strip()
print("Result:", result)

ssh.exec_command("cd /home/u122447978/domains/b370sports.com/public_html && wp litespeed-purge all 2>/dev/null")
ssh.exec_command("rm /tmp/nacional_html.txt /tmp/update_nac.php")
ssh.close()
os.remove(tmp_html)
os.remove(tmp_php)
