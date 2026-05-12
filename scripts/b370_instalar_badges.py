#!/usr/bin/env python3
"""B370 — Instala badges de línea (Fan/Original/1.1/Retro) como mu-plugin."""
import os, sys, paramiko
from dotenv import load_dotenv
try: sys.stdout.reconfigure(encoding="utf-8")
except: pass
load_dotenv()

PHP = r"""<?php
/**
 * Plugin Name: B370 — Line Badges
 * Description: Muestra badges de linea (Fan/Original/1.1/Retro) en ficha de producto.
 * Version: 1.0
 */

function b370_line_map() {
    return [
        'Tipo fan'      => ['label' => 'FAN',      'class' => 'fan'],
        'Tipo original' => ['label' => 'ORIGINAL', 'class' => 'original'],
        '1.1'           => ['label' => '1.1',      'class' => 'once'],
        'Retro'         => ['label' => 'RETRO',    'class' => 'retro'],
    ];
}

add_action('woocommerce_single_product_summary', function() {
    global $product;
    if (!$product) return;
    $attr = $product->get_attribute('Calidad');
    if (!$attr) return;
    $map = b370_line_map();
    $valores = array_map('trim', explode(',', $attr));
    $html = '<div class="b370-lineas">';
    $any = false;
    foreach ($valores as $v) {
        if (isset($map[$v])) {
            $html .= sprintf('<span class="b370-badge b370-%s">%s</span>',
                esc_attr($map[$v]['class']), esc_html($map[$v]['label']));
            $any = true;
        }
    }
    $html .= '</div>';
    if ($any) echo $html;
}, 6);

add_action('wp_head', function() { ?>
<style id="b370-badges-css">
.b370-lineas{display:flex;gap:.5rem;flex-wrap:wrap;margin:.75rem 0 1rem;align-items:center}
.b370-badge{font-family:'Alfa Slab One','Impact',serif;font-size:.78rem;letter-spacing:.06em;
 padding:.38rem .8rem;border-radius:4px;color:#F9FAF7;display:inline-block;line-height:1;
 text-transform:uppercase}
.b370-fan{background:#6B7280}
.b370-original{background:#151B2D}
.b370-once{background:#E2AC70;color:#151B2D}
.b370-retro{background:#C47B5D}
</style>
<?php });
"""

HOST=os.getenv("SSH_HOST");PORT=int(os.getenv("SSH_PORT",22))
USER=os.getenv("SSH_USER");PWD=os.getenv("SSH_PASS")
c=paramiko.SSHClient();c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST,port=PORT,username=USER,password=PWD)
sftp=c.open_sftp()
mu=f"/home/{USER}/domains/b370sports.com/public_html/wp-content/mu-plugins"
try:sftp.stat(mu)
except IOError:c.exec_command(f"mkdir -p {mu}")
path=f"{mu}/b370-badges.php"
with sftp.open(path,"w") as f: f.write(PHP)
print(f"✅ escrito: {path}")
sftp.close();c.close()
print("🧪 Abrí cualquier ficha de producto con Calidad asignada:")
print("   https://b370sports.com/product/local-hombre-2026/")
