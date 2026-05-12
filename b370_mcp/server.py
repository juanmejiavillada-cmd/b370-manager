"""
B370 Manager — MCP Server
=========================

Expone las operaciones de catálogo y stock de B370 Línea Deportiva a Claude
(Desktop / Code) vía Model Context Protocol.

Comparte código con los scripts CLI existentes (mismo .env, mismo wc client).
Los scripts en scripts/ siguen funcionando para batch jobs grandes.
El MCP es para conversación con Claude.

Uso:
    python mcp/server.py             # corre como MCP server stdio
    npx @modelcontextprotocol/inspector python mcp/server.py   # debug UI

Configuración en claude_desktop_config.json:
{
  "mcpServers": {
    "b370-ecommerce": {
      "command": "C:\\path\\to\\B370-MANAGER\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\B370-MANAGER\\mcp\\server.py"]
    }
  }
}
"""
import sys
from pathlib import Path

# Permitir imports relativos al proyecto cuando se corre desde Claude Desktop
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastmcp import FastMCP

from b370_mcp import core
from b370_mcp.tools import productos, variaciones, stock, precios, imagenes, quenti, copys, pedidos


# ============================================================================
mcp = FastMCP("b370-ecommerce")
core.log.info(f"b370-ecommerce-mcp arrancando · DRY_RUN={core.DRY_RUN}")


# ============================================================================
# RESOURCES — contexto de solo lectura para Claude
# ============================================================================

@mcp.resource("b370://config/dry-run")
def res_dry_run() -> str:
    """Estado del modo dry-run."""
    estado = "ACTIVO (escrituras solo simulan)" if core.DRY_RUN else "DESACTIVADO (escrituras a producción)"
    return f"DRY_RUN: {estado}\n\nPara cambiar: edita B370_DRY_RUN en .env y reinicia Claude Desktop."


@mcp.resource("b370://catalog/precios-default")
def res_precios() -> str:
    """Estructura oficial de precios B370."""
    lines = ["Estructura oficial de precios B370 (COP):", ""]
    for calidad, precio in core.PRECIOS_DEFAULT.items():
        lines.append(f"- {calidad}: ${precio:,.0f}".replace(",", "."))
    lines.append("")
    lines.append(f"Bandas validadas: ${core.PRICE_MIN:,.0f} – ${core.PRICE_MAX:,.0f}".replace(",", "."))
    return "\n".join(lines)


@mcp.resource("b370://catalog/atributos")
def res_atributos() -> str:
    """Convención de atributos en WooCommerce de B370."""
    return """Atributos usados en WooCommerce de B370:

- "Tallas" (plural) → opciones: S, M, L, XL, XXL
- "Calidad" → opciones: "Tipo fan", "Tipo jugador", "1.1", "Retro"
  · Nota: "Tipo jugador" se está migrando a "Tipo original" (script normalizar_calidad)
- "Color" → cuando aplique (ej Verde, Blanca, Negra para Retro Sam Atlético Nacional)
- "Tipo" → cuando aplique (ej Azul, Blanca para polos)

IMPORTANTE: cuando un producto NO tiene atributo "Calidad", las herramientas
de actualización masiva por calidad usan la key Python `None` para esas
variaciones. Ej: precios_por_calidad={None: 120000} aplica precio único."""


# ============================================================================
# TOOLS — Lectura
# ============================================================================

@mcp.tool()
def listar_productos(busqueda: str | None = None, categoria: str | None = None, per_page: int = 50) -> list[dict]:
    """Lista productos publicados de B370.

    Úsalo cuando necesites encontrar el ID de un producto, o ver el catálogo.

    Args:
        busqueda: texto a buscar en el nombre (opcional)
        categoria: nombre de categoría (opcional, ej "Barcelona", "Medellín")
        per_page: máximo de resultados
    """
    return productos.listar_productos(busqueda, categoria, per_page)


@mcp.tool()
def consultar_producto(product_id: int) -> dict:
    """Detalle completo de un producto + sus variaciones.

    Devuelve precios, stock, SKUs, atributos. Úsalo antes de modificar
    cualquier cosa para validar el estado actual.
    """
    return productos.consultar_producto(product_id)


@mcp.tool()
def consultar_stock(product_id: int) -> dict:
    """Stock de todas las variaciones de un producto.

    Útil para responder "¿qué tallas hay disponibles de X?"
    """
    return stock.consultar_stock(product_id)


@mcp.tool()
def buscar_imagenes_wp(nombre_imagen: str) -> dict:
    """Busca imágenes en WP Media por prefijo del nombre de archivo.

    Ej: nombre_imagen="BARCELONA-LOCAL-2026" devuelve los IDs de
    todas las imágenes que empiecen con ese prefijo, ordenadas
    (la primera es la imagen principal).

    Requiere SSH configurado en .env.
    """
    return imagenes.buscar_imagenes_wp(nombre_imagen)


# ============================================================================
# TOOLS — Creación
# ============================================================================

@mcp.tool()
def crear_producto(
    nombre_wc: str,
    categoria: str,
    tallas: list[str],
    calidad: str | None = None,
    nombre_imagen: str | None = None,
) -> dict:
    """Crea un producto variable padre en WooCommerce.

    Si pasas nombre_imagen, busca las imágenes en WP Media y asigna la
    principal al producto padre. Las variaciones se crean después con
    crear_variaciones().

    Args:
        nombre_wc: nombre que verá el cliente
        categoria: ej "Barcelona", "Medellín", "Internacional"
        tallas: ej ["S","M","L","XL","XXL"]
        calidad: opcional ("Tipo fan" / "Tipo jugador" / "1.1" / "Retro")
        nombre_imagen: opcional, prefijo del archivo en WP Media
    """
    return productos.crear_producto(nombre_wc, categoria, tallas, calidad, nombre_imagen)


@mcp.tool()
def crear_variaciones(
    product_id: int,
    tallas: list[str],
    calidad: str | None = None,
    skus: dict | None = None,
    stock_por_talla: dict | None = None,
    precio: float | None = None,
    asignar_imagenes: bool = True,
    nombre_imagen: str | None = None,
) -> dict:
    """Crea variaciones (talla × calidad) con SKU, stock y precio.

    Si pasas calidad y NO pasas precio, usa el precio default según
    la estructura oficial B370 (Tipo fan $80k, Tipo jugador $110k, 1.1 $120k).

    Si pasas asignar_imagenes=True y nombre_imagen, asigna principal +
    galería completa (vía SSH + WP-CLI) a cada variación creada.

    Args:
        product_id: ID del producto padre
        tallas: ej ["S","M","L","XL","XXL"]
        calidad: opcional
        skus: opcional, dict {talla: sku}
        stock_por_talla: opcional, dict {talla: cantidad}
        precio: opcional, override del precio default
        asignar_imagenes: True para asignar imágenes (requiere SSH)
        nombre_imagen: prefijo del archivo en WP Media
    """
    return variaciones.crear_variaciones(
        product_id, tallas, calidad,
        skus=skus, stock=stock_por_talla, precio=precio,
        asignar_imagenes=asignar_imagenes, nombre_imagen=nombre_imagen,
    )


@mcp.tool()
def recrear_variaciones_producto(product_id: int, plan: dict) -> dict:
    """ELIMINA todas las variaciones de un producto y las recrea desde cero.

    Útil para corregir SKUs o reestructurar atributos sin tocar el producto padre.

    Args:
        product_id: ID del producto padre
        plan: estructura
            {
                "attr2_name": "Calidad" | "Color" | "Tipo" | None,
                "data": {
                    "Tipo fan": {"S": "sku1", "M": "sku2", ...},
                    "Tipo jugador": {"S": "sku3", ...}
                }
            }
            Si no hay segundo atributo: {"attr2_name": None, "data": {None: {"S": "sku1"...}}}
    """
    return variaciones.recrear_variaciones_producto(product_id, plan)


# ============================================================================
# TOOLS — Actualización
# ============================================================================

@mcp.tool()
def actualizar_stock_variacion(product_id: int, variation_id: int, nuevo_stock: int) -> dict:
    """Actualiza stock de UNA variación específica.

    Para cargas masivas desde Quenti, usa importar_excel_quenti.
    """
    return stock.actualizar_stock_variacion(product_id, variation_id, nuevo_stock)


@mcp.tool()
def actualizar_stock_por_sku(stock_map: dict, product_ids: list[int]) -> dict:
    """Actualiza stock masivamente cruzando SKU.

    Replica scripts/b370_actualizar_stock.py: para cada variación cuyo SKU
    esté en stock_map, asigna el stock correspondiente.

    Args:
        stock_map: dict {sku: cantidad}, ej {"2100002004204": 1, "2100000754705": 3}
        product_ids: lista de productos a procesar (limita scope para no
                     escanear toda la tienda)
    """
    return stock.actualizar_stock_por_sku(stock_map, product_ids)


@mcp.tool()
def actualizar_precio_variacion(product_id: int, variation_id: int, nuevo_precio: float) -> dict:
    """Actualiza precio de UNA variación específica.

    El precio se valida contra B370_PRICE_MIN y B370_PRICE_MAX.
    """
    return precios.actualizar_precio_variacion(product_id, variation_id, nuevo_precio)


@mcp.tool()
def actualizar_precios_por_calidad(product_id: int, precios_por_calidad: dict) -> dict:
    """Actualiza precios por valor de "Calidad" en un producto.

    Args:
        product_id: ID del producto
        precios_por_calidad: dict {valor_calidad: precio}
                             ej {"Tipo fan": 80000, "1.1": 120000}
                             Si producto NO tiene atributo Calidad: {None: 120000}
    """
    return precios.actualizar_precios_por_calidad(product_id, precios_por_calidad)


@mcp.tool()
def actualizar_precios_multi_producto(plan: dict) -> dict:
    """Actualiza precios en MÚLTIPLES productos en una sola operación.

    Replica el patrón PRODUCT_PRICES de scripts/b370_actualizar_precios.py.

    Args:
        plan: dict
            {
                product_id: {
                    "attr": "Calidad" | None,
                    "precios": {"1.1": 120000, "Tipo jugador": 110000}
                              o {None: 120000}
                }, ...
            }
    """
    return precios.actualizar_precios_multi_producto(plan)


# ============================================================================
# TOOLS — Imágenes
# ============================================================================

@mcp.tool()
def asignar_imagen_variacion_rest(product_id: int, variation_id: int, image_id: int) -> dict:
    """Asigna SOLO imagen principal de una variación vía REST API.

    Para galería completa (wavi_value) usa asignar_imagenes_completas.
    """
    return imagenes.asignar_imagen_variacion_rest(product_id, variation_id, image_id)


@mcp.tool()
def asignar_imagenes_por_atributo(product_id: int, attr: str, imagenes_por_valor: dict) -> dict:
    """Asigna imagen principal por valor de atributo (Color/Tipo).

    Args:
        product_id: ID del producto
        attr: nombre del atributo (ej "Color", "Tipo")
        imagenes_por_valor: dict {valor: image_id}
                            ej {"Verde": 1783, "Blanca": 1776, "Negra": 1812}
    """
    return imagenes.asignar_imagenes_por_atributo(product_id, attr, imagenes_por_valor)


@mcp.tool()
def asignar_imagenes_completas(product_id: int, variation_ids: list[int], nombre_imagen: str) -> dict:
    """Asigna imagen principal + galería completa via SSH + WP-CLI.

    Esta es la operación principal: busca todos los archivos cuyo nombre
    empiece con `nombre_imagen`, asigna el menor ID como principal y los
    demás como galería (wavi_value) al producto padre y todas las variaciones.

    Requiere SSH configurado.

    Args:
        product_id: ID del producto padre
        variation_ids: lista de IDs de variaciones
        nombre_imagen: prefijo del archivo (ej "BARCELONA-LOCAL-2026-1.1")
    """
    return imagenes.asignar_imagenes_completas(product_id, variation_ids, nombre_imagen)


# ============================================================================
# TOOLS — Quenti
# ============================================================================

@mcp.tool()
def importar_excel_quenti_preview(ruta_archivo: str) -> dict:
    """Lee un Excel de Quenti y devuelve preview SIN aplicar nada.

    Útil cuando recibes el archivo y quieres ver columnas/filas antes de cruzar.

    Args:
        ruta_archivo: ruta absoluta o relativa al proyecto
                      (ej "data/CUENTI INVENTARIO 6 ABRIL.xlsx")
    """
    return quenti.importar_excel_quenti_simple(ruta_archivo)


@mcp.tool()
def importar_excel_quenti(
    ruta_archivo: str,
    product_ids: list[int],
    columna_sku: str = "codigo_barras",
    columna_stock: str = "existencias",
) -> dict:
    """Importa stock desde Excel de Quenti cruzando por SKU.

    Workflow:
    1. Beto te pasa el .xlsx de Quenti
    2. Tú lo metes en data/ del proyecto
    3. Llamas esto con la lista de product_ids a actualizar
    4. La tool cruza SKUs y actualiza stock_quantity en WC

    Args:
        ruta_archivo: ej "data/CUENTI INVENTARIO 6 ABRIL.xlsx"
        product_ids: lista de productos WC a actualizar
        columna_sku: nombre exacto de la columna (default "codigo_barras")
        columna_stock: nombre exacto de la columna (default "existencias")
    """
    return quenti.importar_excel_quenti(ruta_archivo, product_ids, columna_sku, columna_stock)


# ============================================================================
# TOOLS — Pedidos y métricas
# ============================================================================

@mcp.tool()
def listar_pedidos(dias: int = 7, estado: str = "any") -> dict:
    """Lista pedidos de los últimos N días con resumen por pedido.

    Args:
        dias: ventana de tiempo hacia atrás (default 7)
        estado: "processing", "completed" o "any"
    """
    return pedidos.listar_pedidos(dias, estado)


@mcp.tool()
def metricas_ventas_periodo(dias: int = 7) -> dict:
    """Métricas de ventas agregadas: top productos, ventas por calidad, ticket promedio.

    Úsalo para el reporte semanal o para saber qué está vendiendo.

    Args:
        dias: ventana de tiempo (default 7)
    """
    return pedidos.metricas_ventas_periodo(dias)


# ============================================================================
# TOOLS — Copys
# ============================================================================

@mcp.tool()
def generar_copy_producto(
    nombre_producto: str,
    equipo: str,
    temporada: str = "2026",
    calidades_disponibles: list[str] | None = None,
    persona_objetivo: str = "premium",
) -> dict:
    """Genera copy de producto siguiendo voice-tone B370.

    Lee voice-tone.md y buyer-personas.md del repo b370-brand-context
    automáticamente. Devuelve title_seo, description_short, description_long,
    bullets y cta. NO escribe a WC — solo devuelve el copy.

    Requiere ANTHROPIC_API_KEY y B370_BRAND_REPO en .env.
    """
    return copys.generar_copy_producto(
        nombre_producto, equipo, temporada, calidades_disponibles, persona_objetivo,
    )


@mcp.tool()
def actualizar_copy_en_wc(product_id: int, copy_dict: dict) -> dict:
    """Aplica copy aprobado a un producto en WooCommerce.

    Actualiza: name (title_seo), short_description, description (con bullets y CTA).
    Respeta DRY_RUN — si está activo solo simula.

    Args:
        product_id: ID del producto en WooCommerce
        copy_dict: dict con title_seo, description_short, description_long,
                   bullets (list), cta (str)
    """
    return copys.actualizar_copy_en_wc(product_id, copy_dict)


# ============================================================================
# PROMPTS — slash commands para Claude
# ============================================================================

@mcp.prompt()
def lanzar_producto_completo(equipo: str, temporada: str = "2026") -> str:
    """Workflow guiado para lanzar un producto nuevo de cero a publicado."""
    return f"""Voy a lanzar un producto nuevo de B370: **{equipo} {temporada}**.

Sigue este workflow respetando las convenciones del proyecto:

1. Lee b370://catalog/precios-default y b370://catalog/atributos para alinearte.
2. Pregúntame:
   - Nombre exacto que verá el cliente (formato MAYÚSCULAS, ej "BARCELONA LOCAL 2026 1.1")
   - Categoría (Barcelona, Medellín, Internacional, Selecciones, etc.)
   - Tallas disponibles
   - Calidades (Tipo fan / Tipo jugador / 1.1 / Retro o ninguna)
   - SKUs por talla (códigos de barras de Quenti)
   - Stock por talla
   - Prefijo del nombre de archivo de imágenes en WP Media
3. Llama crear_producto() con esos datos.
4. Llama crear_variaciones() pasando skus, stock_por_talla, asignar_imagenes=True.
5. Pregúntame si quiero generar el copy con generar_copy_producto().
6. Resume: producto creado, variaciones, imágenes asignadas, copy listo.

IMPORTANTE: si DRY_RUN está activo (revisa b370://config/dry-run), avísame al final
que para aplicar de verdad debo cambiar B370_DRY_RUN=false en .env."""


@mcp.prompt()
def auditar_producto(product_id: int) -> str:
    """Audita un producto: precios, stock, copy, imágenes, atributos."""
    return f"""Audita el producto ID {product_id} y dime qué está bien y qué falta:

1. Llama consultar_producto({product_id}) y revisa:
   - ¿Tiene categoría asignada?
   - ¿Atributos están bien? ("Tallas" plural, "Calidad" si aplica)
   - ¿Cuántas variaciones tiene?
2. Llama consultar_stock({product_id}) y revisa:
   - ¿Cuántas variaciones tienen stock 0?
   - ¿Cuántas tienen SKU vacío?
3. Compara precios contra b370://catalog/precios-default:
   - ¿Cada calidad tiene el precio estándar?
   - ¿Hay precios fuera de bandas?
4. Devuelve un checklist con ✅/❌ y propón comandos concretos para
   las correcciones (sin ejecutarlos hasta que yo confirme)."""


@mcp.prompt()
def cargar_inventario_quenti(ruta_excel: str) -> str:
    """Workflow para procesar un nuevo inventario de Quenti."""
    return f"""Voy a cargar el inventario de Quenti desde: {ruta_excel}

1. Llama importar_excel_quenti_preview() para ver qué trae el archivo.
2. Confírmame:
   - Columnas detectadas (¿está "codigo_barras" y "existencias"?)
   - Cantidad de filas
   - Preview de las primeras 5 filas
3. Pregúntame qué product_ids debo actualizar (puede ser una lista grande).
4. Llama importar_excel_quenti() con esos IDs.
5. Si DRY_RUN está activo, muéstrame el plan y pregúntame si aplico de verdad.
6. Reporta: cuántas variaciones se actualizaron, cuántos SKUs no encontraron match."""


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    core.log.info("MCP server listo · transport=stdio")
    mcp.run()
