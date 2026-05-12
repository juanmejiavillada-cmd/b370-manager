"""
Núcleo compartido del MCP b370-content.

Centraliza:
- Cliente Anthropic con prompt caching para documentos de marca
- Carga de archivos de b370-brand-context
- Logger compartido
"""
import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

BRAND_REPO = os.getenv("B370_BRAND_REPO", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2000


def setup_logger(name: str = "b370-content") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log_file = str(PROJECT_ROOT / "b370-content.log")
    try:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception as e:
        sys.stderr.write(f"WARN: log file no disponible: {e}\n")
    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


log = setup_logger()


def leer_brand(nombre_relativo: str) -> str:
    """Lee un archivo del repo b370-brand-context."""
    if not BRAND_REPO:
        return ""
    archivo = Path(BRAND_REPO) / nombre_relativo
    if not archivo.exists():
        log.warning(f"No existe: {archivo}")
        return ""
    return archivo.read_text(encoding="utf-8")


def get_anthropic_client():
    """Devuelve cliente Anthropic o None si falta API key."""
    if not ANTHROPIC_API_KEY:
        return None
    try:
        from anthropic import Anthropic
        return Anthropic(api_key=ANTHROPIC_API_KEY)
    except ImportError:
        log.error("anthropic no instalado. pip install anthropic")
        return None


def build_brand_system_blocks() -> list[dict]:
    """Construye los bloques de sistema con prompt caching para documentos de marca.

    Los documentos de marca (~5K tokens) se cachean → 90% ahorro en llamadas repetidas.
    """
    voice_tone = leer_brand("00_brand/voice-tone.md")
    buyer_personas = leer_brand("00_brand/buyer-personas.md")
    precios = leer_brand("02_catalog/precios-estructura.md")

    blocks = []
    if voice_tone:
        blocks.append({
            "type": "text",
            "text": f"VOZ Y TONO DE MARCA B370:\n{voice_tone}",
            "cache_control": {"type": "ephemeral"},
        })
    if buyer_personas:
        blocks.append({
            "type": "text",
            "text": f"BUYER PERSONAS B370:\n{buyer_personas[:3000]}",
            "cache_control": {"type": "ephemeral"},
        })
    if precios:
        blocks.append({
            "type": "text",
            "text": f"ESTRUCTURA DE PRECIOS B370:\n{precios}",
            "cache_control": {"type": "ephemeral"},
        })
    return blocks


def llamar_claude(prompt: str, extra_system: str = "") -> str:
    """Llama a Claude con los bloques de marca en caché.

    Args:
        prompt: el prompt específico de la tarea
        extra_system: contexto adicional no cacheado (ej: datos del producto)

    Returns:
        Texto de respuesta o string de error.
    """
    client = get_anthropic_client()
    if not client:
        return "ERROR: Falta ANTHROPIC_API_KEY en .env"

    system_blocks = build_brand_system_blocks()
    if extra_system:
        system_blocks.append({"type": "text", "text": extra_system})

    if not system_blocks:
        system_blocks = [{"type": "text", "text": "Eres el asistente de contenido de B370 Línea Deportiva, marca colombiana de camisetas de fútbol."}]

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_blocks,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        log.error(f"Error llamando Claude: {e}")
        return f"ERROR: {str(e)[:200]}"
