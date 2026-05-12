"""
Tool: productos.

Operaciones de lectura y creación de productos respetando las convenciones
del proyecto B370-MANAGER (atributos "Tallas" y "Calidad", precios oficiales).
"""
import time
from typing import Optional

from b370_mcp import core


def listar_productos(
    busqueda: Optional[str] = None,
    categoria: Optional[str] = None,
    per_page: int = 50,
) -> list[dict]:
    """Lista productos publicados de la tienda B370.

    Args:
        busqueda: texto a buscar en el nombre (opcional)
        categoria: nombre o slug de categoría (opcional)
        per_page: máximo a devolver

    Returns:
        Lista con id, name, status, price, total_sales, stock_status, categories
    """
    params = {"per_page": per_page, "status": "publish"}
    if busqueda:
        params["search"] = busqueda
    if categoria:
        # WC admite filtro por slug si se conoce el ID; si no, usamos search
        cat_lookup = core.wc_get("products/categories", search=categoria, per_page=10)
        if cat_lookup.status_code == 200 and cat_lookup.json():
            params["category"] = str(cat_lookup.json()[0]["id"])

    r = core.wc_get("products", **params)
    if r.status_code != 200:
        core.log.error(f"listar_productos: HTTP {r.status_code}")
        return []

    productos = r.json()
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "type": p.get("type"),
            "status": p["status"],
            "price": p.get("price"),
            "total_sales": p.get("total_sales", 0),
            "stock_status": p.get("stock_status"),
            "permalink": p.get("permalink"),
            "categories": [c["name"] for c in p.get("categories", [])],
        }
        for p in productos
    ]


def consultar_producto(product_id: int) -> dict:
    """Detalle completo de un producto + variaciones.

    Args:
        product_id: ID en WooCommerce

    Returns:
        Dict con datos del padre + lista de variaciones (id, sku, talla, calidad,
        precio, stock).
    """
    p = core.get_product(product_id)
    if not p:
        return {"error": f"Producto {product_id} no encontrado"}

    variaciones_raw = core.get_variations(product_id)
    variaciones = []
    for v in variaciones_raw:
        variaciones.append({
            "id": v["id"],
            "sku": v.get("sku"),
            "talla": core.get_talla(v),
            "calidad": core.get_calidad(v),
            "regular_price": v.get("regular_price"),
            "price": v.get("price"),
            "stock_quantity": v.get("stock_quantity"),
            "stock_status": v.get("stock_status"),
            "image_id": (v.get("image") or {}).get("id"),
        })

    return {
        "id": p["id"],
        "name": p["name"],
        "type": p.get("type"),
        "status": p["status"],
        "price": p.get("price"),
        "permalink": p.get("permalink"),
        "categories": [c["name"] for c in p.get("categories", [])],
        "atributos": [
            {"name": a["name"], "options": a.get("options", []), "variation": a.get("variation")}
            for a in p.get("attributes", [])
        ],
        "total_variaciones": len(variaciones),
        "variaciones": variaciones,
    }


def crear_producto(
    nombre_wc: str,
    categoria: str,
    tallas: list[str],
    calidad: Optional[str] = None,
    nombre_imagen: Optional[str] = None,
) -> dict:
    """Crea un producto variable padre en WooCommerce.

    Replica la lógica de scripts/b370_crear_producto.py pero como función pura.
    NO crea variaciones — para eso usa crear_variaciones() después.

    Si se pasa nombre_imagen, busca las imágenes en WP Media via SSH y asigna
    la principal al producto padre antes de crearlo.

    Args:
        nombre_wc: nombre que verá el cliente (ej "BARCELONA LOCAL 2026 1.1")
        categoria: nombre de categoría (ej "Barcelona", "Internacional")
        tallas: lista (ej ["S","M","L","XL","XXL"])
        calidad: opcional ("Tipo fan" / "Tipo jugador" / "1.1" / "Retro")
        nombre_imagen: opcional, prefijo del archivo en WP Media
                       (ej "BARCELONA-LOCAL-2026-1.1")

    Returns:
        Dict con id del producto creado o error.
    """
    # Verificar duplicado
    existing = core.product_exists(nombre_wc)
    if existing:
        return {
            "error": "Ya existe",
            "existing_id": existing,
            "tip": "Usa consultar_producto({existing_id}) para ver lo que hay"
        }

    # Buscar imágenes si aplica
    image_ids = []
    if nombre_imagen:
        image_ids = core.find_image_ids_by_name(nombre_imagen)
        if not image_ids:
            core.log.warning(f"Sin imágenes encontradas para '{nombre_imagen}'")

    # Categoría
    cat_id = core.get_or_create_category(categoria)

    # Atributos
    attrs = [{"name": "Tallas", "visible": True, "variation": True, "options": tallas}]
    if calidad:
        attrs.append({"name": "Calidad", "visible": True, "variation": True, "options": [calidad]})

    payload = {
        "name": nombre_wc,
        "type": "variable",
        "status": "publish",
        "categories": [{"id": cat_id}] if cat_id else [],
        "attributes": attrs,
    }
    if image_ids:
        payload["images"] = [{"id": image_ids[0]}]

    if core.DRY_RUN:
        return {
            "dry_run": True,
            "would_create": payload,
            "image_ids_found": image_ids,
        }

    r = core.wc_post("products", payload)
    if r.status_code not in (200, 201):
        core.log.error(f"crear_producto falló: {r.text[:200]}")
        return {"error": f"WC respondió {r.status_code}", "details": r.text[:200]}

    creado = r.json()
    core.log.info(f"Producto creado: {creado['id']} - {nombre_wc}")
    time.sleep(core.DELAY)

    return {
        "id": creado["id"],
        "name": creado["name"],
        "permalink": creado.get("permalink"),
        "image_ids": image_ids,
        "next_step": (
            f"Producto padre creado. Para variaciones: "
            f"crear_variaciones(product_id={creado['id']}, ...)"
        ),
    }
