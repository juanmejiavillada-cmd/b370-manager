"""
Tools de contenido social: posts para Instagram, TikTok, Facebook.
"""
from b370_content import core_content as core

CANALES = ["instagram", "tiktok", "facebook"]

PILARES = {
    "venta": "venta directa del producto con precio y CTA",
    "educacion": "contenido educativo sobre calidades, tallas, materiales",
    "entretenimiento": "humor, curiosidades del fútbol, cultura del hincha",
    "aspiracional": "identidad, orgullo, emoción de vestir la camiseta",
    "credibilidad": "testimonios, Jorman Campuzano, sede física, contra-entrega",
}

FORMATO_CANAL = {
    "instagram": {
        "caption_max": 2200,
        "visible_sin_expandir": 125,
        "hashtags": "5-10, mezcla equipo + marca + comunidad",
        "formato_imagen": "1080x1080 cuadrado o 1080x1350 vertical",
    },
    "tiktok": {
        "caption_max": 150,
        "hashtags": "3-5, trending + nicho",
        "formato_video": "1080x1920 vertical, 15-60 segundos",
    },
    "facebook": {
        "caption_max": 63206,
        "recomendado": "primeras 125 chars son las más visibles",
        "hashtags": "2-3 máximo",
    },
}


def generar_post_social(
    canal: str,
    pilar: str,
    producto: str = "",
    contexto_extra: str = "",
) -> dict:
    """Genera caption + hashtags para un post en IG, TikTok o Facebook.

    Args:
        canal: "instagram", "tiktok" o "facebook"
        pilar: "venta", "educacion", "entretenimiento", "aspiracional", "credibilidad"
        producto: nombre del producto a mencionar (opcional)
        contexto_extra: info adicional (ej: "hoy hay clásico Nacional vs Millonarios")

    Returns:
        Dict con canal, pilar, caption, hashtags, notas_publicacion.
    """
    canal = canal.lower()
    if canal not in CANALES:
        return {"error": f"Canal inválido. Opciones: {', '.join(CANALES)}"}
    if pilar not in PILARES:
        return {"error": f"Pilar inválido. Opciones: {', '.join(PILARES.keys())}"}

    formato = FORMATO_CANAL[canal]
    pilar_desc = PILARES[pilar]

    prompt = f"""Genera UN post para {canal.upper()} de B370 Línea Deportiva.

PILAR DE CONTENIDO: {pilar} — {pilar_desc}
{"PRODUCTO A DESTACAR: " + producto if producto else "Sin producto específico — genera contenido de marca"}
{"CONTEXTO: " + contexto_extra if contexto_extra else ""}

CANAL: {canal.upper()}
- Límite de caption: {formato['caption_max']} caracteres
- Hashtags recomendados: {formato.get('hashtags', '5-7')}

INSTRUCCIONES:
1. Escribe el caption siguiendo el tono B370: pasional, directo, colombiano, tú
2. Las primeras 125 caracteres deben enganchar — son lo que se ve sin expandir
3. Si es pilar venta: incluir precio y CTA concreto (ej: "Pídela hoy. La pagas cuando llega.")
4. Cierre de copy comercial SIEMPRE: "En B370, vestimos la pasión."
5. Genera los hashtags separados del caption
6. Añade notas cortas de publicación (mejor hora, tipo de imagen/video sugerido)

Responde en este formato exacto:
CAPTION:
[el caption completo]

HASHTAGS:
[hashtags separados por espacio]

NOTAS:
[notas de publicación en 2-3 líneas]"""

    respuesta = core.llamar_claude(prompt)

    if respuesta.startswith("ERROR"):
        return {"error": respuesta}

    resultado = {"canal": canal, "pilar": pilar, "producto": producto}
    partes = {"caption": "", "hashtags": "", "notas": ""}
    clave_actual = None
    lineas = []

    for linea in respuesta.split("\n"):
        l = linea.strip()
        if l == "CAPTION:":
            clave_actual = "caption"
            lineas = []
        elif l == "HASHTAGS:":
            if clave_actual:
                partes[clave_actual] = "\n".join(lineas).strip()
            clave_actual = "hashtags"
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
    core.log.info(f"Post generado: {canal}/{pilar} — {producto or 'sin producto'}")
    return resultado


def generar_stories_pack(
    producto: str,
    tipo: str = "lanzamiento",
    cantidad: int = 5,
) -> dict:
    """Genera un pack de stories secuenciales para Instagram.

    Args:
        producto: nombre del producto a lanzar
        tipo: "lanzamiento", "educativo", "credibilidad", "urgencia"
        cantidad: número de stories (default 5, max 7)

    Returns:
        Dict con lista de stories, cada una con texto, cta, nota_visual.
    """
    cantidad = min(cantidad, 7)

    TIPOS = {
        "lanzamiento": "revelar un producto nuevo de forma progresiva y generar deseo",
        "educativo": "explicar las diferencias entre calidades Tipo Fan / Tipo Original / 1.1",
        "credibilidad": "mostrar la trayectoria y confianza de B370 (sede, Jorman, contra-entrega)",
        "urgencia": "motivar compra inmediata por stock limitado o fecha especial",
    }

    tipo_desc = TIPOS.get(tipo, TIPOS["lanzamiento"])

    prompt = f"""Genera un pack de {cantidad} stories secuenciales de Instagram para B370.

PRODUCTO: {producto}
OBJETIVO DEL PACK: {tipo_desc}

REGLAS:
- Cada story debe funcionar sola Y en secuencia
- Story 1: hook fuerte que detenga el scroll (pregunta, afirmación impactante, misterio)
- Stories intermedias: desarrollo del hook, datos del producto, beneficios
- Última story: CTA claro con "Pídela hoy. La pagas cuando llega." o variante
- Máximo 15 palabras de texto visible por story (el resto es imagen/video)
- Tono pasional, colombiano, directo

Responde en este formato exacto para CADA story:
STORY [número]:
TEXTO: [texto de la story — máx 15 palabras]
CTA: [botón/swipe-up si aplica, sino "ninguno"]
NOTA VISUAL: [descripción de qué imagen/video usar — 1 línea]
---"""

    respuesta = core.llamar_claude(prompt)

    if respuesta.startswith("ERROR"):
        return {"error": respuesta}

    stories = []
    bloque_actual = {}
    for linea in respuesta.split("\n"):
        l = linea.strip()
        if l.startswith("STORY "):
            if bloque_actual:
                stories.append(bloque_actual)
            bloque_actual = {"numero": len(stories) + 1}
        elif l.startswith("TEXTO:"):
            bloque_actual["texto"] = l.replace("TEXTO:", "").strip()
        elif l.startswith("CTA:"):
            bloque_actual["cta"] = l.replace("CTA:", "").strip()
        elif l.startswith("NOTA VISUAL:"):
            bloque_actual["nota_visual"] = l.replace("NOTA VISUAL:", "").strip()
    if bloque_actual and "texto" in bloque_actual:
        stories.append(bloque_actual)

    core.log.info(f"Stories pack generado: {len(stories)} stories para '{producto}'")
    return {
        "producto": producto,
        "tipo": tipo,
        "total_stories": len(stories),
        "stories": stories,
    }
