"""
Tool: stock.

Consulta y actualización de inventario.
Replica la lógica de scripts/b370_actualizar_stock.py adaptada a MCP.
"""
import time

from b370_mcp import core


def consultar_stock(product_id: int) -> dict:
    """Stock actual de todas las variaciones.

    Args:
        product_id: ID del producto padre

    Returns:
        Dict con total, sin_stock, y detalle por variación.
    """
    variaciones = core.get_variations(product_id)
    if not variaciones:
        return {"error": f"Sin variaciones o producto {product_id} no existe"}

    detalle = []
    total = 0
    sin_stock = 0
    for v in variaciones:
        qty = v.get("stock_quantity") or 0
        total += qty
        if qty == 0:
            sin_stock += 1
        detalle.append({
            "id": v["id"],
            "sku": v.get("sku"),
            "talla": core.get_talla(v),
            "calidad": core.get_calidad(v),
            "stock": qty,
            "stock_status": v.get("stock_status"),
            "precio": v.get("price"),
        })

    return {
        "product_id": product_id,
        "total_variaciones": len(variaciones),
        "total_stock": total,
        "variaciones_sin_stock": sin_stock,
        "detalle": detalle,
    }


def actualizar_stock_variacion(
    product_id: int,
    variation_id: int,
    nuevo_stock: int,
) -> dict:
    """Actualiza stock de UNA variación.

    Args:
        product_id: ID del producto padre
        variation_id: ID de la variación
        nuevo_stock: cantidad nueva (entero >= 0)
    """
    if nuevo_stock < 0:
        return {"error": "Stock no puede ser negativo"}

    payload = {
        "manage_stock": True,
        "stock_quantity": nuevo_stock,
        "stock_status": "instock" if nuevo_stock > 0 else "outofstock",
    }

    if core.DRY_RUN:
        return {
            "dry_run": True,
            "would_update": {"variation_id": variation_id, **payload},
        }

    r = core.wc_put(f"products/{product_id}/variations/{variation_id}", payload)
    if r.status_code != 200:
        return {"error": f"WC respondió {r.status_code}", "details": r.text[:150]}
    v = r.json()
    core.log.info(f"Stock actualizado var {variation_id}: {nuevo_stock}")
    return {
        "variation_id": variation_id,
        "sku": v.get("sku"),
        "nuevo_stock": v.get("stock_quantity"),
        "stock_status": v.get("stock_status"),
    }


def actualizar_stock_por_sku(stock_map: dict[str, int], product_ids: list[int]) -> dict:
    """Actualiza stock masivo cruzando SKU contra un mapa.

    Replica el comportamiento de scripts/b370_actualizar_stock.py:
    busca en los product_ids dados, y por cada variación cuyo SKU esté en
    stock_map, actualiza la cantidad.

    Args:
        stock_map: dict {sku: cantidad}, ej {"2100002004204": 1, ...}
        product_ids: lista de IDs de productos a procesar

    Returns:
        Dict con conteo de actualizadas, errores, sin SKU.
    """
    total_ok = total_err = sin_sku = 0
    log_detalle = []

    if core.DRY_RUN:
        # En dry-run, recolectamos el plan
        plan = []
        for pid in product_ids:
            for v in core.get_variations(pid):
                sku = (v.get("sku") or "").strip()
                if not sku or sku not in stock_map:
                    sin_sku += 1
                    continue
                plan.append({
                    "product_id": pid,
                    "variation_id": v["id"],
                    "sku": sku,
                    "talla": core.get_talla(v),
                    "calidad": core.get_calidad(v),
                    "stock_actual": v.get("stock_quantity"),
                    "stock_nuevo": stock_map[sku],
                })
        return {
            "dry_run": True,
            "actualizaria": len(plan),
            "sin_sku": sin_sku,
            "preview": plan[:30],
            "total_preview": len(plan),
        }

    # Modo real
    for pid in product_ids:
        for v in core.get_variations(pid):
            sku = (v.get("sku") or "").strip()
            if not sku or sku not in stock_map:
                sin_sku += 1
                continue
            qty = stock_map[sku]
            payload = {
                "manage_stock": True,
                "stock_quantity": qty,
                "stock_status": "instock" if qty > 0 else "outofstock",
            }
            r = core.wc_put(f"products/{pid}/variations/{v['id']}", payload)
            if r.status_code == 200:
                total_ok += 1
                log_detalle.append({"sku": sku, "qty": qty, "ok": True})
            else:
                total_err += 1
                log_detalle.append({"sku": sku, "qty": qty, "ok": False})
            time.sleep(core.DELAY)

    core.log.info(f"Stock masivo: {total_ok} ok, {total_err} err, {sin_sku} sin sku")

    return {
        "actualizadas": total_ok,
        "errores": total_err,
        "sin_sku": sin_sku,
        "detalle": log_detalle[:50],
    }
