import paramiko, os

host = "195.35.15.241"
port = 65002
user = "u122447978"
password = "Operacionesb370."
wp_path = "/home/u122447978/domains/b370sports.com/public_html"
mu_dir  = wp_path + "/wp-content/mu-plugins"

# ─── 1. b370-urgency.php CORREGIDO ───
urgency_plugin = r"""<?php
/**
 * Plugin Name: B370 Urgency Elements
 * Description: WhatsApp button + stock urgency + delivery strip on product pages.
 * Version: 1.2
 */
if (!defined('ABSPATH')) exit;

// ── WhatsApp button — DESPUÉS del form completo (evita quedar dentro del flex) ──
add_action('woocommerce_after_add_to_cart_form', function() {
    global $product;
    if (!$product) return;
    $msg     = rawurlencode('Hola B370, quiero pedir: ' . $product->get_name());
    $wa_link = 'https://wa.me/573218159715?text=' . $msg;
    echo '<a href="' . esc_url($wa_link) . '" target="_blank" rel="noopener" class="b370-wa-btn">'
       . '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12.004 2.003A9.997 9.997 0 002 12c0 1.763.463 3.417 1.27 4.855L2 22l5.282-1.243A9.953 9.953 0 0012.004 22C17.524 22 22 17.523 22 12c0-5.522-4.476-9.997-9.996-9.997zm0 18.188a8.18 8.18 0 01-4.17-1.143l-.299-.178-3.134.737.764-3.038-.195-.311A8.158 8.158 0 013.818 12c0-4.519 3.667-8.185 8.186-8.185 4.519 0 8.186 3.666 8.186 8.185 0 4.52-3.667 8.186-8.186 8.186z"/></svg>'
       . ' Pedir por WhatsApp'
       . '</a>';
}, 10);

// ── Delivery strip — después del form, debajo del botón WA ──
add_action('woocommerce_after_add_to_cart_form', function() {
    echo '<div class="b370-delivery-strip">'
       . '<span class="b370-ds-item"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg> Llega en 2-5 d&iacute;as</span>'
       . '<span class="b370-ds-sep">&bull;</span>'
       . '<span class="b370-ds-item"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg> Paga al recibir</span>'
       . '<span class="b370-ds-sep">&bull;</span>'
       . '<span class="b370-ds-item"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"/></svg> Envio a todo Colombia</span>'
       . '</div>';
}, 20);

// ── Stock urgency ──
add_action('woocommerce_single_product_summary', function() {
    global $product;
    if (!$product || !$product->managing_stock()) return;
    $qty = (int) $product->get_stock_quantity();
    if ($qty <= 0 || $qty > 10) return;
    if ($qty === 1)      $msg = '&iexcl;Queda solo 1! Pide ahora.';
    elseif ($qty <= 3)   $msg = '&iexcl;Solo quedan ' . $qty . '! Se agotan.';
    else                 $msg = '&iexcl;Quedan ' . $qty . ' disponibles!';
    echo '<p class="b370-stock-urgency">' . $msg . '</p>';
}, 25);

// ── CSS ──
add_action('wp_head', function() {
    if (!is_product()) return;
    ?>
<style>
.b370-wa-btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;background:#25D366;color:#fff!important;font-weight:700;font-size:1rem;padding:14px 20px;border-radius:8px;text-decoration:none!important;margin:12px 0 0;min-height:48px;transition:background .2s,transform .15s;box-sizing:border-box}
.b370-wa-btn:hover{background:#1da855;transform:translateY(-1px);color:#fff!important}
.b370-wa-btn svg{flex-shrink:0}
.b370-stock-urgency{color:#c0392b;font-weight:700;font-size:.92rem;margin:8px 0;padding:7px 12px;background:#fdf3f3;border-left:3px solid #c0392b;border-radius:4px}
.b370-delivery-strip{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;font-size:.78rem;color:#555;margin:10px 0 4px;padding:0}
.b370-ds-item{display:inline-flex;align-items:center;gap:4px;white-space:nowrap}
.b370-ds-item svg{flex-shrink:0;color:#006A4E}
.b370-ds-sep{color:#ccc;font-size:.6rem}
</style>
    <?php
});
"""

# ─── 2. CSS de Colombia (para mu-plugin b370-landing-styles.php) ───
css_colombia = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&display=swap');
*,*::before,*::after{box-sizing:border-box}
.b370-col{font-family:'Inter',system-ui,sans-serif;color:#111827;line-height:1.5}
.b370-col-hero{background:linear-gradient(140deg,#0D1B2A 0%,#1a3a5c 50%,#C8102E 100%);color:#fff;padding:72px 20px 64px;text-align:center;position:relative;overflow:hidden}
.b370-col-hero::before{content:"";position:absolute;top:-60px;right:-60px;width:380px;height:380px;background:radial-gradient(circle,rgba(255,213,0,.1) 0%,transparent 70%);border-radius:50%}
.b370-col-eyebrow{display:inline-block;background:#FFD500;color:#003087;font-size:.68rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;padding:4px 14px;border-radius:100px;margin-bottom:18px}
.b370-col-hero h1{font-family:'Bebas Neue',Impact,sans-serif;font-size:clamp(3rem,9vw,6rem);line-height:.95;letter-spacing:.02em;color:#fff;margin-bottom:12px;position:relative}
.b370-col-hero-sub{font-size:clamp(.95rem,2.5vw,1.15rem);color:rgba(255,255,255,.82);margin-bottom:36px;max-width:520px;margin-left:auto;margin-right:auto;position:relative}
.b370-col-btn-hero{display:inline-block;background:#FFD500;color:#003087;font-weight:800;font-size:.95rem;padding:15px 36px;border-radius:8px;text-decoration:none;min-height:50px;line-height:1.2;position:relative;transition:transform .15s ease-out,box-shadow .15s ease-out}
.b370-col-btn-hero:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(255,213,0,.4)}
.b370-col-sec{padding:60px 20px;max-width:1120px;margin:0 auto}
.b370-col-secwrap-gray{background:#F9FAFB}
.b370-col-secwrap-dark{background:#0D1B2A}
.b370-col-secwrap-red{background:#C8102E}
.b370-col-h2{font-family:'Bebas Neue',Impact,sans-serif;font-size:clamp(1.9rem,5vw,3rem);letter-spacing:.03em;color:#111827;text-align:center;margin-bottom:6px}
.b370-col-h2.inv{color:#fff}
.b370-col-h2-sub{text-align:center;color:#4B5563;font-size:.92rem;margin-bottom:40px}
.b370-col-h2-sub.inv{color:rgba(255,255,255,.65)}
.b370-col-grid{display:grid;grid-template-columns:1fr;gap:24px}
@media(min-width:580px){.b370-col-grid{grid-template-columns:1fr 1fr}}
@media(min-width:860px){.b370-col-grid.g3{grid-template-columns:1fr 1fr 1fr}}
@media(min-width:860px){.b370-col-grid.g4{grid-template-columns:1fr 1fr 1fr 1fr}}
.b370-col-card{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 14px rgba(0,0,0,.08);transition:transform .2s ease-out,box-shadow .2s ease-out;display:flex;flex-direction:column;text-decoration:none;color:inherit}
.b370-col-card:hover{transform:translateY(-5px);box-shadow:0 14px 36px rgba(0,0,0,.14)}
.b370-col-iw{position:relative;overflow:hidden;background:#F3F4F6;aspect-ratio:4/5}
.b370-col-iw img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .35s ease-out}
.b370-col-card:hover .b370-col-iw img{transform:scale(1.05)}
.b370-col-bdg{position:absolute;top:12px;left:12px;background:#C8102E;color:#fff;font-size:.65rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;padding:4px 12px;border-radius:100px}
.b370-col-bdg.yel{background:#FFD500;color:#003087}
.b370-col-bdg.blu{background:#003087;color:#fff}
.b370-col-cb{padding:16px 16px 20px;display:flex;flex-direction:column;gap:6px;flex:1}
.b370-col-tm{font-size:.73rem;font-weight:600;color:#9CA3AF;text-transform:uppercase;letter-spacing:.08em}
.b370-col-cn{font-size:.9rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em;color:#111827;line-height:1.2}
.b370-col-pr{font-family:'Bebas Neue',Impact,sans-serif;font-size:1.65rem;color:#C8102E;letter-spacing:.02em;margin-top:2px}
.b370-col-dl{font-size:.73rem;color:#9CA3AF;margin-top:-2px}
.b370-col-cbtn{display:flex;align-items:center;justify-content:center;background:#C8102E;color:#fff;font-weight:700;font-size:.88rem;padding:12px 16px;border-radius:8px;margin-top:auto;min-height:44px;transition:background .15s}
.b370-col-card:hover .b370-col-cbtn{background:#a30d26}
.b370-col-trust{display:grid;grid-template-columns:1fr;gap:24px;text-align:center}
@media(min-width:640px){.b370-col-trust{grid-template-columns:1fr 1fr 1fr;text-align:left}}
.b370-col-ti{display:flex;flex-direction:column;align-items:center;gap:12px}
@media(min-width:640px){.b370-col-ti{flex-direction:row;align-items:flex-start}}
.b370-col-tico{width:46px;height:46px;background:rgba(255,255,255,.08);border:1px solid rgba(255,213,0,.25);border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;color:#FFD500}
.b370-col-ttxt strong{display:block;color:#fff;font-size:.9rem;font-weight:700;margin-bottom:3px}
.b370-col-ttxt span{font-size:.78rem;color:rgba(255,255,255,.55)}
.b370-col-wa{background:linear-gradient(135deg,#003087 0%,#C8102E 100%);padding:64px 20px;text-align:center;color:#fff}
.b370-col-wa h2{font-family:'Bebas Neue',Impact,sans-serif;font-size:clamp(1.9rem,5vw,2.8rem);letter-spacing:.03em;margin-bottom:10px}
.b370-col-wa p{font-size:.95rem;color:rgba(255,255,255,.82);margin-bottom:32px;max-width:440px;margin-left:auto;margin-right:auto}
.b370-col-btn-wa{display:inline-flex;align-items:center;gap:10px;background:#25D366;color:#fff;font-weight:800;font-size:1rem;padding:16px 36px;border-radius:8px;text-decoration:none;min-height:52px;transition:transform .15s,box-shadow .15s}
.b370-col-btn-wa:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,.25)}
.b370-col-fnote{text-align:center;padding:24px 20px;font-size:.8rem;color:#9CA3AF;font-style:italic}
"""

# ─── 3. HTML limpio Colombia (page ID 3294) ───
html_colombia = """<div class="b370-col">

<div class="b370-col-hero">
  <div style="position:relative;z-index:1">
    <span class="b370-col-eyebrow">Colombia al Mundial 2026</span>
    <h1>La Tri<br>color</h1>
    <p class="b370-col-hero-sub">Vistete de amarillo. Vive el partido. Lleva a Colombia contigo.<br><strong>Envio a todo el pais &mdash; pagas al recibirla.</strong></p>
    <a href="#b370-col-productos" class="b370-col-btn-hero">Ver camisetas Colombia</a>
  </div>
</div>

<div id="b370-col-productos">
<div class="b370-col-sec">
  <h2 class="b370-col-h2">COLECCION COLOMBIA 2026</h2>
  <p class="b370-col-h2-sub">Las tres camisetas oficiales para el Mundial. <strong>Desde $109.900</strong> &bull; Tallas S &ndash; XXL</p>
  <div class="b370-col-grid g3">

    <a href="https://b370sports.com/producto/colombia-local-2026/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4786_compressed-scaled.jpg" alt="Colombia Local 2026 B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg yel">Local</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Seleccion Colombia</span>
        <span class="b370-col-cn">LOCAL 2026</span>
        <span class="b370-col-pr">$109.900</span>
        <span class="b370-col-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-col-cbtn">Pedir esta camiseta</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/colombia-visitante-2026/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4809_compressed-scaled.jpg" alt="Colombia Visitante 2026 B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg blu">Visitante</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Seleccion Colombia</span>
        <span class="b370-col-cn">VISITANTE 2026</span>
        <span class="b370-col-pr">$109.900</span>
        <span class="b370-col-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-col-cbtn">Pedir esta camiseta</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/colombia-edicion-especial/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4816_compressed-scaled.jpg" alt="Colombia Edicion Especial B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg">Edicion especial</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Seleccion Colombia</span>
        <span class="b370-col-cn">EDICION ESPECIAL</span>
        <span class="b370-col-pr">$109.900</span>
        <span class="b370-col-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-col-cbtn">Pedir esta camiseta</span>
      </div>
    </a>

  </div>
</div>
</div>

<div class="b370-col-secwrap-dark">
<div class="b370-col-sec">
  <div class="b370-col-trust">
    <div class="b370-col-ti">
      <div class="b370-col-tico"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg></div>
      <div class="b370-col-ttxt"><strong>Envio a todo Colombia</strong><span>Llega en 2 a 5 d&iacute;as h&aacute;biles a cualquier ciudad</span></div>
    </div>
    <div class="b370-col-ti">
      <div class="b370-col-tico"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div>
      <div class="b370-col-ttxt"><strong>Paga al recibir</strong><span>Contra-entrega disponible. Sin riesgo para ti</span></div>
    </div>
    <div class="b370-col-ti">
      <div class="b370-col-tico"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg></div>
      <div class="b370-col-ttxt"><strong>Atencion por WhatsApp</strong><span>Un humano real te responde siempre</span></div>
    </div>
  </div>
</div>
</div>

<div class="b370-col-secwrap-gray">
<div class="b370-col-sec">
  <h2 class="b370-col-h2">RETROS QUE MARCARON HISTORIA</h2>
  <p class="b370-col-h2-sub">Italia 90 y La Dorada del 98. Para los que recuerdan cuando Colombia temblaba al mundo. <strong>Desde $79.900</strong></p>
  <div class="b370-col-grid g4">

    <a href="https://b370sports.com/producto/camiseta-retro-colombia-italia-90/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4786_compressed-scaled.jpg" alt="Colombia Retro Italia 90 B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg yel">Retro</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">ITALIA 90 LOCAL</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/camiseta-retro-colombia-italia-90-visitante/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4809_compressed-scaled.jpg" alt="Colombia Retro Italia 90 Visitante B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg blu">Retro</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">ITALIA 90 VISITANTE</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/la-dorada-del-98-retro-colombia/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4816_compressed-scaled.jpg" alt="La Dorada del 98 Retro Colombia B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg yel">Retro</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">LA DORADA DEL 98</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/la-colombia-de-los-90-retro-lotto/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4786_compressed-scaled.jpg" alt="La Colombia de los 90 Retro Lotto B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg">Retro</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">LOS 90 RETRO LOTTO</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

  </div>
</div>
</div>

<div class="b370-col-wa">
  <h2>&iquest;DUDAS SOBRE TALLAS O PEDIDOS?</h2>
  <p>Esc&iacute;benos por WhatsApp. Un humano real te responde r&aacute;pido.</p>
  <a href="https://wa.me/573218159715?text=Hola%20B370%2C%20quiero%20pedir%20una%20camiseta%20de%20Colombia%20para%20el%20Mundial" class="b370-col-btn-wa" target="_blank" rel="noopener">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12.004 2.003A9.997 9.997 0 002 12c0 1.763.463 3.417 1.27 4.855L2 22l5.282-1.243A9.953 9.953 0 0012.004 22C17.524 22 22 17.523 22 12c0-5.522-4.476-9.997-9.996-9.997zm0 18.188a8.18 8.18 0 01-4.17-1.143l-.299-.178-3.134.737.764-3.038-.195-.311A8.158 8.158 0 013.818 12c0-4.519 3.667-8.185 8.186-8.185 4.519 0 8.186 3.666 8.186 8.185 0 4.52-3.667 8.186-8.186 8.186z"/></svg>
    Pedir por WhatsApp
  </a>
</div>

<p class="b370-col-fnote">En B370, vestimos la pasi&oacute;n.</p>
</div>"""

php_colombia = """<?php
require_once('/home/u122447978/domains/b370sports.com/public_html/wp-load.php');
kses_remove_filters();
$html = file_get_contents('/tmp/col_html.txt');
$content = '<!-- wp:html -->' . $html . '<!-- /wp:html -->';
$r = wp_update_post(array('ID'=>3294,'post_content'=>$content));
kses_init_filters();
echo is_wp_error($r) ? 'ERR:'.$r->get_error_message() : 'OK:'.$r;
"""

# Actualizar mu-plugin b370-landing-styles.php para incluir Colombia
mu_styles = """<?php
/**
 * Plugin Name: B370 Landing Page Styles
 * Description: CSS de landing pages Nacional y Colombia inyectado en <head>.
 * Version: 1.1
 */
if (!defined('ABSPATH')) exit;

add_action('wp_head', function() {
    $id = get_queried_object_id();
    if ($id === 3295) {
        echo '<style id="b370-nacional-css">' . file_get_contents(__DIR__ . '/b370-nacional.css') . '</style>';
    }
    if ($id === 3294) {
        echo '<style id="b370-colombia-css">' . file_get_contents(__DIR__ . '/b370-colombia.css') . '</style>';
    }
}, 5);
"""

# ─── Escribir archivos locales y subir ───
scripts_dir = os.path.dirname(__file__)

files = {
    "urgency.php":    (urgency_plugin, mu_dir + "/b370-urgency.php"),
    "col.css":        (css_colombia,   mu_dir + "/b370-colombia.css"),
    "mu_styles.php":  (mu_styles,      mu_dir + "/b370-landing-styles.php"),
    "col_html.txt":   (html_colombia,  "/tmp/col_html.txt"),
    "col_update.php": (php_colombia,   "/tmp/col_update.php"),
}

local_paths = {}
for fname, (content, _) in files.items():
    local = os.path.join(scripts_dir, fname)
    with open(local, "w", encoding="utf-8") as f:
        f.write(content)
    local_paths[fname] = local

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port=port, username=user, password=password)

sftp = ssh.open_sftp()
for fname, (_, remote) in files.items():
    sftp.put(local_paths[fname], remote)
    print(f"Uploaded: {fname} -> {remote.split('/')[-1]}")
sftp.close()

stdin, stdout, stderr = ssh.exec_command("php /tmp/col_update.php 2>/dev/null")
print("Colombia page:", stdout.read().decode().strip())

ssh.exec_command(f"cd {wp_path} && wp litespeed-purge all 2>/dev/null")
ssh.exec_command("rm /tmp/col_html.txt /tmp/col_update.php")
ssh.close()

for p in local_paths.values():
    os.remove(p)

print("Done")
