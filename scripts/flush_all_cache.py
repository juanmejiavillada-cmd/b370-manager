#!/usr/bin/env python3
"""Flush completo: object cache + transients + LiteSpeed + verificación."""
import os, sys, paramiko
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

HOST = os.getenv("SSH_HOST")
PORT = int(os.getenv("SSH_PORT", 22))
USER = os.getenv("SSH_USER")
PWD  = os.getenv("SSH_PASS")
WP   = f"/home/{USER}/domains/b370sports.com/public_html"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)

php = r"""<?php
$_SERVER['HTTP_HOST'] = 'b370sports.com';
$_SERVER['REQUEST_URI'] = '/';
define('ABSPATH', '/home/u122447978/domains/b370sports.com/public_html/');
require '/home/u122447978/domains/b370sports.com/public_html/wp-load.php';

// 1. Flush object cache (Redis/Memcached/APCu)
wp_cache_flush();
echo "1. Object cache flushed\n";

// 2. Delete all transients
global $wpdb;
$n = $wpdb->query("DELETE FROM $wpdb->options WHERE option_name LIKE '_transient_%'");
echo "2. Transients eliminados: $n filas\n";

// 3. LiteSpeed: trigger purge via actions
do_action('litespeed_purge_all');
do_action('litespeed_purge_post', 3294);
echo "3. LiteSpeed purge action disparado\n";

// 4. LiteSpeed: set header para purge (si el server lo escucha)
if(function_exists('LiteSpeed_Cache_API::purge_post')) {
    LiteSpeed_Cache_API::purge_post(3294);
    echo "4. LiteSpeed API purge_post llamado\n";
} else {
    echo "4. LiteSpeed API no disponible via PHP (OK)\n";
}

// 5. Verificar que el contenido correcto esta en DB
$post = get_post(3294, ARRAY_A, 'edit');
$has_new = strpos($post['post_content'], 'b370-col-hero') !== false;
echo "5. Contenido DB tiene b370-col-hero: " . ($has_new ? 'SI' : 'NO') . "\n";
echo "   Longitud: " . strlen($post['post_content']) . " chars\n";

// 6. Forzar re-save del post para invalidar caches de WP
// (actualizar sin cambiar contenido — solo timestamp)
$wpdb->update($wpdb->posts, ['post_modified' => current_time('mysql'), 'post_modified_gmt' => current_time('mysql', 1)], ['ID' => 3294]);
clean_post_cache(3294);
echo "6. Post cache limpiado, modified actualizado\n";

echo "\nFLUSH COMPLETADO.\n";
"""

sftp = c.open_sftp()
with sftp.open(f"/home/{USER}/tmp_flush.php", "wb") as f:
    f.write(php.encode("utf-8"))
sftp.close()

print("Ejecutando flush completo...")
_, stdout, _ = c.exec_command(f"php -d error_reporting=0 /home/{USER}/tmp_flush.php 2>&1")
out = stdout.read().decode("utf-8", errors="replace")
print(out)
c.exec_command(f"rm /home/{USER}/tmp_flush.php")

# Verificar con curl qué sirve ahora
print("\n=== Verificando HTML servido post-flush...")
_, stdout2, _ = c.exec_command(
    "curl -s -H 'Cache-Control: no-cache' -H 'Pragma: no-cache' "
    "'https://b370sports.com/colombia-mundial-2026/?nocache=1' --max-time 15 "
    "| grep -o 'b370-col-[a-z-]*' | sort -u | head -20"
)
out2 = stdout2.read().decode("utf-8", errors="replace")
print("Clases b370-col detectadas:", out2.strip() or "(NINGUNA — caché persiste)")

# Si sigue sin clases, intentar con ?v=2 para forzar nueva URL
_, stdout3, _ = c.exec_command(
    "curl -s 'https://b370sports.com/colombia-mundial-2026/?v=2' --max-time 15 "
    "| grep -o 'b370-col-[a-z-]*' | sort -u | head -5"
)
out3 = stdout3.read().decode("utf-8", errors="replace")
print("Con ?v=2:", out3.strip() or "(NINGUNA)")

c.close()
