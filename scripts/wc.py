"""
Cliente mínimo de WooCommerce REST API.

Usa solo stdlib (urllib) para evitar dependencias bloqueadas por
Application Control de Windows. Auth HTTP Basic sobre HTTPS.

⚠ SOLO MÉTODOS DE LECTURA EN ESTA VERSIÓN.
   POST/PUT/DELETE se agregan después de validar el read flow contra producción.
"""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from config import (
    HTTP_TIMEOUT,
    WC_BASE_URL,
    WC_CONSUMER_KEY,
    WC_CONSUMER_SECRET,
)


class WCError(Exception):
    """Error genérico de la WC REST API."""
    def __init__(self, status: int, message: str, body: Any = None):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message
        self.body = body


def _auth_header() -> str:
    raw = f"{WC_CONSUMER_KEY}:{WC_CONSUMER_SECRET}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def _build_url(endpoint: str, query: Optional[dict] = None) -> str:
    base = WC_BASE_URL.rstrip("/") + "/wp-json/wc/v3/" + endpoint.lstrip("/")
    if query:
        base += "?" + urllib.parse.urlencode(query, doseq=True)
    return base


def _request(method: str, endpoint: str, query: Optional[dict] = None, body: Optional[dict] = None) -> Any:
    url = _build_url(endpoint, query)
    data = None
    headers = {
        "Authorization": _auth_header(),
        "Accept": "application/json",
        "User-Agent": "b370-cli/0.1",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, method=method.upper(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
            msg = parsed.get("message", raw)
        except json.JSONDecodeError:
            parsed = raw
            msg = raw[:300]
        raise WCError(e.code, msg, parsed) from None
    except urllib.error.URLError as e:
        raise WCError(0, f"No se pudo conectar con {url}: {e.reason}") from None


# ----------------- Métodos de lectura -----------------

def ping() -> dict:
    """
    Verifica autenticación. Pide la lista de catálogos del store
    (endpoint barato que requiere credenciales válidas).
    """
    return _request("GET", "system_status", query={"_fields": "environment,settings"})


def list_variable_products(per_page: int = 100, max_pages: int = 50) -> list[dict]:
    """Pagina hasta el final productos type=variable, status=publish."""
    out: list[dict] = []
    page = 1
    while page <= max_pages:
        batch = _request("GET", "products", query={
            "type": "variable",
            "status": "publish",
            "per_page": per_page,
            "page": page,
            "_fields": "id,name,sku,permalink,variations",
        })
        if not isinstance(batch, list) or not batch:
            break
        out.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return out


def get_product(product_id: int) -> dict:
    return _request("GET", f"products/{int(product_id)}")


def list_variations(product_id: int, per_page: int = 100) -> list[dict]:
    out: list[dict] = []
    page = 1
    while True:
        batch = _request("GET", f"products/{int(product_id)}/variations", query={
            "per_page": per_page,
            "page": page,
        })
        if not isinstance(batch, list) or not batch:
            break
        out.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return out


def get_size_attribute_options() -> list[str]:
    """
    Devuelve los términos del atributo global de tallas (pa_tallas / pa_talla).
    Útil para detectar qué tallas YA existen vs cuáles hay que crear.
    """
    attrs = _request("GET", "products/attributes")
    if not isinstance(attrs, list):
        return []
    target = None
    for a in attrs:
        slug = (a.get("slug") or "").lower()
        name = (a.get("name") or "").lower()
        if slug in ("pa_talla", "pa_tallas") or "talla" in name:
            target = a
            break
    if not target:
        return []
    terms = _request("GET", f"products/attributes/{int(target['id'])}/terms", query={"per_page": 100})
    if not isinstance(terms, list):
        return []
    return [t.get("name", "") for t in terms]
