"""
Configuración del CLI de B370.
Las credenciales se leen del archivo .env en la raíz del proyecto.
NUNCA escribir claves directamente aquí.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Busca el .env en la raíz del proyecto (un nivel arriba de /scripts)
_ENV_FILE = Path(__file__).parent.parent / ".env"
load_dotenv(_ENV_FILE)


def _require(key: str) -> str:
    val = os.environ.get(key, "").strip()
    if not val:
        print(f"❌ Falta la variable {key} en el archivo .env")
        print(f"   Revisa {_ENV_FILE}")
        sys.exit(1)
    return val


WC_BASE_URL = _require("WC_URL")
WC_CONSUMER_KEY    = _require("WC_CK")
WC_CONSUMER_SECRET = _require("WC_CS")

SSH_HOST = os.environ.get("SSH_HOST", "")
SSH_PORT = int(os.environ.get("SSH_PORT", "22"))
SSH_USER = os.environ.get("SSH_USER", "")
SSH_PATH = os.environ.get("SSH_PATH", "")

QUENTI_DEFAULT_XLSX = os.environ.get(
    "XLSX_PATH",
    r"C:\Users\USUARIO\Downloads\CUENTI INVENTARIO 6 ABRIL.xlsx",
)

HTTP_TIMEOUT = 30
