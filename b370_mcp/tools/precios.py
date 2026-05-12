"""
Tool: precios.

Actualización individual y masiva de precios.
Replica la lógica de scripts/b370_actualizar_precios.py.
"""
import time
from typing import Optional

from b370_mcp import core


def actualizar_precio_variacion(
    product_id: int,
    variation_id: int,
    nuevo_precio: float,
) -> dict:
    """Actualiza el precio de UNA variación.

    Args:
        product_id: ID del producto padre
        variation_id: ID de la variación
        nuevo_precio: precio en COP sin separadores (ej 110000)
    """
    ok, msg = core.validate_price(nuevo_precio)
    if not ok:
        return {"error": msg, "tip": "Si es legítimo, ajusta B370_PRICE_MIN/MAX en .env"}

    payload = {"regular_price": str(int(nuevo_precio))}

    if core.DRY_RUN:
        return {"dry_run": True, "would_update": {"variation_id": variation_id, **payload}}

    r = core.wc_put(f"products/{product_id}/variations/{variation_id}", payload)
    if r.status_code != 200:
        return {"error": f"WC respondió {r.status_code}", "details": r.text[:150]}
    v = r.json()
    core.log.info(f"Precio var {variation_id}: ${int(nuevo_precio):,}")
    return {
        "variation_id": variation_id,
        "sku": v.get("sku"),
        "regular_price": v.get("regular_price"),
    }


def actualizar_precios_por_calidad(
    product_id: int,
    precios_por_calidad: dict[str, float],
) -> dict:
    """Actualiza precios masivamente por valor de Calidad en un producto.

    Replica el patrón PRODUCT_PRICES de scripts/b370_actualizar_precios.py.

    Args:
        product_id: ID del producto padre
        precios_por_calidad: dict {valor_calidad: precio}.
            Si el producto NO tiene atributo "Calidad", usa la key None:
            {None: 120000} → aplica precio único a todas las variaciones.

    Returns:
        Dict con conteo de actualizadas y errores.
    """
    # Validar precios
    for calidad, precio in precios_por_calidad.items():
        ok, msg = core.validate_price(precio)
        if not ok:
            return {"error": f"Precio inválido para '{calidad}': {msg}"}

    variaciones = core.get_variations(product_id)
    if not variaciones:
        return {"error": f"Sin variaciones para producto {product_id}"}

    plan = []
    sin_match = 0

    for v in variaciones:
        calidad_v = core.get_calidad(v)
        # Match: si el producto no tiene calidad, todas las variaciones matchean con key None
        if calidad_v is None and None in precios_por_calidad:
            precio = precios_por_calidad[None]
        elif calidad_v is not None and calidad_v in precios_por_calidad:
            precio = precios_por_calidad[calidad_v]
        else:
            sin_match += 1
            continue
        plan.append({
            "variation_id": v["id"],
            "sku": v.get("sku"),
            "talla": core.get_talla(v),
            "calidad": calidad_v,
            "precio_actual": v.get("regular_price"),
            "precio_nuevo": int(precio),
        })

    if core.DRY_RUN:
        return {
            "dry_run": True,
            "actualizaria": len(plan),
            "sin_match": sin_match,
            "preview": plan,
        }

    actualizadas = errores = 0
    for item in plan:
        r = core.wc_put(
            f"products/{product_id}/variations/{item['variation_id']}",
            {"regular_price": str(item["precio_nuevo"])},
        )
        if r.status_code == 200:
            actualizadas += 1
        else:
            errores += 1
        time.sleep(core.DELAY)

    core.log.info(f"Precios masivos #{product_id}: {actualizadas} ok, {errores} err")

    return {
        "product_id": product_id,
        "actualizadas": actualizadas,
        "errores": errores,
        "sin_match": sin_match,
    }


def actualizar_precios_multi_producto(
    plan: dict[int, dict],
) -> dict:
    """Actualiza precios en MÚLTIPLES productos en una sola operación.

    Replica exactamente el patrón PRODUCT_PRICES de
    scripts/b370_actualizar_precios.py.

    Args:
        plan: dict con estructura
            {
                product_id: {
                    "attr": "Calidad" | None,
                    "precios": {"1.1": 120000, "Tipo jugador": 110000}
                              o {None: 120000}
                },
                ...
            }

    Returns:
        Dict con resumen consolidado.
    """
    resultados = {}
    total_ok = total_err = 0

    for pid, config in plan.items():
        precios = config.get("precios", {})
        # Reusar la función por-producto
        resultado = actualizar_precios_por_calidad(pid, precios)
        resultados[pid] = resultado
        if not core.DRY_RUN:
            total_ok += resultado.get("actualizadas", 0)
            total_err += resultado.get("errores", 0)

    if core.DRY_RUN:
        total_plan = sum(r.get("actualizaria", 0) for r in resultados.values())
        return {
            "dry_run": True,
            "productos_a_procesar": len(plan),
            "variaciones_a_actualizar": total_plan,
            "por_producto": resultados,
        }

    return {
        "productos_procesados": len(plan),
        "actualizadas_total": total_ok,
        "errores_total": total_err,
        "por_producto": resultados,
    }
