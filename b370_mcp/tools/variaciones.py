"""
Tool: variaciones.

Crea variaciones (talla × calidad) para un producto variable.
Replica la lógica de scripts/b370_crear_producto.py y b370_crear_variaciones.py.
"""
import time
from typing import Optional

from b370_mcp import core


def crear_variaciones(
    product_id: int,
    tallas: list[str],
    calidad: Optional[str] = None,
    skus: Optional[dict] = None,
    stock: Optional[dict] = None,
    precio: Optional[float] = None,
    asignar_imagenes: bool = True,
    nombre_imagen: Optional[str] = None,
) -> dict:
    """Crea variaciones para un producto variable.

    Args:
        product_id: ID del producto padre (debe ser type=variable)
        tallas: lista (ej ["S","M","L","XL","XXL"])
        calidad: opcional, atributo "Calidad" (ej "Tipo fan", "Tipo jugador", "1.1")
        skus: opcional, dict {talla: sku} (ej {"S": "2100002006109", "M": "..."})
        stock: opcional, dict {talla: cantidad} (ej {"S": 1, "M": 0, "L": 2})
        precio: opcional, precio único para todas. Si no se pasa, usa
                PRECIOS_DEFAULT[calidad] o falla si no hay calidad.
        asignar_imagenes: si True y nombre_imagen no es None, asigna imagen
                          principal y galería via SSH.
        nombre_imagen: prefijo del archivo en WP Media (ej "BARCELONA-LOCAL")

    Returns:
        Dict con conteo de creadas, errores, IDs de variaciones.
    """
    # Resolver precio
    if precio is None:
        if calidad and calidad in core.PRECIOS_DEFAULT:
            precio = core.PRECIOS_DEFAULT[calidad]
        else:
            return {
                "error": "Falta precio. Pasa precio= explícito o calidad= con valor estándar.",
                "calidades_validas": list(core.PRECIOS_DEFAULT.keys()),
            }

    ok, msg = core.validate_price(precio)
    if not ok:
        return {"error": msg}

    # Validar producto padre
    parent = core.get_product(product_id)
    if not parent:
        return {"error": f"Producto {product_id} no encontrado"}
    if parent.get("type") != "variable":
        return {"error": f"Producto {product_id} no es variable (type={parent.get('type')})"}

    skus = skus or {}
    stock = stock or {}

    plan = []
    for talla in tallas:
        attrs = [{"name": "Tallas", "option": talla}]
        if calidad:
            attrs.append({"name": "Calidad", "option": calidad})
        plan.append({
            "talla": talla,
            "calidad": calidad,
            "sku": skus.get(talla, ""),
            "stock": stock.get(talla, 0),
            "precio": int(precio),
            "attributes": attrs,
        })

    if core.DRY_RUN:
        return {
            "dry_run": True,
            "would_create": len(plan),
            "preview": plan,
            "tip": "Cambia B370_DRY_RUN=false en .env para aplicar",
        }

    creadas = []
    errores = []

    for item in plan:
        payload = {
            "attributes": item["attributes"],
            "sku": item["sku"],
            "regular_price": str(item["precio"]),
            "manage_stock": True,
            "stock_quantity": item["stock"],
            "stock_status": "instock" if item["stock"] > 0 else "outofstock",
        }
        r = core.wc_post(f"products/{product_id}/variations", payload)
        if r.status_code in (200, 201):
            v = r.json()
            creadas.append({
                "id": v["id"],
                "talla": item["talla"],
                "calidad": item["calidad"],
                "sku": item["sku"],
                "stock": item["stock"],
            })
            core.log.info(f"Variación creada: {item['talla']} (SKU {item['sku']})")
        else:
            errores.append({
                "talla": item["talla"],
                "status": r.status_code,
                "error": r.text[:150],
            })
            core.log.error(f"Variación falló {item['talla']}: {r.text[:150]}")
        time.sleep(core.DELAY)

    # Asignar imágenes a variaciones via SSH si aplica
    imagenes_asignadas = False
    if asignar_imagenes and nombre_imagen and creadas:
        image_ids = core.find_image_ids_by_name(nombre_imagen)
        if image_ids:
            main_id = image_ids[0]
            gallery_ids = image_ids[1:]
            # Producto padre
            core.assign_image_meta_via_ssh(product_id, main_id, gallery_ids)
            # Cada variación
            for v in creadas:
                core.assign_image_meta_via_ssh(v["id"], main_id, gallery_ids)
            imagenes_asignadas = True
            core.log.info(f"Imágenes asignadas a {len(creadas)} variaciones")

    return {
        "product_id": product_id,
        "creadas": len(creadas),
        "errores": len(errores),
        "imagenes_asignadas": imagenes_asignadas,
        "detalle_creadas": creadas,
        "detalle_errores": errores,
    }


def recrear_variaciones_producto(product_id: int, plan: dict) -> dict:
    """Reemplaza TODAS las variaciones de un producto con un nuevo plan.

    Replica la lógica de scripts/b370_crear_variaciones.py: borra existentes
    y crea desde cero. Útil para corregir SKUs o reestructurar.

    Args:
        product_id: ID del producto padre
        plan: dict con estructura
            {
                "attr2_name": "Calidad" | "Color" | "Tipo" | None,
                "data": {
                    "Tipo fan": {"S": "sku1", "M": "sku2", ...},
                    "Tipo jugador": {"S": "sku3", ...},
                }
            }
            Si attr2_name es None, usar None como key:
            {"attr2_name": None, "data": {None: {"S": "sku1", ...}}}

    Returns:
        Dict con resumen.
    """
    parent = core.get_product(product_id)
    if not parent:
        return {"error": f"Producto {product_id} no encontrado"}

    # Calcular plan de variaciones
    operaciones = []
    for tipo, tallas_skus in plan["data"].items():
        for talla, sku in tallas_skus.items():
            attrs = [{"name": "Tallas", "option": talla}]
            if plan["attr2_name"] and tipo:
                attrs.append({"name": plan["attr2_name"], "option": tipo})
            operaciones.append({
                "talla": talla,
                "tipo": tipo,
                "sku": sku,
                "attributes": attrs,
            })

    if core.DRY_RUN:
        existing = core.get_variations(product_id)
        return {
            "dry_run": True,
            "borraria": len(existing),
            "crearia": len(operaciones),
            "preview_create": operaciones,
        }

    # Borrar existentes
    existing = core.get_variations(product_id)
    for v in existing:
        core.wc_delete(f"products/{product_id}/variations/{v['id']}", force=True)
        time.sleep(core.DELAY)

    # Crear nuevas
    precio_actual = parent.get("regular_price") or parent.get("price") or ""
    creadas = errores = 0
    for op in operaciones:
        payload = {
            "attributes": op["attributes"],
            "sku": op["sku"],
        }
        if precio_actual:
            payload["regular_price"] = str(precio_actual)
        r = core.wc_post(f"products/{product_id}/variations", payload)
        if r.status_code in (200, 201):
            creadas += 1
        else:
            errores += 1
        time.sleep(core.DELAY)

    return {
        "product_id": product_id,
        "borradas": len(existing),
        "creadas": creadas,
        "errores": errores,
    }
