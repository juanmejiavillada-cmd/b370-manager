"""
Tool: imagenes.

Asignación de imágenes a variaciones. Combina REST API (image principal)
con SSH + WP-CLI (galería vía wavi_value).

Replica scripts/b370_imagenes_variaciones.py y b370_asignar_imagenes_nuevos.py.
"""
import time
from typing import Optional

from b370_mcp import core


def buscar_imagenes_wp(nombre_imagen: str) -> dict:
    """Busca imágenes en la biblioteca de WP que coincidan con un prefijo.

    Útil cuando subes archivos con convención NOMBRE_1.jpg, NOMBRE_2.jpg, etc.
    y necesitas saber qué IDs les asignó WP.

    Args:
        nombre_imagen: prefijo a buscar (ej "BARCELONA-LOCAL-2026-1.1")

    Returns:
        Dict con IDs encontrados (ordenados, principal primero).
    """
    ids = core.find_image_ids_by_name(nombre_imagen)
    if not ids:
        return {
            "encontradas": 0,
            "tip": (
                f"No se encontraron imágenes con el patrón '{nombre_imagen}'. "
                f"Verifica que estén subidas en WP Media con ese prefijo en el nombre."
            ),
        }
    return {
        "encontradas": len(ids),
        "principal_id": ids[0],
        "galeria_ids": ids[1:],
        "todos_los_ids": ids,
    }


def asignar_imagen_variacion_rest(
    product_id: int,
    variation_id: int,
    image_id: int,
) -> dict:
    """Asigna SOLO la imagen principal de una variación via REST API.

    Para galería completa (wavi_value) usa asignar_imagenes_completas.

    Args:
        product_id: ID del producto padre
        variation_id: ID de la variación
        image_id: ID de WP Media de la imagen
    """
    payload = {"image": {"id": image_id}}

    if core.DRY_RUN:
        return {"dry_run": True, "would_assign": {"variation_id": variation_id, "image_id": image_id}}

    r = core.wc_put(f"products/{product_id}/variations/{variation_id}", payload)
    if r.status_code != 200:
        return {"error": f"WC respondió {r.status_code}", "details": r.text[:150]}
    v = r.json()
    return {
        "variation_id": variation_id,
        "image_id_asignado": (v.get("image") or {}).get("id"),
        "image_src": (v.get("image") or {}).get("src"),
    }


def asignar_imagenes_por_atributo(
    product_id: int,
    attr: str,
    imagenes_por_valor: dict[str, int],
) -> dict:
    """Asigna imagen principal por valor de atributo (Color/Tipo).

    Replica scripts/b370_imagenes_variaciones.py exactamente.

    Args:
        product_id: ID del producto padre
        attr: nombre del atributo (ej "Color", "Tipo")
        imagenes_por_valor: dict {valor: image_id}
                            ej {"Verde": 1783, "Blanca": 1776, "Negra": 1812}

    Returns:
        Dict con resumen.
    """
    variaciones = core.get_variations(product_id)
    if not variaciones:
        return {"error": f"Sin variaciones para {product_id}"}

    plan = []
    for v in variaciones:
        attrs = core.extract_variation_attrs(v)
        valor = attrs.get(attr)
        if not valor or valor not in imagenes_por_valor:
            continue
        plan.append({
            "variation_id": v["id"],
            "talla": attrs.get("Tallas") or attrs.get("Talla"),
            "valor_atributo": valor,
            "image_id": imagenes_por_valor[valor],
        })

    if core.DRY_RUN:
        return {"dry_run": True, "asignaria": len(plan), "preview": plan}

    ok = err = 0
    for item in plan:
        r = core.wc_put(
            f"products/{product_id}/variations/{item['variation_id']}",
            {"image": {"id": item["image_id"]}},
        )
        if r.status_code == 200:
            ok += 1
        else:
            err += 1
        time.sleep(core.DELAY)

    core.log.info(f"Imágenes por {attr} en #{product_id}: {ok} ok, {err} err")
    return {"product_id": product_id, "attr": attr, "asignadas": ok, "errores": err}


def asignar_imagenes_completas(
    product_id: int,
    nombre_imagen: str,
    variation_ids: Optional[list[int]] = None,
) -> dict:
    """Asigna imagen principal + galería completa via SSH + WP-CLI.

    Busca archivos cuyo nombre empiece con `nombre_imagen`, ordena por ID
    (el menor es principal), y asigna `_thumbnail_id` + `wavi_value`.

    Cuándo pasar variation_ids:
    - Producto con múltiples visuales (Calidad/Color distintos) → pasar los IDs
      de las variaciones que corresponden a cada visual.
    - Producto con solo Tallas (un único visual) → omitir o pasar lista vacía.
      WooCommerce usa la imagen del padre como fallback para todas las tallas,
      así que no hay que repetir la operación N veces.

    Args:
        product_id: ID del producto padre (siempre recibe la imagen)
        nombre_imagen: prefijo del archivo (ej "BARCELONA-LOCAL-2026-1.1")
        variation_ids: variaciones que también deben recibir la imagen.
                       None o [] → solo se asigna al producto padre.
    """
    image_ids = core.find_image_ids_by_name(nombre_imagen)
    if not image_ids:
        return {
            "error": f"No se encontraron imágenes con prefijo '{nombre_imagen}'",
            "tip": "Verifica que las imágenes estén subidas a WP Media",
        }

    main_id = image_ids[0]
    gallery_ids = image_ids[1:]
    variation_ids = variation_ids or []

    if core.DRY_RUN:
        return {
            "dry_run": True,
            "principal_id": main_id,
            "galeria_ids": gallery_ids,
            "asignaria_a_padre": product_id,
            "asignaria_a_variaciones": variation_ids,
            "nota": "Solo padre" if not variation_ids else f"{len(variation_ids)} variaciones",
        }

    # Asignar a padre siempre
    core.assign_image_meta_via_ssh(product_id, main_id, gallery_ids)

    # Asignar a variaciones solo si se pasan explícitamente
    asignadas = 0
    for vid in variation_ids:
        if core.assign_image_meta_via_ssh(vid, main_id, gallery_ids):
            asignadas += 1

    return {
        "product_id": product_id,
        "principal_id": main_id,
        "galeria_count": len(gallery_ids),
        "variaciones_asignadas": asignadas,
        "nota": "Solo padre — todas las tallas usan esta imagen como fallback" if not variation_ids else "",
    }
