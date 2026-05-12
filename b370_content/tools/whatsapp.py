"""
Tools de WhatsApp: generación de broadcasts y mensajes tipo.
"""
from b370_content import core_content as core

TIPOS_BROADCAST = {
    "lanzamiento": "anunciar un producto nuevo con precio y link de compra",
    "cupon": "compartir un cupón de descuento con fecha de vencimiento",
    "partido": "mensaje pre o post partido alusivo a un equipo que venden",
    "restock": "avisar que volvió a haber stock de un producto agotado",
    "status_diario": "contenido rápido para el Status de WhatsApp Business (máx 1 min)",
}


def generar_broadcast_whatsapp(
    tipo: str,
    producto: str = "",
    contexto_extra: str = "",
) -> dict:
    """Genera texto de broadcast para WhatsApp o Status de WhatsApp Business.

    El texto generado está listo para copiar y pegar. Juanjo lo envía manualmente
    desde WhatsApp Business (Status o lista de difusión).

    Args:
        tipo: "lanzamiento", "cupon", "partido", "restock", "status_diario"
        producto: producto o equipo involucrado
        contexto_extra: detalles adicionales (ej: "cupón VIPB370 vence el viernes")

    Returns:
        Dict con mensaje_principal, mensaje_corto (para Status), notas.
    """
    if tipo not in TIPOS_BROADCAST:
        return {"error": f"Tipo inválido. Opciones: {', '.join(TIPOS_BROADCAST.keys())}"}

    tipo_desc = TIPOS_BROADCAST[tipo]

    prompt = f"""Genera un mensaje de WhatsApp Business para B370 Línea Deportiva.

TIPO: {tipo} — {tipo_desc}
{"PRODUCTO/EQUIPO: " + producto if producto else ""}
{"CONTEXTO: " + contexto_extra if contexto_extra else ""}

REGLAS PARA WHATSAPP:
- Tono: conversacional, cercano, como un amigo que te da un dato
- Párrafos MUY cortos (1-2 líneas)
- Usar emojis con moderación (2-3 máximo, relevantes)
- Link de tienda: b370sports.com
- WhatsApp de contacto: w.me/573... (dejar placeholder)
- El mensaje principal para lista de difusión: máx 300 caracteres
- El mensaje corto para Status: máx 100 caracteres

IMPORTANTE: No sonar como spam. Sonar como un parcero que recomienda.
Si es de lanzamiento, incluir precio.
Cerrar con invitación a escribir por WhatsApp para pedidos.

Responde en este formato exacto:
MENSAJE_PRINCIPAL:
[el mensaje completo para lista de difusión]

MENSAJE_CORTO:
[el texto corto para Status de WA]

NOTAS:
[recomendaciones para el envío — 2 líneas]"""

    respuesta = core.llamar_claude(prompt)

    if respuesta.startswith("ERROR"):
        return {"error": respuesta}

    resultado = {"tipo": tipo, "producto": producto}
    partes = {"mensaje_principal": "", "mensaje_corto": "", "notas": ""}
    clave_actual = None
    lineas = []

    for linea in respuesta.split("\n"):
        l = linea.strip()
        if l == "MENSAJE_PRINCIPAL:":
            clave_actual = "mensaje_principal"
            lineas = []
        elif l == "MENSAJE_CORTO:":
            if clave_actual:
                partes[clave_actual] = "\n".join(lineas).strip()
            clave_actual = "mensaje_corto"
            lineas = []
        elif l == "NOTAS:":
            if clave_actual:
                partes[clave_actual] = "\n".join(lineas).strip()
            clave_actual = "notas"
            lineas = []
        elif clave_actual:
            lineas.append(linea)

    if clave_actual and lineas:
        partes[clave_actual] = "\n".join(lineas).strip()

    resultado.update(partes)
    core.log.info(f"Broadcast WA generado: tipo={tipo}, producto={producto}")
    return resultado
