#!/usr/bin/env python3
import os, sys, paramiko
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

HOST = os.getenv("SSH_HOST"); PORT = int(os.getenv("SSH_PORT", 22))
USER = os.getenv("SSH_USER"); PWD  = os.getenv("SSH_PASS")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)
sftp = c.open_sftp()

php = r"""<?php
$_SERVER['HTTP_HOST'] = 'b370sports.com';
$_SERVER['REQUEST_URI'] = '/';
define('ABSPATH', '/home/u122447978/domains/b370sports.com/public_html/');
require '/home/u122447978/domains/b370sports.com/public_html/wp-load.php';

$args = ['post_type'=>'product','posts_per_page'=>100,'post_status'=>'publish',
  'tax_query'=>[['taxonomy'=>'product_cat','field'=>'slug','terms'=>['camisetas-colombia','retro','colombia'],'operator'=>'IN']]
];
$q = new WP_Query($args);
foreach($q->posts as $p) {
    $img_id = get_post_thumbnail_id($p->ID);
    $img = $img_id ? wp_get_attachment_image_url($img_id, 'full') : '(sin img)';
    $slug = get_post_field('post_name', $p->ID);
    echo $p->ID . '|' . $p->post_title . '|' . $slug . '|' . $img . "\n";
}
if($q->post_count == 0) {
    // fallback: buscar por nombre
    $q2 = new WP_Query(['post_type'=>'product','posts_per_page'=>100,'s'=>'colombia retro']);
    foreach($q2->posts as $p) {
        $img_id = get_post_thumbnail_id($p->ID);
        $img = $img_id ? wp_get_attachment_image_url($img_id, 'full') : '(sin img)';
        echo $p->ID . '|' . $p->post_title . '|' . get_post_field('post_name',$p->ID) . '|' . $img . "\n";
    }
}
"""
with sftp.open(f"/home/{USER}/tmp_imgs.php", "wb") as f:
    f.write(php.encode("utf-8"))
sftp.close()
_, stdout, _ = c.exec_command(f"php -d error_reporting=0 /home/{USER}/tmp_imgs.php 2>&1")
out = stdout.read().decode("utf-8", errors="replace")
print(out[:3000])
c.exec_command(f"rm /home/{USER}/tmp_imgs.php")
c.close()
