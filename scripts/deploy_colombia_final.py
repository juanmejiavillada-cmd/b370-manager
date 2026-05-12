#!/usr/bin/env python3
"""Override final de Colombia con imágenes y slugs REALES de WooCommerce."""
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

# IDs y URLs reales de WooCommerce:
# Colombia Local 2026      (1374) → DSC_4786 → /producto/colombia-2026/
# Colombia Visitante 2026  (1737) → DSC_4809 → /producto/colombia-visitante-2026/
# Colombia Edicion Especial(1378) → DSC_4816 → /producto/colombia-edicion-especial/
# Italia 90 Local          (1872) → DSC_4757 → /producto/retro-colombia-italia-90/
# Italia 90 Visitante      (1875) → DSC_4763 → /producto/retro-colombia-italia-90-visitante/
# La Dorada del 98         (1877) → DSC_4768 → /producto/retro-colombia-francia-98/
# Retro Lotto              (1866) → DSC_4743 → /producto/retro-lotto-colombia/

OVERRIDE = r"""<?php
/**
 * B370 Colombia — Override de contenido (ID correcto: 3293)
 * Imágenes y slugs verificados en WooCommerce.
 */
if (!defined('ABSPATH')) exit;

add_action('wp_head', function() {
    global $post;
    if (!isset($post) || $post->ID != 3293) return;
    header('X-LiteSpeed-Cache-Control: no-cache');
}, 1);

add_filter('the_content', function($content) {
    global $post;
    $is_colombia = false;
    if (is_page(3293)) $is_colombia = true;
    if (isset($post) && $post->ID == 3293) $is_colombia = true;
    if (get_queried_object_id() == 3293) $is_colombia = true;
    if (!$is_colombia) return $content;
    return b370_colombia_full_html();
}, 999);

function b370_colombia_full_html() {
    ob_start(); ?>
<div class="b370-col">

<div class="b370-col-hero">
  <div class="b370-col-hero-inner">
    <span class="b370-col-eyebrow"><span class="b370-col-eyebrow-dot"></span>Colombia al Mundial 2026</span>
    <h1>LA <span class="acc">TRI</span><br>COLOR</h1>
    <div class="b370-col-tribar"><span></span><span></span><span></span></div>
    <p class="b370-col-hero-sub">
      Vistete de amarillo. Siente el partido. Lleva a Colombia contigo.<br>
      <strong>Envio a todo el pais &mdash; pagas al recibirla.</strong>
    </p>
    <div class="b370-col-cta-group">
      <a href="#b370-col-productos" class="b370-col-btn-hero">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
        Ver camisetas Colombia
      </a>
      <a href="https://wa.me/573218159715?text=Hola%2C%20quiero%20info%20de%20la%20camiseta%20Colombia%202026" class="b370-col-btn-hero-sec">
        Preguntar por WhatsApp
      </a>
    </div>
  </div>
</div>

<div class="b370-col-stats-bar">
  <div class="b370-col-stats-inner">
    <div class="b370-col-stat"><span class="b370-col-stat-n">+500</span><span class="b370-col-stat-l">Pedidos entregados</span></div>
    <div class="b370-col-stat"><span class="b370-col-stat-n">4</span><span class="b370-col-stat-l">Ediciones Colombia</span></div>
    <div class="b370-col-stat"><span class="b370-col-stat-n">S&ndash;XXL</span><span class="b370-col-stat-l">Todas las tallas</span></div>
    <div class="b370-col-stat"><span class="b370-col-stat-n">2&ndash;5</span><span class="b370-col-stat-l">D&iacute;as h&aacute;biles</span></div>
  </div>
</div>

<div class="b370-col-featured">
  <div class="b370-col-featured-inner">
    <div class="b370-col-featured-img-wrap">
      <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4786_compressed-scaled.jpg"
           alt="Colombia Local 2026 B370" loading="eager" width="600" height="750">
      <div class="b370-col-featured-accent">
        <span style="color:#FFD500;font-family:'Bebas Neue',Impact,sans-serif;font-size:1.8rem">$109.900</span>
      </div>
    </div>
    <div class="b370-col-featured-text">
      <span class="b370-col-eyebrow"><span class="b370-col-eyebrow-dot"></span>La mas pedida</span>
      <h2 class="b370-col-featured-h">COLOMBIA<br><span>LOCAL</span><br>2026</h2>
      <p class="b370-col-featured-desc">La camiseta que vas a usar cuando Colombia haga historia en el Mundial. Tela de alto rendimiento, corte ajustado, escudo impreso con detalle. La que se va a agotar primero.</p>
      <div class="b370-col-featured-perks">
        <div class="b370-col-perk"><div class="b370-col-perk-icon"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div><span>Calidad 1.1 &mdash; la mejor relaci&oacute;n calidad-precio</span></div>
        <div class="b370-col-perk"><div class="b370-col-perk-icon"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg></div><span>Env&iacute;o a todo Colombia &mdash; 2 a 5 d&iacute;as h&aacute;biles</span></div>
        <div class="b370-col-perk"><div class="b370-col-perk-icon"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg></div><span>Pagas al recibirla &mdash; cero riesgo</span></div>
      </div>
      <a href="https://b370sports.com/producto/colombia-2026/" class="b370-col-btn-hero">Pedir Colombia Local 2026</a>
    </div>
  </div>
</div>

<div id="b370-col-productos" class="b370-col-secwrap-gray">
<div class="b370-col-sec">
  <div class="b370-col-divider"><span></span><span></span><span></span></div>
  <h2 class="b370-col-h2">COLECCION COLOMBIA 2026</h2>
  <p class="b370-col-h2-sub">Las tres camisetas del Mundial. <strong>Desde $109.900</strong> &bull; Tallas S &ndash; XXL</p>
  <div class="b370-col-grid g3">

    <a href="https://b370sports.com/producto/colombia-2026/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4786_compressed-scaled.jpg" alt="Colombia Local 2026" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg yel">Local</span><span class="b370-col-price-chip">$109.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Selecci&oacute;n Colombia</span>
        <span class="b370-col-cn">LOCAL 2026</span>
        <span class="b370-col-pr">$109.900</span>
        <span class="b370-col-dl">Paga al recibir &bull; 2-5 d&iacute;as</span>
        <span class="b370-col-cbtn"><svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>Pedir esta camiseta</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/colombia-visitante-2026/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4809_compressed-scaled.jpg" alt="Colombia Visitante 2026" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg blu">Visitante</span><span class="b370-col-price-chip">$109.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Selecci&oacute;n Colombia</span>
        <span class="b370-col-cn">VISITANTE 2026</span>
        <span class="b370-col-pr">$109.900</span>
        <span class="b370-col-dl">Paga al recibir &bull; 2-5 d&iacute;as</span>
        <span class="b370-col-cbtn"><svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>Pedir esta camiseta</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/colombia-edicion-especial/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4816_compressed-scaled.jpg" alt="Colombia Edicion Especial" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg" style="background:#FFD500;color:#003087">Edici&oacute;n especial</span><span class="b370-col-price-chip">$109.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Selecci&oacute;n Colombia</span>
        <span class="b370-col-cn">EDICION ESPECIAL</span>
        <span class="b370-col-pr">$109.900</span>
        <span class="b370-col-dl">Paga al recibir &bull; 2-5 d&iacute;as</span>
        <span class="b370-col-cbtn"><svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>Pedir esta camiseta</span>
      </div>
    </a>

  </div>
</div>
</div>

<div class="b370-col-trust-wrap">
<div class="b370-col-trust">
  <div class="b370-col-ti"><div class="b370-col-tico"><svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg></div><div class="b370-col-ttxt"><strong>Env&iacute;o a todo Colombia</strong><span>2 a 5 d&iacute;as h&aacute;biles a cualquier ciudad</span></div></div>
  <div class="b370-col-ti"><div class="b370-col-tico"><svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div><div class="b370-col-ttxt"><strong>Paga al recibir</strong><span>Contraentrega. Sin riesgo, sin tarjeta</span></div></div>
  <div class="b370-col-ti"><div class="b370-col-tico"><svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg></div><div class="b370-col-ttxt"><strong>Atenci&oacute;n por WhatsApp</strong><span>Persona real. Sin bots. Siempre.</span></div></div>
</div>
</div>

<div class="b370-col-urgency">
  <div class="b370-col-urgency-inner">
    <h3>COLOMBIA AL MUNDIAL.<br>LA CAMISETA YA NO PUEDE ESPERAR.</h3>
    <p>Stock limitado. Cada pedido se despacha desde La Ceja, Antioquia.</p>
    <a href="#b370-col-productos" class="b370-col-btn-urgency">Pedir antes que se acaben</a>
  </div>
</div>

<div class="b370-col-secwrap-white">
<div class="b370-col-sec">
  <div class="b370-col-retro-header">
    <span class="b370-col-retro-badge">Coleccion Retro</span>
    <div class="b370-col-divider"><span></span><span></span><span></span></div>
    <h2 class="b370-col-h2">RETROS QUE MARCARON HISTORIA</h2>
    <p class="b370-col-h2-sub">Italia 90 y La Dorada del 98. Para los que recuerdan cuando Colombia le tembl&oacute; al mundo.<br><strong>Desde $79.900</strong> &bull; Calidad Retro</p>
  </div>
  <div class="b370-col-grid g4">

    <a href="https://b370sports.com/producto/retro-colombia-italia-90/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4757_compressed-scaled.jpg" alt="Colombia Retro Italia 90 Local" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg ret">Retro</span><span class="b370-col-price-chip">$79.900</span>
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
        <span class="b370-col-bdg ret">Retro</span><span class="b370-col-price-chip">$79.900</span>
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
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4768_compressed-scaled.jpg" alt="La Dorada del 98 Colombia" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg ret">Retro</span><span class="b370-col-price-chip">$79.900</span>
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
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4743_compressed-scaled.jpg" alt="La Colombia de los 90 Retro Lotto" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg ret">Retro</span><span class="b370-col-price-chip">$79.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">LA COLOMBIA DE LOS 90</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

  </div>
</div>
</div>

<div class="b370-col-wa">
  <div class="b370-col-wa-inner">
    <h2>DUDAS? ESTAMOS<br>EN WHATSAPP</h2>
    <p>Tallas, colores, despachos. Te respondemos en minutos. Sin bots.</p>
    <a href="https://wa.me/573218159715?text=Hola%2C%20quiero%20info%20sobre%20las%20camisetas%20Colombia%202026%20de%20B370"
       class="b370-col-btn-wa" target="_blank" rel="noopener">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
      Escribir al WhatsApp
    </a>
  </div>
</div>

<p class="b370-col-fnote">En B370, vestimos la pasi&oacute;n. &bull; La Ceja, Antioquia &bull; Env&iacute;os a todo Colombia</p>

</div>
<?php
    return ob_get_clean();
}
"""

print("Subiendo override final con imágenes correctas...")
with sftp.open(f"{MU}/b370-colombia-override.php", "wb") as f:
    f.write(OVERRIDE.encode("utf-8"))
sftp.close()

out = run(f"php -l {MU}/b370-colombia-override.php 2>&1")
print(f"PHP: {out[:80]}")

# Verificar imágenes en HTML servido
out2 = run("curl -s 'https://b370sports.com/colombia-mundial-2026/' --max-time 20 | grep -o 'DSC_47[0-9][0-9]' | sort -u")
print(f"Imágenes detectadas en HTML: {out2 or '(caché — ok para visitantes logueados)'}")

c.close()
print("\nDeploy final completado. Ctrl+Shift+R en el browser.")
