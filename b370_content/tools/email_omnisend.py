"""
Tools de email: generación de campañas y envío via Omnisend API.
"""
import os
from datetime import datetime, timezone

from b370_content import core_content as core

OMNISEND_KEY = os.getenv("OMNISEND_API_KEY", "")
OMNISEND_SEGMENT_ID = os.getenv("OMNISEND_SEGMENT_ID", "")
OMNISEND_BASE = "https://api.omnisend.com/v3"


def _omnisend_headers() -> dict:
    return {
        "X-API-Key": OMNISEND_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def generar_email_kampania(
    tipo: str,
    producto: str = "",
    segmento: str = "general",
    contexto_extra: str = "",
) -> dict:
    """Genera asunto + preheader + body HTML para un email de Omnisend.

    NO envía — solo genera el contenido para revisión antes de enviar.

    Args:
        tipo: "lanzamiento", "carrito_abandonado", "post_compra", "cupon", "broadcast"
        producto: nombre del producto a destacar (opcional)
        segmento: "general", "vip" o "compradores_recientes"
        contexto_extra: datos adicionales (ej: "cupón VIPB370 vence el viernes")

    Returns:
        Dict con asunto, preheader, body_html listo para enviar_email_omnisend.
    """
    TIPOS = {
        "lanzamiento": "anunciar un producto nuevo con urgencia y entusiasmo",
        "carrito_abandonado": "recuperar a alguien que agregó al carrito pero no compró",
        "post_compra": "agradecer la compra y pedir recomendación/reseña",
        "cupon": "entregar un cupón de descuento con urgencia de vencimiento",
        "broadcast": "mensaje masivo sobre novedad, evento o promoción",
    }

    SEGMENTOS = {
        "general": "todos los suscriptores (hinchas que conocen la marca pero pueden no haber comprado)",
        "vip": "clientes VIP con historial de compra (tratalos con privilegio)",
        "compradores_recientes": "compraron en los últimos 30 días (referencia su compra previa)",
    }

    tipo_desc = TIPOS.get(tipo, TIPOS["broadcast"])
    seg_desc = SEGMENTOS.get(segmento, SEGMENTOS["general"])

    prompt = f"""Genera un email de marketing para B370 Línea Deportiva.

TIPO: {tipo} — {tipo_desc}
{"PRODUCTO: " + producto if producto else ""}
SEGMENTO: {segmento} — {seg_desc}
{"CONTEXTO ADICIONAL: " + contexto_extra if contexto_extra else ""}

REGLAS:
- Asunto: máx 50 caracteres, que genere apertura, sin clickbait falso
- Preheader: complementa el asunto, máx 90 caracteres
- Body: tono pasional y directo. Párrafos cortos (2-3 oraciones max)
- Incluir CTA claro como botón (escríbelo como [BOTÓN: texto del botón | URL_PLACEHOLDER])
- Cerrar con "En B370, vestimos la pasión."
- El body va en HTML simple (p, strong, em, a — sin CSS inline complejo)
- Usa {{{{ contact.firstName | default: 'crack' }}}} para personalización de nombre (sintaxis Omnisend)
- Si hay cupón: ponlo en grande y con vencimiento

Responde en este formato exacto:
ASUNTO:
[el asunto]

PREHEADER:
[el preheader]

BODY_HTML:
[el HTML del body]"""

    respuesta = core.llamar_claude(prompt)

    if respuesta.startswith("ERROR"):
        return {"error": respuesta}

    resultado = {"tipo": tipo, "producto": producto, "segmento": segmento}
    partes = {"asunto": "", "preheader": "", "body_html": ""}
    clave_actual = None
    lineas = []

    for linea in respuesta.split("\n"):
        l = linea.strip()
        if l == "ASUNTO:":
            clave_actual = "asunto"
            lineas = []
        elif l == "PREHEADER:":
            if clave_actual:
                partes[clave_actual] = "\n".join(lineas).strip()
            clave_actual = "preheader"
            lineas = []
        elif l == "BODY_HTML:":
            if clave_actual:
                partes[clave_actual] = "\n".join(lineas).strip()
            clave_actual = "body_html"
            lineas = []
        elif clave_actual:
            lineas.append(linea)

    if clave_actual and lineas:
        partes[clave_actual] = "\n".join(lineas).strip()

    resultado.update(partes)
    core.log.info(f"Email generado (Omnisend): tipo={tipo}, producto={producto}")
    return resultado


def enviar_email_omnisend(
    asunto: str,
    preheader: str,
    body_html: str,
    nombre_campana: str = "",
    programar_para: str = "",
) -> dict:
    """Crea y envía (o programa) una campaña de email en Omnisend.

    Requiere OMNISEND_API_KEY en .env.
    Usar generar_email_kampania primero para obtener el contenido.

    Args:
        asunto: línea de asunto del email (máx 50 chars recomendado)
        preheader: texto de vista previa (máx 90 chars)
        body_html: HTML completo del body
        nombre_campana: nombre interno en Omnisend (se autogenera si vacío)
        programar_para: ISO 8601 para programar (ej "2026-05-03T09:00:00Z").
                        Dejar vacío para envío inmediato.

    Returns:
        Dict con campaign_id, status.
    """
    if not OMNISEND_KEY:
        return {"error": "Falta OMNISEND_API_KEY en .env — consíguela en Omnisend → Store Settings → API Keys"}

    try:
        import requests
    except ImportError:
        return {"error": "requests no instalado. pip install requests"}

    if not nombre_campana:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
        nombre_campana = f"B370-{ts}"

    h = _omnisend_headers()

    # Construir payload de la campaña
    campaign_payload = {
        "name": nombre_campana,
        "type": "regular",
        "subject": asunto,
        "previewText": preheader,
        "fromName": "B370 Línea Deportiva",
        "fromEmail": "hola@b370sports.com",
        "replyTo": "hola@b370sports.com",
        "content": {
            "html": body_html,
        },
        "options": {
            "trackClicks": True,
            "trackOpens": True,
        },
    }

    # Agregar segmento si está configurado
    if OMNISEND_SEGMENT_ID:
        campaign_payload["recipients"] = {
            "segments": [OMNISEND_SEGMENT_ID],
        }

    # 1. Crear la campaña
    r_create = requests.post(f"{OMNISEND_BASE}/campaigns", headers=h, json=campaign_payload)
    if r_create.status_code not in (200, 201):
        return {
            "error": f"Error creando campaña Omnisend: {r_create.status_code}",
            "detalle": r_create.text[:300],
        }

    campaign_data = r_create.json()
    campaign_id = campaign_data.get("campaignID") or campaign_data.get("id", "")
    core.log.info(f"Campaña Omnisend creada: {campaign_id}")

    # 2. Enviar o programar
    send_payload = {}
    if programar_para:
        send_payload["scheduledFor"] = programar_para

    r_send = requests.post(
        f"{OMNISEND_BASE}/campaigns/{campaign_id}/actions/start",
        headers=h,
        json=send_payload,
    )

    if r_send.status_code not in (200, 201, 204):
        return {
            "error": f"Error enviando campaña: {r_send.status_code}",
            "campaign_id": campaign_id,
            "detalle": r_send.text[:300],
            "tip": "La campaña fue creada — puedes enviarla manualmente desde Omnisend",
        }

    core.log.info(f"Email Omnisend enviado/programado: campaign_id={campaign_id}")
    return {
        "ok": True,
        "campaign_id": campaign_id,
        "nombre_campana": nombre_campana,
        "estado": "programado" if programar_para else "enviando",
        "programado_para": programar_para or "inmediato",
    }
