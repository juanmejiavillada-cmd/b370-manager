"""
B370 Content — MCP Server
=========================

Genera contenido de marketing para B370 Línea Deportiva:
- Posts para Instagram, TikTok y Facebook
- Packs de stories de lanzamiento
- Emails para Omnisend (generación + envío)
- Broadcasts de WhatsApp

Todos los tools leen automáticamente el voice-tone y buyer-personas del repo
b370-brand-context con prompt caching activo (90% ahorro en tokens).

Configuración en .claude/settings.json:
{
  "mcpServers": {
    "b370-content": {
      "command": "C:\\...\\venv\\Scripts\\python.exe",
      "args": ["C:\\...\\B370-MANAGER\\b370_content\\server.py"]
    }
  }
}

Variables de entorno requeridas:
  ANTHROPIC_API_KEY     — para generación con Claude
  B370_BRAND_REPO       — ruta al repo b370-brand-context
  OMNISEND_API_KEY      — para envío de emails (solo enviar_email_omnisend)
  OMNISEND_SEGMENT_ID   — ID de segmento en Omnisend (opcional, si vacío envía a todos)
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastmcp import FastMCP

from b370_content import core_content as core
from b370_content.tools import social, email_omnisend, whatsapp

mcp = FastMCP("b370-content")
core.log.info("b370-content-mcp arrancando")


# ============================================================================
# TOOLS — Social
# ============================================================================

@mcp.tool()
def generar_post_social(
    canal: str,
    pilar: str,
    producto: str = "",
    contexto_extra: str = "",
) -> dict:
    """Genera caption + hashtags listos para publicar en Instagram, TikTok o Facebook.

    Args:
        canal: "instagram", "tiktok" o "facebook"
        pilar: "venta", "educacion", "entretenimiento", "aspiracional", "credibilidad"
        producto: nombre del producto a destacar (opcional)
        contexto_extra: info del día (ej: "hoy hay clásico Nacional vs Millonarios 8pm")
    """
    return social.generar_post_social(canal, pilar, producto, contexto_extra)


@mcp.tool()
def generar_stories_pack(
    producto: str,
    tipo: str = "lanzamiento",
    cantidad: int = 5,
) -> dict:
    """Genera un pack de stories secuenciales de Instagram para un lanzamiento o campaña.

    Args:
        producto: nombre del producto (ej "Barcelona Local 2026 1.1")
        tipo: "lanzamiento", "educativo", "credibilidad" o "urgencia"
        cantidad: número de stories (3-7, default 5)
    """
    return social.generar_stories_pack(producto, tipo, cantidad)


# ============================================================================
# TOOLS — Email / Omnisend
# ============================================================================

@mcp.tool()
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
    """
    return email_omnisend.generar_email_kampania(tipo, producto, segmento, contexto_extra)


@mcp.tool()
def enviar_email_omnisend(
    asunto: str,
    preheader: str,
    body_html: str,
    nombre_campana: str = "",
    programar_para: str = "",
) -> dict:
    """Crea y envía (o programa) una campaña de email en Omnisend.

    Requiere OMNISEND_API_KEY en .env (Omnisend → Store Settings → API Keys).
    Usar generar_email_kampania primero para obtener el contenido.

    Args:
        asunto: línea de asunto del email (máx 50 chars recomendado)
        preheader: texto de vista previa (máx 90 chars)
        body_html: HTML completo del body
        nombre_campana: nombre interno en Omnisend (se autogenera si vacío)
        programar_para: ISO 8601 para programar (ej "2026-05-03T09:00:00Z").
                        Dejar vacío para envío inmediato.
    """
    return email_omnisend.enviar_email_omnisend(
        asunto, preheader, body_html, nombre_campana, programar_para
    )


# ============================================================================
# TOOLS — WhatsApp
# ============================================================================

@mcp.tool()
def generar_broadcast_whatsapp(
    tipo: str,
    producto: str = "",
    contexto_extra: str = "",
) -> dict:
    """Genera texto de broadcast para WhatsApp o Status de WhatsApp Business.

    El texto queda listo para copiar y enviar manualmente desde WhatsApp Business.

    Args:
        tipo: "lanzamiento", "cupon", "partido", "restock" o "status_diario"
        producto: producto o equipo relevante (opcional)
        contexto_extra: detalles adicionales (ej: "cupón VIPB370, vence el viernes")
    """
    return whatsapp.generar_broadcast_whatsapp(tipo, producto, contexto_extra)


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    core.log.info("MCP b370-content listo · transport=stdio")
    mcp.run()
