#!/usr/bin/env python3
"""
B370 — Instala redirect 301 como mu-plugin vía SSH.
Se carga solo, sin plugins, sin admin.
"""
import os, sys, paramiko
from dotenv import load_dotenv

try: sys.stdout.reconfigure(encoding="utf-8")
except: pass

load_dotenv()
HOST = os.getenv("SSH_HOST")
PORT = int(os.getenv("SSH_PORT", 22))
USER = os.getenv("SSH_USER")
PASS = os.getenv("SSH_PASS")
BASE = os.getenv("SSH_PATH", "~/domains/b370sports.com/public_html")

PHP = """<?php
/**
 * Plugin Name: B370 — 301 Redirects
 * Description: Redirige slugs viejos a productos actuales.
 * Version: 1.0
 */
add_action('template_redirect', function() {
    $path = trim(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH), '/');
    $map = [
        'product/atletico-nacional-local-2025' => '/product/local-hombre-2026/',
        'product/atletico-nacional-local'      => '/product/local-hombre-2026/',
    ];
    foreach ($map as $from => $to) {
        if (strpos($path, $from) === 0) {
            wp_redirect(home_url($to), 301);
            exit;
        }
    }
});
"""

def main():
    print("🔌 Conectando a", HOST)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USER, password=PASS)
    sftp = c.open_sftp()

    mu_dir = f"{BASE}/wp-content/mu-plugins".replace("~", f"/home/{USER}")
    # crear dir si no existe
    try: sftp.stat(mu_dir)
    except IOError:
        c.exec_command(f"mkdir -p {mu_dir}")
        print(f"  📁 creado {mu_dir}")

    target = f"{mu_dir}/b370-redirects.php"
    with sftp.open(target, "w") as f:
        f.write(PHP)
    print(f"  ✅ escrito: {target}")

    sftp.close(); c.close()
    print("\n🧪 Probá en incógnito:")
    print("   https://b370sports.com/product/atletico-nacional-local-2025/")
    print("   → debería redirigir a /product/local-hombre-2026/\n")

if __name__ == "__main__":
    main()
