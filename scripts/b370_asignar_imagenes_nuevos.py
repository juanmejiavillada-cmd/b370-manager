#!/usr/bin/env python3
"""
B370 — Asignar imágenes a los 5 productos nuevos (abril 2026)
=============================================================
Busca los IDs de imagen en WordPress por nombre de archivo via SSH
y los asigna al producto padre y a cada variación.

Uso:
    python b370_asignar_imagenes_nuevos.py

Requisitos en .env:
    SSH_HOST, SSH_PORT, SSH_USER, SSH_PASS, SSH_PATH
"""

import os
import sys
import paramiko
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = int(os.getenv("SSH_PORT", 65002))
SSH_USER = os.getenv("SSH_USER")
SSH_PASS = os.getenv("SSH_PASS")
SSH_PATH = os.getenv("SSH_PATH", "~/domains/b370sports.com/public_html")


# ── MAPA DE PRODUCTOS ─────────────────────────────────────────────────────────
# producto_id  → ID del producto padre
# variaciones  → IDs de las 5 variaciones (S, M, L, XL, XXL)
# nombre_imagen → prefijo del archivo en wp-content/uploads
# ─────────────────────────────────────────────────────────────────────────────
PRODUCTOS = [
    {
        "nombre":        "BARCELONA 4A EQUIPACION TIPO ORIGINAL",
        "nombre_imagen": "BARCELONA-4-EQUIPACION-TIPO-ORIGINAL",
        "producto_id":   2349,
        "variaciones":   [2350, 2351, 2352, 2353, 2354],
    },
    {
        "nombre":        "RETRO PILSEN MEDELLIN",
        "nombre_imagen": "RETRO-PILSEN-MEDELLIN",
        "producto_id":   2356,
        "variaciones":   [2357, 2358, 2359, 2360, 2361],
    },
    {
        "nombre":        "MEDELLIN LOCAL 2026 TIPO FAN",
        "nombre_imagen": "MEDELLIN-LOCAL-2026-TIPO-FAN",
        "producto_id":   2362,
        "variaciones":   [2363, 2364, 2365, 2366, 2367],
    },
    {
        "nombre":        "RETRO KONGA MEDELLIN",
        "nombre_imagen": "RETRO-KONGA-MEDELLIN",
        "producto_id":   2368,
        "variaciones":   [2369, 2370, 2371, 2372, 2373],
    },
    {
        "nombre":        "CHAPECOENSE 1.1",
        "nombre_imagen": "CHAPECOENSE-1.1",
        "producto_id":   2374,
        "variaciones":   [2375, 2376, 2377, 2378, 2379],
    },
]


# ── SSH ───────────────────────────────────────────────────────────────────────

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER,
                   password=SSH_PASS, timeout=15)
    return client


def ssh_exec(client, cmd):
    _, stdout, _ = client.exec_command(f"cd {SSH_PATH} && {cmd}")
    return stdout.read().decode(errors="replace").strip()


def get_image_ids(client, nombre_imagen):
    """
    Busca IDs de imágenes filtrando por nombre de archivo en la URL (guid).
    Devuelve lista ordenada: IDs[0] = principal, IDs[1:] = galería.
    """
    cmd = (
        f'wp post list --post_type=attachment --fields=ID,guid '
        f'--format=csv --posts_per_page=9999 2>/dev/null '
        f'| grep -i "{nombre_imagen}"'
    )
    output = ssh_exec(client, cmd)
    ids = []
    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(",", 1)
        if parts[0].strip().isdigit():
            ids.append(int(parts[0].strip()))
    return sorted(ids)


def assign_images(client, producto):
    """Asigna _thumbnail_id y wavi_value al padre y a todas las variaciones."""
    nombre_imagen = producto["nombre_imagen"]
    producto_id   = producto["producto_id"]
    variaciones   = producto["variaciones"]

    image_ids = get_image_ids(client, nombre_imagen)
    if not image_ids:
        print(f"  ⚠️  No se encontraron imágenes para '{nombre_imagen}'")
        print(f"      Verifica que los archivos estén subidos como:")
        print(f"      {nombre_imagen}_1-scaled.jpg, {nombre_imagen}_2-scaled.jpg ...")
        return False

    main_id     = image_ids[0]
    gallery_ids = image_ids[1:]
    gallery_str = ",".join(str(i) for i in gallery_ids)

    print(f"  📷 Principal : ID {main_id}")
    if gallery_ids:
        print(f"  🖼️  Galería   : {gallery_str}")

    # Producto padre
    ssh_exec(client, f"wp post meta update {producto_id} _thumbnail_id {main_id}")
    print(f"  ✅ Padre ({producto_id}) → _thumbnail_id asignado")

    # Variaciones
    for vid in variaciones:
        ssh_exec(client, f"wp post meta update {vid} _thumbnail_id {main_id}")
        if gallery_str:
            ssh_exec(client, f"wp post meta update {vid} wavi_value '{gallery_str}'")

    print(f"  ✅ {len(variaciones)} variaciones → _thumbnail_id"
          + (" + wavi_value" if gallery_str else "") + " asignados")
    return True


# ── PROCESO PRINCIPAL ─────────────────────────────────────────────────────────

def main():
    print("\n" + "="*62)
    print("  B370 — ASIGNAR IMÁGENES A PRODUCTOS NUEVOS (ABRIL 2026)")
    print("="*62)

    print("\n🔌 Conectando a servidor SSH...")
    try:
        client = ssh_connect()
        print("  ✅ Conectado")
    except Exception as e:
        print(f"  ❌ Error SSH: {e}")
        input("\n  Presiona ENTER para cerrar...")
        return

    ok_count  = 0
    err_count = 0

    for producto in PRODUCTOS:
        print(f"\n{'─'*62}")
        print(f"  🟡 {producto['nombre']}")
        try:
            ok = assign_images(client, producto)
            if ok:
                ok_count += 1
            else:
                err_count += 1
        except Exception as e:
            print(f"  ❌ Error inesperado: {e}")
            err_count += 1

    client.close()

    print(f"\n{'='*62}")
    print("  RESUMEN")
    print(f"{'='*62}")
    print(f"  ✅ Con imágenes asignadas : {ok_count}")
    if err_count:
        print(f"  ⚠️  Sin imágenes (pendiente): {err_count}")
    print("="*62)
    input("\n  Presiona ENTER para cerrar...")


if __name__ == "__main__":
    main()
