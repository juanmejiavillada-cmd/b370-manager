#!/usr/bin/env python3
"""Agrega debug al override y hace el bypass más robusto."""
import os, sys, paramiko
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

HOST = os.getenv("SSH_HOST")
PORT = int(os.getenv("SSH_PORT", 22))
USER = os.getenv("SSH_USER")
PWD  = os.getenv("SSH_PASS")
MU   = f"/home/{USER}/domains/b370sports.com/public_html/wp-content/mu-plugins"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)
sftp = c.open_sftp()

def run(cmd):
    _, stdout, _ = c.exec_command(cmd)
    return stdout.read().decode("utf-8", errors="replace").strip()

# Test rápido: reemplazar todo el override con uno ultra-simple
# que usa múltiples estrategias de detección de página
SIMPLE_TEST = r"""<?php
/**
 * B370 Colombia Override — DEBUG VERSION
 */
if (!defined('ABSPATH')) exit;

// Estrategia 1: the_content filter con múltiples métodos de detección
add_filter('the_content', 'b370_col_inject_content', 999);

function b370_col_inject_content($content) {
    global $post;

    // Detectar por múltiples métodos
    $is_colombia = false;
    if (is_page(3294)) $is_colombia = true;
    if (isset($post) && $post->ID == 3294) $is_colombia = true;
    if (get_queried_object_id() == 3294) $is_colombia = true;

    if (!$is_colombia) return $content;

    return b370_colombia_full_html();
}

// Estrategia 2: template_redirect para mostrar el contenido correcto
add_action('template_redirect', function() {
    global $post;
    if (!isset($post) || $post->ID != 3294) return;

    // Agregar shortcode de emergencia en footer
    add_action('wp_footer', function() {
        echo '<script>
        // B370 Colombia Override — fallback JS
        if(window.location.pathname.indexOf("colombia-mundial") > -1) {
            var heroOld = document.querySelector(".wp-block-heading");
            if(heroOld && !document.querySelector(".b370-col-hero")) {
                console.log("B370: Override PHP no funciono, intentando JS override");
                // Marcar que el override PHP no funcionó
                document.title = "[DEBUG] " + document.title;
            }
        }
        </script>';
    });
});

// Estrategia 3: wp_head debug
add_action('wp_head', function() {
    global $post;
    if (!isset($post) || $post->ID != 3294) return;
    echo '<!-- B370-OVERRIDE-ACTIVE: post_id=' . $post->ID . ' is_page=' . (is_page(3294)?'YES':'NO') . ' -->';
}, 99);

function b370_colombia_full_html() {
    return '<div class="b370-col" style="border:5px solid red;padding:20px;background:yellow;">
    <h2 style="color:red;">B370 OVERRIDE ACTIVO — NUEVO DISEÑO CARGANDO</h2>
    <p>Si ves esto, el mu-plugin funciona. El diseño completo viene ahora...</p>
    </div>';
}
"""

print("Subiendo override de debug simplificado...")
with sftp.open(f"{MU}/b370-colombia-override.php", "wb") as f:
    f.write(SIMPLE_TEST.encode("utf-8"))
print("  OK")

# Validar PHP
out = run(f"php -l {MU}/b370-colombia-override.php 2>&1")
print(f"PHP syntax: {out}")

sftp.close()
c.close()
print("\nListo. Ahora en el browser:")
print("  1. Ve a https://b370sports.com/colombia-mundial-2026/")
print("  2. Ctrl+Shift+R (hard refresh)")
print("  3. Busca el cuadro ROJO/AMARILLO con el texto 'B370 OVERRIDE ACTIVO'")
print("  4. Mira el codigo fuente (Ctrl+U) y busca '<!-- B370-OVERRIDE-ACTIVE'")
