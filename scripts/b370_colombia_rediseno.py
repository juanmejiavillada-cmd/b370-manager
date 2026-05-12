#!/usr/bin/env python3
"""
B370 — Rediseno landing Colombia Mundial 2026
Aplica principios UI/UX Pro Max: Vibrant & Block-based + Conversion-Optimized
Tokens tricolor: #C8102E / #FFD500 / #003087 / #0D1B2A
"""
import os, sys, paramiko, io
from dotenv import load_dotenv
try: sys.stdout.reconfigure(encoding="utf-8")
except: pass
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# 1. CSS REDISEÑADO — b370-colombia.css
# ─────────────────────────────────────────────────────────────────────────────
CSS = """@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Reset & Base ── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
@media(prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important}}

.b370-col{font-family:'Inter',system-ui,sans-serif;color:#111827;line-height:1.5;-webkit-font-smoothing:antialiased}

/* ── HERO ── */
.b370-col-hero{
  background:linear-gradient(140deg,#0D1B2A 0%,#1a3a5c 45%,#8b0020 75%,#C8102E 100%);
  color:#fff;padding:80px 20px 72px;text-align:center;position:relative;overflow:hidden
}
/* Orbe decorativo amarillo — top derecha */
.b370-col-hero::before{
  content:"";position:absolute;top:-80px;right:-80px;
  width:420px;height:420px;
  background:radial-gradient(circle,rgba(255,213,0,.12) 0%,transparent 65%);
  border-radius:50%;pointer-events:none
}
/* Orbe decorativo azul — bottom izquierda */
.b370-col-hero::after{
  content:"";position:absolute;bottom:-60px;left:-60px;
  width:320px;height:320px;
  background:radial-gradient(circle,rgba(0,48,135,.25) 0%,transparent 65%);
  border-radius:50%;pointer-events:none
}
.b370-col-hero-inner{position:relative;z-index:1;max-width:680px;margin:0 auto}

/* Eyebrow badge */
.b370-col-eyebrow{
  display:inline-flex;align-items:center;gap:8px;
  background:rgba(255,213,0,.15);
  border:1px solid rgba(255,213,0,.4);
  color:#FFD500;font-size:.72rem;font-weight:700;
  letter-spacing:.18em;text-transform:uppercase;
  padding:6px 16px;border-radius:100px;margin-bottom:22px
}
.b370-col-eyebrow-dot{
  width:7px;height:7px;border-radius:50%;
  background:#FFD500;display:inline-block;
  animation:b370-pulse 2s ease-in-out infinite
}
@keyframes b370-pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.85)}}

.b370-col-hero h1{
  font-family:'Bebas Neue',Impact,sans-serif;
  font-size:clamp(3.5rem,10vw,7rem);
  line-height:.9;letter-spacing:.03em;color:#fff;margin-bottom:16px
}
.b370-col-hero h1 .acc{color:#FFD500}

/* Barra tricolor decorativa bajo el titulo */
.b370-col-tribar{
  display:flex;height:4px;width:200px;margin:0 auto 24px;border-radius:2px;overflow:hidden
}
.b370-col-tribar span:nth-child(1){flex:1;background:#FFD500}
.b370-col-tribar span:nth-child(2){flex:1;background:#C8102E}
.b370-col-tribar span:nth-child(3){flex:1;background:#003087}

.b370-col-hero-sub{
  font-size:clamp(1rem,2.5vw,1.18rem);color:rgba(255,255,255,.82);
  margin-bottom:40px;line-height:1.6
}
.b370-col-hero-sub strong{color:#fff}

/* CTA Group */
.b370-col-cta-group{display:flex;flex-direction:column;gap:12px;align-items:center}
@media(min-width:480px){.b370-col-cta-group{flex-direction:row;justify-content:center}}

.b370-col-btn-hero{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;
  background:#FFD500;color:#003087;font-weight:900;font-size:.95rem;
  padding:16px 36px;border-radius:8px;text-decoration:none;
  min-height:52px;letter-spacing:.02em;
  transition:transform .18s ease-out,box-shadow .18s ease-out,background .15s;
  cursor:pointer
}
.b370-col-btn-hero:hover{
  transform:translateY(-3px);
  box-shadow:0 12px 32px rgba(255,213,0,.45);
  background:#ffe033
}
.b370-col-btn-hero:focus-visible{outline:3px solid #FFD500;outline-offset:3px}

.b370-col-btn-hero-sec{
  display:inline-flex;align-items:center;justify-content:center;
  border:2px solid rgba(255,255,255,.4);color:#fff;font-weight:700;font-size:.9rem;
  padding:14px 28px;border-radius:8px;text-decoration:none;
  min-height:52px;
  transition:border-color .18s,background .18s;cursor:pointer
}
.b370-col-btn-hero-sec:hover{border-color:#fff;background:rgba(255,255,255,.08)}
.b370-col-btn-hero-sec:focus-visible{outline:3px solid #fff;outline-offset:3px}

/* Stats bar bajo el hero */
.b370-col-stats-bar{
  background:#0D1B2A;border-top:1px solid rgba(255,213,0,.15);
  border-bottom:1px solid rgba(255,213,0,.1);
  padding:20px;
}
.b370-col-stats-inner{
  max-width:800px;margin:0 auto;
  display:flex;flex-wrap:wrap;justify-content:center;
  gap:12px 40px
}
.b370-col-stat{text-align:center}
.b370-col-stat-n{
  font-family:'Bebas Neue',Impact,sans-serif;
  font-size:1.8rem;color:#FFD500;letter-spacing:.04em;display:block
}
.b370-col-stat-l{font-size:.72rem;color:rgba(255,255,255,.55);text-transform:uppercase;letter-spacing:.1em}

/* ── SECCIONES GENÉRICAS ── */
.b370-col-sec{padding:64px 20px;max-width:1140px;margin:0 auto}
.b370-col-secwrap-white{background:#fff}
.b370-col-secwrap-gray{background:#F8F9FA}
.b370-col-secwrap-dark{background:#0D1B2A}
.b370-col-secwrap-red{background:#C8102E}
.b370-col-secwrap-blue{background:#003087}

.b370-col-h2{
  font-family:'Bebas Neue',Impact,sans-serif;
  font-size:clamp(2rem,5.5vw,3.2rem);
  letter-spacing:.03em;color:#111827;text-align:center;margin-bottom:6px
}
.b370-col-h2.inv{color:#fff}
.b370-col-h2-sub{text-align:center;color:#4B5563;font-size:.93rem;margin-bottom:44px;line-height:1.6}
.b370-col-h2-sub.inv{color:rgba(255,255,255,.65)}

/* Divisor tricolor sobre titulos de sección */
.b370-col-divider{
  display:flex;height:3px;width:80px;margin:0 auto 18px;border-radius:2px;overflow:hidden
}
.b370-col-divider span:nth-child(1){flex:1;background:#FFD500}
.b370-col-divider span:nth-child(2){flex:1;background:#C8102E}
.b370-col-divider span:nth-child(3){flex:1;background:#003087}

/* ── PRODUCT CARDS ── */
.b370-col-grid{display:grid;grid-template-columns:1fr;gap:28px}
@media(min-width:580px){.b370-col-grid{grid-template-columns:1fr 1fr}}
@media(min-width:860px){.b370-col-grid.g3{grid-template-columns:1fr 1fr 1fr}}
@media(min-width:860px){.b370-col-grid.g4{grid-template-columns:1fr 1fr 1fr 1fr}}

.b370-col-card{
  background:#fff;border-radius:14px;overflow:hidden;
  box-shadow:0 2px 16px rgba(0,0,0,.07);
  transition:transform .22s ease-out,box-shadow .22s ease-out;
  display:flex;flex-direction:column;text-decoration:none;color:inherit;
  border:1px solid rgba(0,0,0,.05)
}
.b370-col-card:hover{
  transform:translateY(-6px);
  box-shadow:0 18px 48px rgba(0,0,0,.13)
}
.b370-col-card:focus-visible{outline:3px solid #C8102E;outline-offset:2px}

/* Imagen wrapper con aspect-ratio fijo — previene CLS */
.b370-col-iw{
  position:relative;overflow:hidden;
  background:#EAECF0;aspect-ratio:4/5
}
.b370-col-iw img{
  width:100%;height:100%;object-fit:cover;display:block;
  transition:transform .4s ease-out
}
.b370-col-card:hover .b370-col-iw img{transform:scale(1.06)}

/* Badges de producto */
.b370-col-bdg{
  position:absolute;top:12px;left:12px;
  font-size:.64rem;font-weight:800;letter-spacing:.12em;
  text-transform:uppercase;padding:5px 13px;border-radius:100px;
  background:#C8102E;color:#fff
}
.b370-col-bdg.yel{background:#FFD500;color:#003087}
.b370-col-bdg.blu{background:#003087;color:#fff}
.b370-col-bdg.ret{background:#0D1B2A;color:#FFD500}

/* Precio — chip top-right */
.b370-col-price-chip{
  position:absolute;top:12px;right:12px;
  background:rgba(13,27,42,.85);backdrop-filter:blur(4px);
  color:#FFD500;font-family:'Bebas Neue',Impact,sans-serif;
  font-size:1.1rem;letter-spacing:.04em;
  padding:4px 10px;border-radius:8px
}

/* Card body */
.b370-col-cb{
  padding:18px 18px 22px;display:flex;flex-direction:column;gap:6px;flex:1
}
.b370-col-tm{
  font-size:.72rem;font-weight:600;color:#9CA3AF;
  text-transform:uppercase;letter-spacing:.1em
}
.b370-col-cn{
  font-size:.92rem;font-weight:800;text-transform:uppercase;
  letter-spacing:.04em;color:#111827;line-height:1.2
}
.b370-col-pr{
  font-family:'Bebas Neue',Impact,sans-serif;
  font-size:1.75rem;color:#C8102E;letter-spacing:.02em;margin-top:4px
}
.b370-col-dl{font-size:.72rem;color:#9CA3AF;margin-top:-3px}

/* CTA dentro de la card */
.b370-col-cbtn{
  display:flex;align-items:center;justify-content:center;gap:7px;
  background:#C8102E;color:#fff;font-weight:700;font-size:.88rem;
  padding:13px 16px;border-radius:9px;margin-top:auto;
  min-height:44px;transition:background .15s,transform .15s;cursor:pointer
}
.b370-col-card:hover .b370-col-cbtn{background:#a30d26;transform:translateY(-1px)}

/* ── HERO PRODUCTO DESTACADO (Local) ── */
.b370-col-featured{
  background:linear-gradient(120deg,#003087 0%,#0D1B2A 100%);
  padding:64px 20px;color:#fff
}
.b370-col-featured-inner{
  max-width:1100px;margin:0 auto;
  display:grid;grid-template-columns:1fr;gap:40px;align-items:center
}
@media(min-width:768px){
  .b370-col-featured-inner{grid-template-columns:1fr 1fr}
}
.b370-col-featured-img-wrap{
  position:relative;border-radius:16px;overflow:hidden;
  aspect-ratio:4/5;max-width:400px;margin:0 auto;width:100%
}
.b370-col-featured-img-wrap img{
  width:100%;height:100%;object-fit:cover;display:block;
  transition:transform .4s ease-out
}
.b370-col-featured-img-wrap:hover img{transform:scale(1.04)}
.b370-col-featured-accent{
  position:absolute;bottom:0;left:0;right:0;
  background:linear-gradient(to top,rgba(13,27,42,.85) 0%,transparent 50%);
  padding:24px 20px 20px
}
.b370-col-featured-accent .b370-col-pr{color:#FFD500}

.b370-col-featured-text{}
.b370-col-featured-text .b370-col-eyebrow{background:rgba(255,213,0,.12)}
.b370-col-featured-h{
  font-family:'Bebas Neue',Impact,sans-serif;
  font-size:clamp(2.4rem,6vw,4rem);
  letter-spacing:.03em;line-height:.95;margin-bottom:20px;color:#fff
}
.b370-col-featured-h span{color:#FFD500}
.b370-col-featured-desc{
  font-size:.97rem;color:rgba(255,255,255,.78);
  line-height:1.7;margin-bottom:30px
}
.b370-col-featured-perks{
  display:flex;flex-direction:column;gap:12px;margin-bottom:36px
}
.b370-col-perk{
  display:flex;align-items:center;gap:12px;
  font-size:.9rem;color:rgba(255,255,255,.85)
}
.b370-col-perk-icon{
  width:36px;height:36px;border-radius:8px;
  background:rgba(255,213,0,.12);border:1px solid rgba(255,213,0,.2);
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;color:#FFD500
}

/* ── TRUST BAR ── */
.b370-col-trust-wrap{background:#0D1B2A;border-top:1px solid rgba(255,213,0,.1)}
.b370-col-trust{
  max-width:1100px;margin:0 auto;padding:56px 20px;
  display:grid;grid-template-columns:1fr;gap:28px
}
@media(min-width:640px){.b370-col-trust{grid-template-columns:1fr 1fr 1fr}}

.b370-col-ti{
  display:flex;flex-direction:column;align-items:center;
  text-align:center;gap:14px
}
@media(min-width:640px){
  .b370-col-ti{flex-direction:row;text-align:left;align-items:flex-start}
}
.b370-col-tico{
  width:50px;height:50px;
  background:rgba(255,255,255,.06);
  border:1px solid rgba(255,213,0,.2);
  border-radius:12px;display:flex;align-items:center;justify-content:center;
  flex-shrink:0;color:#FFD500
}
.b370-col-ttxt strong{
  display:block;color:#fff;font-size:.92rem;font-weight:700;margin-bottom:4px
}
.b370-col-ttxt span{font-size:.8rem;color:rgba(255,255,255,.5);line-height:1.5}

/* ── RETROS SECTION ── */
.b370-col-retro-header{
  text-align:center;margin-bottom:44px
}
/* Glassmorphism badge para retros */
.b370-col-retro-badge{
  display:inline-block;background:rgba(0,48,135,.08);
  border:1px solid rgba(0,48,135,.18);color:#003087;
  font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  padding:5px 14px;border-radius:100px;margin-bottom:14px
}

/* ── SOCIAL PROOF / URGENCY ── */
.b370-col-urgency{
  background:linear-gradient(135deg,#8b0020 0%,#C8102E 50%,#e61535 100%);
  padding:48px 20px;text-align:center;color:#fff;
  position:relative;overflow:hidden
}
.b370-col-urgency::before{
  content:"";position:absolute;top:0;left:0;right:0;bottom:0;
  background:repeating-linear-gradient(
    -45deg,
    transparent,transparent 20px,
    rgba(255,255,255,.02) 20px,rgba(255,255,255,.02) 40px
  );pointer-events:none
}
.b370-col-urgency-inner{position:relative;z-index:1}
.b370-col-urgency h3{
  font-family:'Bebas Neue',Impact,sans-serif;
  font-size:clamp(1.8rem,5vw,2.8rem);letter-spacing:.04em;margin-bottom:10px
}
.b370-col-urgency p{
  font-size:.95rem;color:rgba(255,255,255,.85);
  margin-bottom:28px;max-width:500px;margin-left:auto;margin-right:auto
}
.b370-col-btn-urgency{
  display:inline-flex;align-items:center;gap:8px;
  background:#FFD500;color:#003087;font-weight:900;font-size:1rem;
  padding:16px 40px;border-radius:8px;text-decoration:none;
  min-height:52px;transition:transform .18s,box-shadow .18s;cursor:pointer
}
.b370-col-btn-urgency:hover{
  transform:translateY(-3px);box-shadow:0 12px 32px rgba(0,0,0,.25)
}
.b370-col-btn-urgency:focus-visible{outline:3px solid #fff;outline-offset:3px}

/* ── WHATSAPP CTA ── */
.b370-col-wa{
  background:linear-gradient(135deg,#003087 0%,#001f5c 50%,#0D1B2A 100%);
  padding:72px 20px;text-align:center;color:#fff;
  position:relative;overflow:hidden
}
.b370-col-wa::before{
  content:"";position:absolute;top:-40px;left:50%;transform:translateX(-50%);
  width:600px;height:300px;
  background:radial-gradient(ellipse,rgba(37,211,102,.08) 0%,transparent 70%);
  pointer-events:none
}
.b370-col-wa-inner{position:relative;z-index:1}
.b370-col-wa h2{
  font-family:'Bebas Neue',Impact,sans-serif;
  font-size:clamp(2rem,5.5vw,3rem);letter-spacing:.03em;margin-bottom:12px
}
.b370-col-wa p{
  font-size:.97rem;color:rgba(255,255,255,.78);
  margin-bottom:36px;max-width:460px;margin-left:auto;margin-right:auto;
  line-height:1.6
}
.b370-col-btn-wa{
  display:inline-flex;align-items:center;gap:12px;
  background:#25D366;color:#fff;font-weight:800;font-size:1.05rem;
  padding:18px 40px;border-radius:8px;text-decoration:none;
  min-height:56px;transition:transform .18s,box-shadow .18s;cursor:pointer
}
.b370-col-btn-wa:hover{
  transform:translateY(-3px);box-shadow:0 14px 36px rgba(37,211,102,.35)
}
.b370-col-btn-wa:focus-visible{outline:3px solid #25D366;outline-offset:3px}

/* ── FOOTER NOTE ── */
.b370-col-fnote{
  text-align:center;padding:28px 20px;
  font-size:.8rem;color:#9CA3AF;font-style:italic;
  border-top:1px solid #F3F4F6
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# 2. HTML REDISEÑADO — contenido del wp:html block (page 3294)
# ─────────────────────────────────────────────────────────────────────────────
HTML = """<!-- wp:html -->
<div class="b370-col">

<!-- ══ HERO ══ -->
<div class="b370-col-hero">
  <div class="b370-col-hero-inner">
    <span class="b370-col-eyebrow">
      <span class="b370-col-eyebrow-dot"></span>
      Colombia al Mundial 2026
    </span>
    <h1>LA <span class="acc">TRI</span><br>COLOR</h1>
    <div class="b370-col-tribar"><span></span><span></span><span></span></div>
    <p class="b370-col-hero-sub">
      Vistete de amarillo. Siente el partido. Lleva a Colombia contigo.<br>
      <strong>Envio a todo el pais &mdash; pagas al recibirla.</strong>
    </p>
    <div class="b370-col-cta-group">
      <a href="#b370-col-productos" class="b370-col-btn-hero">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
        Ver camisetas Colombia
      </a>
      <a href="https://wa.me/573218159715?text=Hola%2C%20quiero%20info%20de%20la%20camiseta%20Colombia%202026" class="b370-col-btn-hero-sec">
        Preguntar por WhatsApp
      </a>
    </div>
  </div>
</div>

<!-- ══ STATS BAR ══ -->
<div class="b370-col-stats-bar">
  <div class="b370-col-stats-inner">
    <div class="b370-col-stat">
      <span class="b370-col-stat-n">+500</span>
      <span class="b370-col-stat-l">Pedidos entregados</span>
    </div>
    <div class="b370-col-stat">
      <span class="b370-col-stat-n">4</span>
      <span class="b370-col-stat-l">Ediciones Colombia</span>
    </div>
    <div class="b370-col-stat">
      <span class="b370-col-stat-n">S&ndash;XXL</span>
      <span class="b370-col-stat-l">Todas las tallas</span>
    </div>
    <div class="b370-col-stat">
      <span class="b370-col-stat-n">2&ndash;5</span>
      <span class="b370-col-stat-l">D&iacute;as h&aacute;biles</span>
    </div>
  </div>
</div>

<!-- ══ HERO PRODUCTO — LOCAL 2026 DESTACADA ══ -->
<div class="b370-col-featured">
  <div class="b370-col-featured-inner">
    <div class="b370-col-featured-img-wrap">
      <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4786_compressed-scaled.jpg"
           alt="Colombia Local 2026 camiseta B370 La Ceja Antioquia"
           loading="eager" width="600" height="750">
      <div class="b370-col-featured-accent">
        <span class="b370-col-pr" style="color:#FFD500;font-family:'Bebas Neue',Impact,sans-serif;font-size:1.8rem">$109.900</span>
      </div>
    </div>
    <div class="b370-col-featured-text">
      <span class="b370-col-eyebrow">
        <span class="b370-col-eyebrow-dot"></span>
        La mas pedida
      </span>
      <h2 class="b370-col-featured-h">COLOMBIA<br><span>LOCAL</span><br>2026</h2>
      <p class="b370-col-featured-desc">
        La camiseta que vas a usar cuando Colombia haga historia en el Mundial.
        Tela de alto rendimiento, corte ajustado, escudo impreso con detalle.
        La que se va a agotar primero.
      </p>
      <div class="b370-col-featured-perks">
        <div class="b370-col-perk">
          <div class="b370-col-perk-icon">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
          </div>
          <span>Calidad 1.1 &mdash; la mejor relaci&oacute;n calidad-precio del mercado</span>
        </div>
        <div class="b370-col-perk">
          <div class="b370-col-perk-icon">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
          </div>
          <span>Env&iacute;o a todo Colombia &mdash; 2 a 5 d&iacute;as h&aacute;biles</span>
        </div>
        <div class="b370-col-perk">
          <div class="b370-col-perk-icon">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
          </div>
          <span>Pagas al recibirla &mdash; cero riesgo para ti</span>
        </div>
      </div>
      <a href="https://b370sports.com/producto/colombia-local-2026/" class="b370-col-btn-hero">
        Pedir Colombia Local 2026
      </a>
    </div>
  </div>
</div>

<!-- ══ GRILLA DE PRODUCTOS ══ -->
<div id="b370-col-productos" class="b370-col-secwrap-gray">
<div class="b370-col-sec">
  <div class="b370-col-divider"><span></span><span></span><span></span></div>
  <h2 class="b370-col-h2">COLECCION COLOMBIA 2026</h2>
  <p class="b370-col-h2-sub">Las tres camisetas del Mundial. Elige la tuya. <strong>Desde $109.900</strong> &bull; Tallas S &ndash; XXL</p>

  <div class="b370-col-grid g3">

    <a href="https://b370sports.com/producto/colombia-local-2026/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4786_compressed-scaled.jpg"
             alt="Camiseta Colombia Local 2026 B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg yel">Local</span>
        <span class="b370-col-price-chip">$109.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Selecci&oacute;n Colombia</span>
        <span class="b370-col-cn">LOCAL 2026</span>
        <span class="b370-col-pr">$109.900</span>
        <span class="b370-col-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-col-cbtn">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
          Pedir esta camiseta
        </span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/colombia-visitante-2026/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4809_compressed-scaled.jpg"
             alt="Camiseta Colombia Visitante 2026 B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg blu">Visitante</span>
        <span class="b370-col-price-chip">$109.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Selecci&oacute;n Colombia</span>
        <span class="b370-col-cn">VISITANTE 2026</span>
        <span class="b370-col-pr">$109.900</span>
        <span class="b370-col-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-col-cbtn">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
          Pedir esta camiseta
        </span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/colombia-edicion-especial/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4816_compressed-scaled.jpg"
             alt="Camiseta Colombia Edici&oacute;n Especial B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg" style="background:#FFD500;color:#003087">Edici&oacute;n especial</span>
        <span class="b370-col-price-chip">$109.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Selecci&oacute;n Colombia</span>
        <span class="b370-col-cn">EDICION ESPECIAL</span>
        <span class="b370-col-pr">$109.900</span>
        <span class="b370-col-dl">Paga al recibir &bull; 2-5 d&iacute;as h&aacute;biles</span>
        <span class="b370-col-cbtn">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
          Pedir esta camiseta
        </span>
      </div>
    </a>

  </div>
</div>
</div>

<!-- ══ TRUST BAR ══ -->
<div class="b370-col-trust-wrap">
<div class="b370-col-trust">
  <div class="b370-col-ti">
    <div class="b370-col-tico">
      <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
    </div>
    <div class="b370-col-ttxt">
      <strong>Env&iacute;o a todo Colombia</strong>
      <span>Llega en 2 a 5 d&iacute;as h&aacute;biles a cualquier ciudad del pa&iacute;s</span>
    </div>
  </div>
  <div class="b370-col-ti">
    <div class="b370-col-tico">
      <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
    </div>
    <div class="b370-col-ttxt">
      <strong>Paga al recibir</strong>
      <span>Contraentrega disponible. Sin riesgo para ti, sin tarjeta requerida</span>
    </div>
  </div>
  <div class="b370-col-ti">
    <div class="b370-col-tico">
      <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
    </div>
    <div class="b370-col-ttxt">
      <strong>Atenci&oacute;n por WhatsApp</strong>
      <span>Un humano real te responde. Siempre. Sin bots</span>
    </div>
  </div>
</div>
</div>

<!-- ══ URGENCY CTA ══ -->
<div class="b370-col-urgency">
  <div class="b370-col-urgency-inner">
    <h3>COLOMBIA AL MUNDIAL.<br>LA CAMISETA YA NO PUEDE ESPERAR.</h3>
    <p>Stock limitado. Cada pedido se despacha desde La Ceja, Antioquia. Haz el tuyo hoy.</p>
    <a href="#b370-col-productos" class="b370-col-btn-urgency">
      <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      Pedir antes que se acaben
    </a>
  </div>
</div>

<!-- ══ RETROS ══ -->
<div class="b370-col-secwrap-white">
<div class="b370-col-sec">
  <div class="b370-col-retro-header">
    <span class="b370-col-retro-badge">Coleccion Retro</span>
    <div class="b370-col-divider"><span></span><span></span><span></span></div>
    <h2 class="b370-col-h2">RETROS QUE MARCARON HISTORIA</h2>
    <p class="b370-col-h2-sub">Italia 90 y La Dorada del 98. Para los que recuerdan cuando Colombia le tembl&oacute; al mundo.<br><strong>Desde $79.900</strong> &bull; Calidad Retro</p>
  </div>

  <div class="b370-col-grid g4">

    <a href="https://b370sports.com/producto/camiseta-retro-colombia-italia-90/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4786_compressed-scaled.jpg"
             alt="Colombia Retro Italia 90 Local B370" loading="lazy" width="600" height="750">
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

    <a href="https://b370sports.com/producto/camiseta-retro-colombia-italia-90-visitante/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4809_compressed-scaled.jpg"
             alt="Colombia Retro Italia 90 Visitante B370" loading="lazy" width="600" height="750">
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

    <a href="https://b370sports.com/producto/camiseta-retro-colombia-1998/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4816_compressed-scaled.jpg"
             alt="Colombia Retro 1998 Local B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg ret">Retro</span>
        <span class="b370-col-price-chip">$79.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">DORADA 98 &mdash; LOCAL</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

    <a href="https://b370sports.com/producto/camiseta-retro-colombia-1998-visitante/" class="b370-col-card">
      <div class="b370-col-iw">
        <img src="https://b370sports.com/wp-content/uploads/2026/03/DSC_4809_compressed-scaled.jpg"
             alt="Colombia Retro 1998 Visitante B370" loading="lazy" width="600" height="750">
        <span class="b370-col-bdg ret">Retro</span>
        <span class="b370-col-price-chip">$79.900</span>
      </div>
      <div class="b370-col-cb">
        <span class="b370-col-tm">Colombia Retro</span>
        <span class="b370-col-cn">DORADA 98 &mdash; VISITANTE</span>
        <span class="b370-col-pr">$79.900</span>
        <span class="b370-col-dl">Paga al recibir</span>
        <span class="b370-col-cbtn">Pedir</span>
      </div>
    </a>

  </div>
</div>
</div>

<!-- ══ WHATSAPP CTA ══ -->
<div class="b370-col-wa">
  <div class="b370-col-wa-inner">
    <h2>DUDAS? ESTAMOS<br>EN WHATSAPP</h2>
    <p>
      Tallas, colores, despachos. Te respondemos en minutos.
      Sin bots, sin formularios. Solo una persona real que ama el f&uacute;tbol.
    </p>
    <a href="https://wa.me/573218159715?text=Hola%2C%20quiero%20info%20sobre%20las%20camisetas%20Colombia%202026%20de%20B370"
       class="b370-col-btn-wa" target="_blank" rel="noopener">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
      Escribir al WhatsApp
    </a>
  </div>
</div>

<p class="b370-col-fnote">En B370, vestimos la pasi&oacute;n. &bull; La Ceja, Antioquia &bull; Env&iacute;os a todo Colombia</p>

</div>
<!-- /wp:html -->"""

# ─────────────────────────────────────────────────────────────────────────────
# 3. PHP para actualizar el post
# ─────────────────────────────────────────────────────────────────────────────
PHP_UPDATE = r"""<?php
$_SERVER['HTTP_HOST'] = 'b370sports.com';
$_SERVER['REQUEST_URI'] = '/';
define('ABSPATH', '/home/u122447978/domains/b370sports.com/public_html/');
require '/home/u122447978/domains/b370sports.com/public_html/wp-load.php';

kses_remove_filters();

$content = file_get_contents('/home/u122447978/tmp_colombia_html.html');

$result = wp_update_post([
    'ID'           => 3294,
    'post_content' => $content,
    'post_status'  => 'publish',
], true);

if (is_wp_error($result)) {
    echo 'ERROR: ' . $result->get_error_message() . "\n";
    exit(1);
}
echo 'OK: post 3294 actualizado.' . "\n";
"""

# ─────────────────────────────────────────────────────────────────────────────
# 4. CONEXION SSH Y DESPLIEGUE
# ─────────────────────────────────────────────────────────────────────────────
HOST = os.getenv("SSH_HOST")
PORT = int(os.getenv("SSH_PORT", 22))
USER = os.getenv("SSH_USER")
PWD  = os.getenv("SSH_PASS")
MU   = f"/home/{USER}/domains/b370sports.com/public_html/wp-content/mu-plugins"

print(f"Conectando a {HOST}:{PORT}...")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)
sftp = c.open_sftp()

# 4a. Subir CSS
print("Subiendo b370-colombia.css...")
css_bytes = CSS.encode("utf-8")
with sftp.open(f"{MU}/b370-colombia.css", "wb") as f:
    f.write(css_bytes)
print(f"  OK — {len(css_bytes):,} bytes")

# 4b. Subir HTML temporal
print("Subiendo HTML temporal...")
html_bytes = HTML.encode("utf-8")
with sftp.open(f"/home/{USER}/tmp_colombia_html.html", "wb") as f:
    f.write(html_bytes)
print(f"  OK — {len(html_bytes):,} bytes")

# 4c. Subir PHP de actualización
print("Subiendo PHP de actualización...")
php_bytes = PHP_UPDATE.encode("utf-8")
with sftp.open(f"/home/{USER}/tmp_colombia_update.php", "wb") as f:
    f.write(php_bytes)
sftp.close()

# 4d. Ejecutar PHP
print("Ejecutando update PHP...")
stdin, stdout, stderr = c.exec_command(f"php /home/{USER}/tmp_colombia_update.php")
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
print(f"  STDOUT: {out.strip()}")
if err: print(f"  STDERR: {err.strip()[:400]}")

# 4e. Limpiar temporales
c.exec_command(f"rm /home/{USER}/tmp_colombia_html.html /home/{USER}/tmp_colombia_update.php")

# 4f. Purgar caché LiteSpeed
print("Purgando caché LiteSpeed...")
stdin2, stdout2, stderr2 = c.exec_command(
    f"wp --path=/home/{USER}/domains/b370sports.com/public_html litespeed-purge all --allow-root 2>&1 || "
    f"php -r \"define('ABSPATH','/home/{USER}/domains/b370sports.com/public_html/'); "
    f"require '/home/{USER}/domains/b370sports.com/public_html/wp-load.php'; "
    f"do_action('litespeed_purge_all'); echo 'cache purged\n';\" 2>&1"
)
cache_out = stdout2.read().decode("utf-8", errors="replace")
print(f"  {cache_out.strip()[:200]}")

c.close()
print("\n✅ Rediseno Colombia completado.")
print("   https://b370sports.com/colombia-mundial-2026/")
