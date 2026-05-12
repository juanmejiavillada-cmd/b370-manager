"""
B370 CLI — punto de entrada.

Subcomandos disponibles (todos read-only en esta versión):

    python cli.py ping
        Verifica conexión y autenticación contra b370sports.com.

    python cli.py list-products
        Lista todos los productos variables (id, nombre, nº de variaciones).

    python cli.py product <id>
        Detalle de un producto: atributos + variaciones existentes.

    python cli.py size-options
        Lista las tallas que existen actualmente en el atributo Tallas de WC.

    python cli.py parse-quenti [ruta.xlsx]
        Parsea el inventario de Quenti y muestra resumen + tallas nuevas
        + variaciones sin calidad (las que requieren confirmación de Beto).

    python cli.py family <substring>
        Busca familias parseadas cuyo nombre base contenga <substring>.
        Útil para inspeccionar qué hay en Quenti para un producto específico.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

# Forzar UTF-8 en stdout/stderr — la consola de Windows usa cp1252 por defecto
# y muere ante cualquier emoji o tilde. Reconfigurable desde Python 3.7.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, Exception):
    pass

import wc
import quenti
from config import QUENTI_DEFAULT_XLSX


def _print_table(rows: list[list[str]], headers: list[str]) -> None:
    if not rows:
        print("(sin filas)")
        return
    widths = [len(h) for h in headers]
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], len(str(c)))
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print(fmt.format(*[str(c) for c in r]))


def cmd_ping(_: argparse.Namespace) -> int:
    try:
        data = wc.ping()
    except wc.WCError as e:
        print(f"❌ Error de autenticación o red: {e}")
        return 1
    env = (data or {}).get("environment", {})
    settings = (data or {}).get("settings", {})
    print("✅ Conexión OK con b370sports.com")
    print(f"   WC version:    {env.get('version', '?')}")
    print(f"   WP version:    {env.get('wp_version', '?')}")
    print(f"   PHP version:   {env.get('php_version', '?')}")
    print(f"   Currency:      {settings.get('currency', '?')}")
    return 0


def cmd_list_products(_: argparse.Namespace) -> int:
    try:
        products = wc.list_variable_products()
    except wc.WCError as e:
        print(f"❌ {e}")
        return 1
    print(f"Productos variables encontrados: {len(products)}")
    rows = []
    for p in products:
        rows.append([
            str(p.get("id", "")),
            (p.get("name", "") or "")[:60],
            str(len(p.get("variations") or [])),
        ])
    _print_table(rows, ["ID", "Nombre", "Var."])
    return 0


def cmd_product(args: argparse.Namespace) -> int:
    pid = args.id
    try:
        prod = wc.get_product(pid)
        variations = wc.list_variations(pid)
    except wc.WCError as e:
        print(f"❌ {e}")
        return 1
    print(f"#{prod.get('id')} — {prod.get('name')}")
    print(f"   status:    {prod.get('status')}")
    print(f"   permalink: {prod.get('permalink')}")
    print(f"   atributos:")
    for a in prod.get("attributes") or []:
        opts = a.get("options") or []
        print(f"     - {a.get('name')}: {', '.join(map(str, opts))}")
    print(f"\nVariaciones ({len(variations)}):")
    rows = []
    for v in variations:
        attrs = " / ".join(f"{a.get('name')}={a.get('option')}" for a in (v.get("attributes") or []))
        rows.append([
            str(v.get("id", "")),
            attrs[:50],
            (v.get("sku") or "")[:18],
            str(v.get("price") or ""),
            str(v.get("stock_quantity") if v.get("stock_quantity") is not None else "—"),
        ])
    _print_table(rows, ["ID", "Atributos", "SKU", "Precio", "Stock"])
    return 0


def cmd_size_options(_: argparse.Namespace) -> int:
    try:
        terms = wc.get_size_attribute_options()
    except wc.WCError as e:
        print(f"❌ {e}")
        return 1
    if not terms:
        print("⚠ No encontré atributo Tallas. ¿Existe en WC → Productos → Atributos?")
        return 1
    print(f"Tallas configuradas en WooCommerce ({len(terms)}):")
    for t in terms:
        print(f"  - {t}")
    return 0


def cmd_parse_quenti(args: argparse.Namespace) -> int:
    path = args.path or QUENTI_DEFAULT_XLSX
    print(f"Leyendo {path} ...")
    try:
        rows = quenti.parse_xlsx(path)
    except FileNotFoundError:
        print(f"❌ No existe el archivo: {path}")
        return 1
    families = quenti.group_by_family(rows)
    sin_calidad = [r for r in rows if r["calidad"] is None]
    nuevas_tallas = quenti.detect_new_sizes(rows)

    print(f"\nFilas parseadas:    {len(rows)}")
    print(f"Familias únicas:    {len(families)}")
    print(f"Sin calidad:        {len(sin_calidad)}  (requieren asignación manual de Beto)")
    print(f"Tallas nuevas:      {sorted(nuevas_tallas) if nuevas_tallas else '(ninguna)'}")
    print()
    print("Top 10 familias por cantidad de variaciones:")
    top = sorted(families.values(), key=lambda f: -len(f["variaciones"]))[:10]
    for f in top:
        print(f"  [{f['tipo']:8}] {f['base']}  → {len(f['variaciones'])} var.")

    if nuevas_tallas:
        print()
        print("⚠ Estas tallas existen en Quenti pero NO en WooCommerce todavía:")
        for t in sorted(nuevas_tallas):
            count = sum(1 for r in rows if r["talla"] == t)
            print(f"   - {t}  ({count} filas)")
        print("   El comando que cree variaciones pedirá confirmación antes de crearlas.")
    return 0


def cmd_family(args: argparse.Namespace) -> int:
    path = args.path or QUENTI_DEFAULT_XLSX
    needle = args.substring.upper()
    rows = quenti.parse_xlsx(path)
    families = quenti.group_by_family(rows)
    matches = [f for f in families.values() if needle in f["base"].upper()]
    if not matches:
        print(f"(sin coincidencias para '{needle}')")
        return 0
    print(f"Familias que contienen '{needle}': {len(matches)}\n")
    for f in matches:
        print(f"[{f['tipo']}] {f['base']}  ({len(f['variaciones'])} var.)")
        rows_v = []
        for v in f["variaciones"]:
            rows_v.append([
                v["calidad"] or "—",
                v["acabado"],
                v["talla"],
                v["sku"],
                str(v["stock"]),
                str(v["precio"]),
            ])
        _print_table(rows_v, ["Calidad", "Acabado", "Talla", "SKU", "Stock", "Precio"])
        print()
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="b370-cli", description="CLI de gestión del catálogo B370.")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("ping", help="Verifica conexión y auth contra b370sports.com")
    sub.add_parser("list-products", help="Lista productos variables de la tienda")

    p_prod = sub.add_parser("product", help="Detalle de un producto + variaciones")
    p_prod.add_argument("id", type=int)

    sub.add_parser("size-options", help="Lista las tallas configuradas en el atributo Tallas")

    p_parse = sub.add_parser("parse-quenti", help="Parsea el Excel de Quenti")
    p_parse.add_argument("path", nargs="?", default=None)

    p_fam = sub.add_parser("family", help="Busca familias en Quenti por substring del nombre")
    p_fam.add_argument("substring")
    p_fam.add_argument("--path", default=None)

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0

    handlers = {
        "ping":         cmd_ping,
        "list-products": cmd_list_products,
        "product":      cmd_product,
        "size-options": cmd_size_options,
        "parse-quenti": cmd_parse_quenti,
        "family":       cmd_family,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
