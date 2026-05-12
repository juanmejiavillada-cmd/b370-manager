"""
Tool: copys.

Genera copy de producto siguiendo el voice-tone de B370.
Lee el repo b370-brand-context (si está configurado en B370_BRAND_REPO).
"""
import os
import json
from pathlib import Path
from typing import Optional

from b370_mcp import core


def _leer_archivo_brand(nombre_relativo: str) -> str:
    """Lee un archivo del repo b370-brand-context si está configurado."""
    repo_path = os.getenv("B370_BRAND_REPO")
    if not repo_path:
        return ""
    archivo = Path(repo_path) / nombre_relativo
    if not archivo.exists():
        core.log.warning(f"No existe: {archivo}")
        return ""
    return archivo.read_text(encoding="utf-8")


def generar_copy_producto(
    nombre_producto: str,
    equipo: str,
    temporada: str = "2026",
    calidades_disponibles: Optional[list[str]] = None,
    persona_objetivo: str = "premium",
) -> dict:
    """Genera copy completo de producto usando Claude API + voice-tone B370.

    Lee automáticamente del repo b370-brand-context:
    - 00_brand/voice-tone.md
    - 00_brand/buyer-personas.md

    Args:
        nombre_producto: ej "BARCELONA LOCAL 2026 1.1"
        equipo: ej "Barcelona"
        temporada: ej "2026"
        calidades_disponibles: ej ["Tipo fan","Tipo original","1.1"]
        persona_objetivo: "premium" o "budget"

    Returns:
        Dict con title_seo, description_short, description_long, bullets, cta.
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        return {"error": "Falta anthropic. pip install anthropic"}

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "error": "Falta ANTHROPIC_API_KEY en .env",
            "tip": "Agrégala al .env del proyecto",
        }

    voice_tone = _leer_archivo_brand("00_brand/voice-tone.md")
    if not voice_tone:
        return {
            "error": "No se pudo leer voice-tone.md del repo de marca",
            "tip": "Configura B370_BRAND_REPO en .env apuntando al repo b370-brand-context",
        }

    buyer_personas = _leer_archivo_brand("00_brand/buyer-personas.md")
    calidades_disponibles = calidades_disponibles or ["Tipo fan", "Tipo original", "1.1"]

    persona_label = (
        "Premium street/stadium buyer (hombre 20-35, paga por autenticidad y look)"
        if persona_objetivo == "premium"
        else "Budget fan buyer (hincha promedio, prioriza precio y diseño)"
    )

    system_blocks = [
        {
            "type": "text",
            "text": f"GUÍA DE TONO Y VOZ B370 (RESPÉTALA):\n{voice_tone}",
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": f"BUYER PERSONAS DE B370:\n{buyer_personas[:3000]}",
            "cache_control": {"type": "ephemeral"},
        },
    ]

    prompt = f"""Eres el copywriter de B370 Línea Deportiva.
Genera el copy completo para un producto que se publicará en b370sports.com.

PRODUCTO:
- Nombre: {nombre_producto}
- Equipo: {equipo}
- Temporada: {temporada}
- Calidades disponibles: {', '.join(calidades_disponibles)}
- Persona objetivo: {persona_label}

INSTRUCCIONES:
Genera el copy en JSON válido con estas claves exactas:
- "title_seo": título corto (máx 60 caracteres) con equipo + año + camiseta
- "description_short": resumen de 2-3 líneas (máx 200 caracteres)
- "description_long": descripción completa para la ficha (3-4 párrafos cortos)
- "bullets": array de 4-6 bullets de características clave
- "cta": llamado a la acción que cierre con la frase obligatoria de B370

Responde ÚNICAMENTE con el JSON, sin markdown, sin texto adicional."""

    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=system_blocks,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()

        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        copy_data = json.loads(text)
        core.log.info(f"Copy generado: {nombre_producto}")
        return {
            "producto": nombre_producto,
            "persona": persona_objetivo,
            **copy_data,
        }
    except Exception as e:
        core.log.error(f"Error generando copy: {e}")
        return {"error": f"Falló generación: {str(e)[:200]}"}


def actualizar_copy_en_wc(product_id: int, copy_dict: dict) -> dict:
    """Aplica copy generado a un producto en WooCommerce vía REST API.

    Campos que actualiza: name (title_seo), short_description, description.
    Si DRY_RUN está activo, solo simula y devuelve el payload.

    Args:
        product_id: ID del producto en WooCommerce
        copy_dict: dict con title_seo, description_short, description_long,
                   bullets (list[str]), cta (str)

    Returns:
        Dict con status, product_id, url del producto.
    """
    title = copy_dict.get("title_seo", "")
    short = copy_dict.get("description_short", "")
    long_desc = copy_dict.get("description_long", "")
    bullets = copy_dict.get("bullets", [])
    cta = copy_dict.get("cta", "")

    bullets_html = ""
    if bullets:
        items = "\n".join(f"  <li>{b}</li>" for b in bullets)
        bullets_html = f"\n<ul>\n{items}\n</ul>"

    full_description = f"{long_desc}{bullets_html}"
    if cta:
        full_description += f"\n<p><strong>{cta}</strong></p>"

    payload = {
        "name": title,
        "short_description": short,
        "description": full_description,
    }

    if core.DRY_RUN:
        core.log.info(f"[DRY] actualizar_copy_en_wc product_id={product_id}")
        return {
            "dry_run": True,
            "product_id": product_id,
            "payload_preview": payload,
            "message": "Activa B370_DRY_RUN=false en .env para aplicar",
        }

    try:
        r = core.wc_put(f"products/{product_id}", payload)
        if r.status_code in (200, 201):
            data = r.json()
            core.log.info(f"Copy aplicado a producto {product_id}")
            return {
                "ok": True,
                "product_id": product_id,
                "url": data.get("permalink", ""),
                "name": data.get("name", ""),
            }
        else:
            core.log.error(f"Error WC al actualizar copy {product_id}: {r.status_code} {r.text[:200]}")
            return {"error": f"WC respondió {r.status_code}", "detalle": r.text[:200]}
    except Exception as e:
        core.log.error(f"Excepción actualizar_copy_en_wc: {e}")
        return {"error": str(e)[:200]}
