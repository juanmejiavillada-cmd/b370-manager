"""
Tool: quenti.

Importación del Excel de inventario de Quenti POS.
Cruza por SKU (código de barras) con variaciones de WC y actualiza stock.

Workflow real visto en data/CUENTI INVENTARIO 6 ABRIL.xlsx:
- Beto exporta inventario de Quenti como .xlsx
- Las columnas relevantes son nombre, codigo_barras (SKU), existencias
"""
from pathlib import Path
from typing import Optional

from b370_mcp import core


def importar_excel_quenti(
    ruta_archivo: str,
    product_ids: list[int],
    columna_sku: str = "codigo_barras",
    columna_stock: str = "existencias",
) -> dict:
    """Importa stock desde Excel de Quenti cruzando por SKU.

    Args:
        ruta_archivo: ruta al .xlsx (ej "data/CUENTI INVENTARIO 6 ABRIL.xlsx").
                     Acepta absoluto o relativo a la raíz del proyecto.
        product_ids: lista de productos WC a actualizar
        columna_sku: nombre de columna del SKU (default "codigo_barras")
        columna_stock: nombre de columna del stock (default "existencias")

    Returns:
        Dict con conteo de aplicadas, errores, sin SKU.
    """
    try:
        import pandas as pd
    except ImportError:
        return {"error": "Falta pandas. pip install pandas openpyxl"}

    # Resolver ruta
    p = Path(ruta_archivo)
    if not p.is_absolute():
        # Buscar relativo a la raíz del proyecto
        p = core.PROJECT_ROOT / ruta_archivo

    if not p.exists():
        return {
            "error": f"Archivo no encontrado: {p}",
            "tip": f"Ruta buscada: {p.absolute()}",
        }

    # Leer Excel
    try:
        df = pd.read_excel(p)
    except Exception as e:
        return {"error": f"No se pudo leer el Excel: {e}"}

    # Normalizar nombres de columna (lowercase, sin espacios)
    df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]

    if columna_sku not in df.columns:
        return {
            "error": f"Columna '{columna_sku}' no encontrada",
            "columnas_encontradas": list(df.columns),
        }
    if columna_stock not in df.columns:
        return {
            "error": f"Columna '{columna_stock}' no encontrada",
            "columnas_encontradas": list(df.columns),
        }

    # Construir stock_map: {sku: cantidad}
    df[columna_sku] = df[columna_sku].astype(str).str.strip()
    df[columna_stock] = (
        # Convertir a numérico, errores → 0, fillna(0), int
        df[columna_stock]
        .apply(lambda x: x if str(x).replace(".", "").replace("-", "").isdigit() else 0)
        .astype(float)
        .fillna(0)
        .astype(int)
    )
    df = df[df[columna_sku] != ""]
    df = df[df[columna_sku] != "nan"]

    stock_map = dict(zip(df[columna_sku], df[columna_stock]))

    # Delegar al tool de stock
    from b370_mcp.tools.stock import actualizar_stock_por_sku
    resultado = actualizar_stock_por_sku(stock_map, product_ids)

    # Enriquecer con info del Excel
    resultado["archivo_procesado"] = str(p)
    resultado["filas_excel"] = len(df)
    resultado["skus_unicos_excel"] = len(stock_map)

    return resultado


def importar_excel_quenti_simple(ruta_archivo: str) -> dict:
    """Versión exploratoria: solo lee el Excel y devuelve preview.

    No requiere product_ids — útil cuando recién recibes el archivo y quieres
    ver qué SKUs trae antes de cruzar con WC.

    Args:
        ruta_archivo: ruta al .xlsx

    Returns:
        Dict con preview de filas y SKUs únicos.
    """
    try:
        import pandas as pd
    except ImportError:
        return {"error": "Falta pandas. pip install pandas openpyxl"}

    p = Path(ruta_archivo)
    if not p.is_absolute():
        p = core.PROJECT_ROOT / ruta_archivo
    if not p.exists():
        return {"error": f"Archivo no encontrado: {p}"}

    try:
        df = pd.read_excel(p)
    except Exception as e:
        return {"error": f"Error leyendo Excel: {e}"}

    return {
        "archivo": str(p),
        "filas": len(df),
        "columnas": list(df.columns),
        "preview_5_filas": df.head(5).to_dict(orient="records"),
    }
