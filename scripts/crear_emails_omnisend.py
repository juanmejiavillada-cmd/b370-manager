#!/usr/bin/env python3
"""
Genera los 11 emails de las 3 secuencias y los sube como borradores a Omnisend.
Secuencia 1: Carrito abandonado (3 emails)
Secuencia 2: Post-compra (4 emails)
Secuencia 3: Reactivación (4 emails)
"""
import os, requests, socket, time
from dotenv import load_dotenv

load_dotenv()

OMNISEND_KEY = os.getenv("OMNISEND_API_KEY", "")
BASE = "https://api.omnisend.com/v3"
HEADERS = {"X-API-Key": OMNISEND_KEY, "Content-Type": "application/json"}

# Forzar DNS antes de cualquier request
try:
    socket.getaddrinfo("api.omnisend.com", 443)
except Exception:
    pass

# ─── Plantilla HTML base ──────────────────────────────────────────────────────
def html_email(body_inner: str, cta_texto: str, cta_url: str = "https://b370sports.com") -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>B370</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:30px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:8px;overflow:hidden;">

      <!-- HEADER -->
      <tr>
        <td style="background:#006A4E;padding:24px 32px;text-align:center;">
          <span style="color:#FFD700;font-size:26px;font-weight:900;letter-spacing:2px;">B370</span>
          <span style="color:#ffffff;font-size:13px;display:block;margin-top:4px;letter-spacing:1px;">LÍNEA DEPORTIVA</span>
        </td>
      </tr>

      <!-- BODY -->
      <tr>
        <td style="padding:32px 36px;color:#333333;font-size:15px;line-height:1.7;">
          {body_inner}
        </td>
      </tr>

      <!-- CTA -->
      <tr>
        <td style="padding:0 36px 32px;text-align:center;">
          <a href="{cta_url}"
             style="display:inline-block;background:#006A4E;color:#ffffff;text-decoration:none;
                    font-weight:700;font-size:15px;padding:14px 36px;border-radius:6px;
                    letter-spacing:0.5px;">{cta_texto}</a>
        </td>
      </tr>

      <!-- TRUST BAR -->
      <tr>
        <td style="background:#f9f9f9;padding:16px 32px;text-align:center;border-top:1px solid #eeeeee;">
          <span style="font-size:12px;color:#888888;">
            🚚 Envío a todo Colombia &nbsp;|&nbsp; 💳 Pago contra-entrega &nbsp;|&nbsp; 💬 WhatsApp: +57 321 815 9715
          </span>
        </td>
      </tr>

      <!-- FOOTER -->
      <tr>
        <td style="padding:20px 32px;text-align:center;">
          <p style="font-size:11px;color:#aaaaaa;margin:0;">
            B370 Línea Deportiva · La Ceja, Antioquia · Colombia<br>
            <a href="{{{{unsubscribe_url}}}}" style="color:#aaaaaa;">Cancelar suscripción</a>
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""

# ─── Contenido de cada email ──────────────────────────────────────────────────

EMAILS = [

  # ══ SECUENCIA 1: CARRITO ABANDONADO ══

  {
    "name": "[SEQ1-E1] Carrito Abandonado — 1 hora",
    "subject": "¿Se te quedó algo, crack? 🔥",
    "preheader": "Tu camiseta todavía te está esperando en el carrito",
    "cta": "Completar mi pedido",
    "cta_url": "https://b370sports.com/carrito",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Vimos que estuviste mirando algo en la tienda y no terminaste el pedido. Pasa, no te preocupes.</p>
<p>Pero te decimos una cosa: <strong>tu camiseta todavía está disponible</strong> — y alguien más la está mirando en este momento.</p>
<p>Recuerda: en B370 <strong>pagas al recibir</strong>. Sin tarjeta, sin riesgo. Llega a todo Colombia en 2–5 días hábiles.</p>
<p>¿Tienes dudas de talla o de calidad? Escríbenos por WhatsApp ahora mismo — respondemos rápido.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  {
    "name": "[SEQ1-E2] Carrito Abandonado — 24 horas",
    "subject": "Última vez que te lo decimos 👀",
    "preheader": "No queremos que te quedes sin ella — de verdad",
    "cta": "La quiero ahora",
    "cta_url": "https://b370sports.com/carrito",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Ayer te dejaste algo en el carrito. Hoy te lo volvemos a mostrar, y esta es la última vez que te lo recordamos.</p>
<p>No te pedimos que te apures. Solo te pedimos que <strong>no te vayas a arrepentir</strong> cuando la veas agotada.</p>
<p>✅ Pagas al recibir<br>
✅ Envío a todo Colombia<br>
✅ Atención humana por WhatsApp si tienes alguna duda</p>
<p>No hay excusa para no tenerla.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  {
    "name": "[SEQ1-E3] Carrito Abandonado — 72 horas",
    "subject": "Stock bajo en tu talla — avísate",
    "preheader": "Quedan pocas unidades. En serio, no es exageración.",
    "cta": "Asegurar mi talla",
    "cta_url": "https://b370sports.com/carrito",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Revisamos el stock y <strong>quedan pocas unidades en las tallas más pedidas</strong>.</p>
<p>No inventamos urgencia — te avisamos cuando es real. Y esta vez es real.</p>
<p>Si la querías, el momento es ahora. Después no respondemos por las tallas.</p>
<p>📦 Paga al recibir · 🇨🇴 Envío a todo Colombia · 💬 WhatsApp: +57 321 815 9715</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  # ══ SECUENCIA 2: POST-COMPRA ══

  {
    "name": "[SEQ2-E1] Post-Compra — Confirmación",
    "subject": "¡Pedido recibido! Ya lo estamos alistando 🔥",
    "preheader": "Tu camiseta empieza el viaje hoy desde La Ceja",
    "cta": "Ver detalles de mi pedido",
    "cta_url": "https://b370sports.com/mi-cuenta",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>¡Buena elección! Tu pedido ya está en nuestras manos y lo estamos alistando.</p>
<p><strong>¿Qué pasa ahora?</strong><br>
📦 Alistamos y empacamos tu pedido en La Ceja, Antioquia<br>
🚚 Lo despachamos con transportadora en las próximas horas<br>
💳 Recuerdas: <strong>pagas al recibir</strong> — el mensajero te cobra en la puerta</p>
<p>Tiempo estimado de entrega: <strong>2–5 días hábiles</strong> según tu ubicación.</p>
<p>¿Alguna duda? Escríbenos por WhatsApp al <strong>+57 321 815 9715</strong> — estamos para lo que necesites.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  {
    "name": "[SEQ2-E2] Post-Compra — Despacho",
    "subject": "Tu camiseta salió de La Ceja ⚽",
    "preheader": "Ya va en camino, crack. Prepárate para recibirla.",
    "cta": "Rastrear mi envío",
    "cta_url": "https://b370sports.com/mi-cuenta",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>¡Buenas noticias! Tu pedido <strong>ya salió de La Ceja</strong> y está en manos de la transportadora.</p>
<p>En los próximos días te llegará el número de guía para rastrear el envío.</p>
<p><strong>Recuerda:</strong> cuando llegue el mensajero, tienes que tener el dinero listo para el pago contra-entrega. Si no estás, deja a alguien de confianza.</p>
<p>¿Preguntas sobre el envío? Escríbenos al WhatsApp y miramos el estado contigo.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  {
    "name": "[SEQ2-E3] Post-Compra — Solicitud de reseña (D+7)",
    "subject": "¿Cómo te quedó? Cuéntanos 🏆",
    "preheader": "30 segundos y nos ayudas un montón — de verdad",
    "cta": "Dejar mi reseña en Google",
    "cta_url": "https://g.page/r/PLACEHOLDER_GOOGLE_REVIEW",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Ya deberías tener tu camiseta en las manos. Esperamos que te haya llegado perfecta y te esté quedando increíble.</p>
<p>Un favor que vale oro para nosotros:<br>
¿Nos dejas tu opinión en Google? Son <strong>30 segundos</strong>.</p>
<p>Tu reseña le ayuda a otros hinchas a animarse a pedir la suya con confianza — y nos ayuda a seguir mejorando.</p>
<p><em>Si algo no estuvo bien, escríbenos ANTES de publicar — lo resolvemos, en serio. Tu experiencia importa.</em></p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  {
    "name": "[SEQ2-E4] Post-Compra — Segunda compra (D+14)",
    "subject": "¿Ya tienes la próxima en mente?",
    "preheader": "Mira lo que llegó nuevo esta semana a la tienda",
    "cta": "Ver novedades",
    "cta_url": "https://b370sports.com/tienda",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Esperamos que tu camiseta esté dando guerra. Los hinchas B370 siempre vuelven por más — y esta semana hay buenas novedades en la tienda.</p>
<p>🆕 Nuevas referencias disponibles<br>
⚽ Colombia local 2026 — la más pedida del momento<br>
🏆 Retros que no habíamos tenido nunca</p>
<p>Como ya eres parte de B370, tienes acceso a todo el catálogo con <strong>pago contra-entrega y envío a todo Colombia</strong>.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  # ══ SECUENCIA 3: REACTIVACIÓN ══

  {
    "name": "[SEQ3-E1] Reactivación — Check-in (Día 0)",
    "subject": "Te extrañamos, {{contact.firstName | default: 'crack'}} ⚽",
    "preheader": "Han pasado unos meses. ¿Todo bien por allá?",
    "cta": "Ver lo nuevo en B370",
    "cta_url": "https://b370sports.com/tienda",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Hace un tiempo que no sabemos de ti. Esperamos que estés bien — y que tu camiseta de B370 siga dando guerra en los partidos.</p>
<p>Desde tu última compra llegaron cosas que te pueden interesar:</p>
<p>🇨🇴 <strong>Selección Colombia 2026</strong> — la camiseta del Mundial ya está disponible<br>
🟢 <strong>Atlético Nacional</strong> — temporada nueva, camiseta nueva<br>
🕰️ <strong>Retros</strong> que no habíamos tenido nunca en el catálogo</p>
<p>Échales un ojo. Y si ves algo que te gusta, ya sabes: <strong>pagas al recibir, llega a todo Colombia</strong>.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  {
    "name": "[SEQ3-E2] Reactivación — Novedades (Día 5)",
    "subject": "Esto llegó mientras no estabas 👀",
    "preheader": "Colombia al Mundial, Nacional nueva temporada y más retros",
    "cta": "Explorar novedades",
    "cta_url": "https://b370sports.com/tienda",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>El fútbol no paró y B370 tampoco. Aquí un resumen rápido de lo que llegó:</p>
<p>⚽ <strong>Colombia Local 2026</strong> — la más vendida de la tienda. Tres calidades, desde $79.900<br>
🟢 <strong>Atlético Nacional Local y Tercera</strong> — temporada actual en stock<br>
🏆 <strong>Retros nuevos</strong> — Brasil, Argentina, Portugal y más europeos<br>
🎁 <strong>Cajas regalo de fútbol</strong> — para el hincha que lo tiene todo</p>
<p>Todo con <strong>pago contra-entrega y envío a todo Colombia</strong>. Como siempre.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  {
    "name": "[SEQ3-E3] Reactivación — Cupón 10% (Día 12)",
    "subject": "Última oportunidad: 10% OFF solo para ti",
    "preheader": "Código VUELVE10 — válido solo hasta el domingo",
    "cta": "Usar mi descuento",
    "cta_url": "https://b370sports.com/tienda",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>Te tenemos algo especial porque ya eres parte de B370:</p>
<p style="text-align:center;margin:24px 0;">
  <span style="font-size:28px;font-weight:900;color:#006A4E;background:#e8f5e9;padding:12px 24px;border-radius:8px;display:inline-block;letter-spacing:2px;">VUELVE10</span>
</p>
<p><strong>10% de descuento</strong> en tu próximo pedido. Sin mínimo de compra. Sin letra chiquita.</p>
<p>⏰ <strong>Solo hasta el domingo.</strong></p>
<p>Esa camiseta que te estabas mirando ya tiene descuento. No la dejes pasar.</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

  {
    "name": "[SEQ3-E4] Reactivación — Último intento (Día 18)",
    "subject": "Antes de decir adiós...",
    "preheader": "¿Seguimos en contacto o prefieres que te demos de baja?",
    "cta": "Sí, sigo aquí",
    "cta_url": "https://b370sports.com/tienda",
    "body": """
<p>Hola <strong>{{contact.firstName | default: 'crack'}}</strong>,</p>
<p>No te vamos a mandar más correos si no quieres. Serios.</p>
<p>Solo queremos saber: <strong>¿seguimos en contacto o prefieres que te saquemos de la lista?</strong></p>
<p>Si te quedas, serás el primero en enterarte de lanzamientos, descuentos y novedades del catálogo.</p>
<p>Si no, también está bien. Sin dramas.</p>
<p style="text-align:center;margin-top:20px;">
  <a href="{{{{unsubscribe_url}}}}" style="font-size:12px;color:#aaaaaa;text-decoration:underline;">Prefiero que me den de baja</a>
</p>
<p style="margin-top:24px;font-style:italic;color:#006A4E;font-weight:700;">En B370, vestimos la pasión.</p>
""",
  },

]

# ─── Subir a Omnisend como borradores ────────────────────────────────────────

def crear_borrador(email: dict) -> dict:
    payload = {
        "name": email["name"],
        "type": "regular",
        "subject": email["subject"],
        "previewText": email["preheader"],
        "fromName": "B370 Línea Deportiva",
        "fromEmail": "hola@b370sports.com",
        "replyTo": "hola@b370sports.com",
        "content": {
            "html": html_email(email["body"], email["cta"], email["cta_url"]),
        },
        "options": {"trackClicks": True, "trackOpens": True},
    }

    r = requests.post(f"{BASE}/campaigns", headers=HEADERS, json=payload, timeout=15)
    if r.status_code in (200, 201):
        data = r.json()
        cid = data.get("campaignID") or data.get("id", "?")
        return {"ok": True, "id": cid, "name": email["name"]}
    else:
        return {"ok": False, "name": email["name"], "status": r.status_code, "error": r.text[:200]}


print("Subiendo 11 emails a Omnisend como borradores...\n")
resultados = []
for i, em in enumerate(EMAILS):
    res = crear_borrador(em)
    status = "OK" if res["ok"] else f"ERROR {res.get('status','?')}"
    print(f"  [{i+1:02d}/11] {status} — {em['name']}")
    resultados.append(res)
    time.sleep(0.5)  # evitar rate limit

ok = sum(1 for r in resultados if r["ok"])
print(f"\nResultado: {ok}/11 emails subidos correctamente a Omnisend.")
print("\nBusca los borradores en Omnisend → Campaigns → All Campaigns")
print("Están nombrados con prefijo [SEQ1], [SEQ2], [SEQ3] para identificarlos fácilmente.")
