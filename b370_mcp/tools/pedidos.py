"""
Tool: pedidos.

Consulta pedidos y métricas de ventas de B370 vía WooCommerce REST API.
"""
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from b370_mcp import core


def listar_pedidos(dias: int = 7, estado: str = "any", per_page: int = 100) -> dict:
    """Lista pedidos de los últimos N días.

    Args:
        dias: ventana de tiempo hacia atrás (default 7)
        estado: filtro de estado WC ("processing", "completed", "any")
        per_page: máximo de pedidos a traer

    Returns:
        Dict con total_pedidos, facturacion_total, pedidos (lista resumida).
    """
    desde = (datetime.now(timezone.utc) - timedelta(days=dias)).strftime("%Y-%m-%dT%H:%M:%S")

    params = {
        "after": desde,
        "per_page": per_page,
        "orderby": "date",
        "order": "desc",
    }
    if estado != "any":
        params["status"] = estado

    try:
        r = core.wc_get("orders", **params)
        if r.status_code != 200:
            return {"error": f"WC respondió {r.status_code}", "detalle": r.text[:200]}

        pedidos_raw = r.json()
        total_facturado = sum(float(p.get("total", 0)) for p in pedidos_raw)

        pedidos_resumen = []
        for p in pedidos_raw:
            pedidos_resumen.append({
                "id": p["id"],
                "fecha": p.get("date_created", "")[:10],
                "estado": p.get("status"),
                "total": float(p.get("total", 0)),
                "items": [
                    {
                        "producto": item.get("name"),
                        "qty": item.get("quantity"),
                        "sku": item.get("sku", ""),
                    }
                    for item in p.get("line_items", [])
                ],
            })

        core.log.info(f"listar_pedidos: {len(pedidos_raw)} pedidos en últimos {dias} días")
        return {
            "dias": dias,
            "total_pedidos": len(pedidos_raw),
            "facturacion_total_cop": round(total_facturado),
            "ticket_promedio_cop": round(total_facturado / len(pedidos_raw)) if pedidos_raw else 0,
            "pedidos": pedidos_resumen,
        }
    except Exception as e:
        core.log.error(f"Error listar_pedidos: {e}")
        return {"error": str(e)[:200]}


def metricas_ventas_periodo(dias: int = 7) -> dict:
    """Métricas de ventas agregadas por producto y calidad.

    Útil para el reporte semanal: top productos, unidades vendidas,
    productos sin movimiento.

    Args:
        dias: ventana de tiempo (default 7)

    Returns:
        Dict con top_productos, ventas_por_calidad, alertas_stock.
    """
    resultado = listar_pedidos(dias=dias, estado="any")
    if "error" in resultado:
        return resultado

    ventas_producto = defaultdict(lambda: {"unidades": 0, "facturacion": 0})
    ventas_calidad = defaultdict(lambda: {"unidades": 0, "facturacion": 0})

    for pedido in resultado.get("pedidos", []):
        for item in pedido.get("items", []):
            nombre = item.get("producto", "Sin nombre")
            qty = item.get("qty", 0)
            # Intentar inferir calidad desde el nombre del producto
            calidad = _inferir_calidad(nombre)
            precio_unitario = pedido["total"] / max(
                sum(i["qty"] for i in pedido["items"]), 1
            )

            ventas_producto[nombre]["unidades"] += qty
            ventas_producto[nombre]["facturacion"] += precio_unitario * qty
            ventas_calidad[calidad]["unidades"] += qty
            ventas_calidad[calidad]["facturacion"] += precio_unitario * qty

    top_productos = sorted(
        [{"producto": k, **v} for k, v in ventas_producto.items()],
        key=lambda x: x["unidades"],
        reverse=True,
    )[:10]

    core.log.info(f"metricas_ventas_periodo: {len(ventas_producto)} productos con ventas en {dias} días")
    return {
        "dias": dias,
        "total_pedidos": resultado["total_pedidos"],
        "facturacion_total_cop": resultado["facturacion_total_cop"],
        "ticket_promedio_cop": resultado["ticket_promedio_cop"],
        "top_productos": top_productos,
        "ventas_por_calidad": dict(ventas_calidad),
    }


def _inferir_calidad(nombre_producto: str) -> str:
    """Infiere calidad desde el nombre del producto (heurística)."""
    nombre = nombre_producto.upper()
    if "1.1" in nombre:
        return "1.1"
    if "RETRO" in nombre:
        return "Retro"
    if "TIPO FAN" in nombre or "FAN" in nombre:
        return "Tipo fan"
    if "ORIGINAL" in nombre or "TIPO ORIGINAL" in nombre:
        return "Tipo original"
    return "Sin clasificar"
