#!/usr/bin/env python3
"""Genera los 11 archivos HTML de email para las 3 secuencias Omnisend."""
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'emails_omnisend')
os.makedirs(OUT_DIR, exist_ok=True)

def html(body_inner, cta_texto, cta_url="https://b370sports.com"):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:30px 0;">
  <tr><td align="center">
  <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:8px;overflow:hidden;">
    <tr><td style="background:#006A4E;padding:24px 32px;text-align:center;">
      <span style="color:#FFD700;font-size:26px;font-weight:900;letter-spacing:2px;">B370</span>
      <span style="color:#fff;font-size:13px;display:block;margin-top:4px;letter-spacing:1px;">LINEA DEPORTIVA</span>
    </td></tr>
    <tr><td style="padding:32px 36px;color:#333;font-size:15px;line-height:1.7;">
      {body_inner}
    </td></tr>
    <tr><td style="padding:0 36px 32px;text-align:center;">
      <a href="{cta_url}" style="display:inline-block;background:#006A4E;color:#fff;text-decoration:none;font-weight:700;font-size:15px;padding:14px 36px;border-radius:6px;">{cta_texto}</a>
    </td></tr>
    <tr><td style="background:#f9f9f9;padding:16px 32px;text-align:center;border-top:1px solid #eee;">
      <span style="font-size:12px;color:#888;">Envio a todo Colombia &nbsp;|&nbsp; Pago contra-entrega &nbsp;|&nbsp; WhatsApp: +57 321 815 9715</span>
    </td></tr>
    <tr><td style="padding:20px 32px;text-align:center;">
      <p style="font-size:11px;color:#aaa;margin:0;">B370 Linea Deportiva &middot; La Ceja, Antioquia<br>
      <a href="{{{{unsubscribe_url}}}}" style="color:#aaa;">Cancelar suscripcion</a></p>
    </td></tr>
  </table>
  </td></tr>
</table>
</body></html>"""

EMAILS = [
  # ── SECUENCIA 1: CARRITO ABANDONADO ──────────────────────────
  ("SEQ1_E1_carrito_1hora", "Completar mi pedido", "https://b370sports.com/carrito",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Vimos que estuviste mirando algo en la tienda y no terminaste el pedido. Pasa, no te preocupes.</p>
<p>Pero te decimos una cosa: <strong>tu camiseta todavia esta disponible</strong> y alguien mas la esta mirando en este momento.</p>
<p>En B370 <strong>pagas al recibir</strong>. Sin tarjeta, sin riesgo. Llega a todo Colombia en 2-5 dias habiles.</p>
<p>Dudas de talla o calidad? Escribenos por WhatsApp ahora — respondemos rapido.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  ("SEQ1_E2_carrito_24horas", "La quiero ahora", "https://b370sports.com/carrito",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Ayer te dejaste algo en el carrito. Hoy te lo volvemos a mostrar — y esta es la ultima vez que te lo recordamos.</p>
<p>No te pedimos que te apures. Solo te pedimos que <strong>no te vayas a arrepentir</strong> cuando la veas agotada.</p>
<p>✅ Pagas al recibir<br>✅ Envio a todo Colombia<br>✅ Atencion humana por WhatsApp si tienes alguna duda</p>
<p>No hay excusa para no tenerla.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  ("SEQ1_E3_carrito_72horas", "Asegurar mi talla", "https://b370sports.com/carrito",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Revisamos el stock y <strong>quedan pocas unidades en las tallas mas pedidas</strong>.</p>
<p>No inventamos urgencia — te avisamos cuando es real. Y esta vez es real.</p>
<p>Si la querias, el momento es ahora. Despues no respondemos por las tallas.</p>
<p>📦 Paga al recibir &nbsp;·&nbsp; 🇨🇴 Envio a todo Colombia &nbsp;·&nbsp; 💬 WhatsApp: +57 321 815 9715</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  # ── SECUENCIA 2: POST-COMPRA ──────────────────────────────────
  ("SEQ2_E1_postcompra_confirmacion", "Ver detalles de mi pedido", "https://b370sports.com/mi-cuenta",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Buena eleccion! Tu pedido ya esta en nuestras manos y lo estamos alistando.</p>
<p><strong>Que pasa ahora:</strong><br>
📦 Alistamos y empacamos tu pedido en La Ceja, Antioquia<br>
🚚 Lo despachamos con transportadora en las proximas horas<br>
💳 <strong>Pagas al recibir</strong> — el mensajero te cobra en la puerta</p>
<p>Tiempo estimado: <strong>2-5 dias habiles</strong> segun tu ubicacion.</p>
<p>Dudas? WhatsApp al <strong>+57 321 815 9715</strong> — estamos para lo que necesites.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  ("SEQ2_E2_postcompra_despacho", "Rastrear mi envio", "https://b370sports.com/mi-cuenta",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Buenas noticias! Tu pedido <strong>ya salio de La Ceja</strong> y esta en manos de la transportadora.</p>
<p>En los proximos dias te llegara el numero de guia para rastrear el envio.</p>
<p><strong>Recuerda:</strong> cuando llegue el mensajero, ten listo el dinero para el pago contra-entrega. Si no estas, deja a alguien de confianza.</p>
<p>Preguntas sobre el envio? Escribenos al WhatsApp y miramos el estado contigo.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  ("SEQ2_E3_postcompra_resena_d7", "Dejar mi resena en Google", "https://g.page/r/PEGAR_LINK_RESENA_AQUI",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Ya deberias tener tu camiseta en las manos. Esperamos que te haya llegado perfecta.</p>
<p>Un favor que vale oro para nosotros: <strong>dejanos tu opinion en Google</strong>. Son 30 segundos.</p>
<p>Tu resena le ayuda a otros hinchas a animarse a pedir la suya — y nos ayuda a seguir mejorando.</p>
<p><em>Si algo no estuvo bien, escribenos ANTES de publicar — lo resolvemos, en serio.</em></p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  ("SEQ2_E4_postcompra_segunda_compra_d14", "Ver novedades", "https://b370sports.com/tienda",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Esperamos que tu camiseta este dando guerra. Esta semana hay buenas novedades en la tienda:</p>
<p>🇨🇴 <strong>Colombia Local 2026</strong> — la mas pedida del momento<br>
🏆 Retros que no habiamos tenido nunca<br>
🟢 Atletico Nacional temporada nueva en stock</p>
<p>Todo con <strong>pago contra-entrega y envio a todo Colombia</strong>. Como siempre.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  # ── SECUENCIA 3: REACTIVACION ─────────────────────────────────
  ("SEQ3_E1_reactivacion_dia0", "Ver lo nuevo en B370", "https://b370sports.com/tienda",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Hace un tiempo que no sabemos de ti. Esperamos que estes bien — y que tu camiseta de B370 siga dando guerra.</p>
<p>Desde tu ultima compra llegaron cosas que te pueden interesar:<br>
🇨🇴 <strong>Colombia 2026</strong> — la camiseta del Mundial ya esta disponible<br>
🟢 <strong>Atletico Nacional</strong> — temporada nueva<br>
🕰️ <strong>Retros</strong> que no habiamos tenido nunca</p>
<p>Echales un ojo. Si ves algo que te gusta: <strong>pagas al recibir, llega a todo Colombia</strong>.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  ("SEQ3_E2_reactivacion_dia5", "Explorar novedades", "https://b370sports.com/tienda",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>El futbol no paro y B370 tampoco. Aqui un resumen de lo que llego:</p>
<p>⚽ <strong>Colombia Local 2026</strong> — tres calidades, desde $79.900<br>
🟢 <strong>Atletico Nacional</strong> Local y Tercera en stock<br>
🏆 <strong>Retros</strong> nuevos — Brasil, Argentina, Portugal y europeos<br>
🎁 <strong>Cajas regalo</strong> de futbol para el hincha que lo tiene todo</p>
<p>Todo con pago contra-entrega y envio a todo Colombia. Como siempre.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  ("SEQ3_E3_reactivacion_cupon_dia12", "Usar mi descuento", "https://b370sports.com/tienda",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Te tenemos algo especial porque ya eres parte de B370:</p>
<p style="text-align:center;margin:24px 0;">
  <span style="font-size:28px;font-weight:900;color:#006A4E;background:#e8f5e9;padding:12px 24px;border-radius:8px;display:inline-block;letter-spacing:2px;">VUELVE10</span>
</p>
<p><strong>10% de descuento</strong> en tu proximo pedido. Sin minimo de compra. Solo hasta el domingo.</p>
<p>Esa camiseta que te estabas mirando ya tiene descuento. No la dejes pasar.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),

  ("SEQ3_E4_reactivacion_adios_dia18", "Si, sigo aqui", "https://b370sports.com/tienda",
   """<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>No te vamos a mandar mas correos si no quieres. Serios.</p>
<p>Solo queremos saber: <strong>seguimos en contacto o prefieres que te saquemos de la lista?</strong></p>
<p>Si te quedas, seras el primero en enterarte de lanzamientos, descuentos y novedades.</p>
<p>Si no, tambien esta bien. Sin dramas.</p>
<p style="text-align:center;margin-top:20px;">
  <a href="{{{{unsubscribe_url}}}}" style="font-size:12px;color:#aaa;text-decoration:underline;">Prefiero que me den de baja</a>
</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasion.</p>"""),
]

for filename, cta, url, body in EMAILS:
    path = os.path.join(OUT_DIR, f"{filename}.html")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html(body, cta, url))
    print(f"  OK: {filename}.html")

print(f"\n11 archivos HTML generados en: {os.path.abspath(OUT_DIR)}")
