#!/usr/bin/env python3
import os, sys, paramiko
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

HOST = os.getenv("SSH_HOST")
PORT = int(os.getenv("SSH_PORT", 22))
USER = os.getenv("SSH_USER")
PWD  = os.getenv("SSH_PASS")

print(f"Conectando a {HOST}:{PORT}...")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, port=PORT, username=USER, password=PWD)

php = r"""<?php
$_SERVER['HTTP_HOST'] = 'b370sports.com';
$_SERVER['REQUEST_URI'] = '/';
define('ABSPATH', '/home/u122447978/domains/b370sports.com/public_html/');
require '/home/u122447978/domains/b370sports.com/public_html/wp-load.php';

$post = get_post(3294);
echo "STATUS: " . $post->post_status . "\n";
echo "LENGTH: " . strlen($post->post_content) . "\n";
echo "FIRST500:\n" . substr($post->post_content, 0, 500) . "\n";
echo "---END---\n";
echo "TEMPLATE: " . get_page_template_slug(3294) . "\n";
$meta = get_post_meta(3294);
$builder_found = false;
foreach($meta as $k => $v) {
  if(strpos($k, 'elementor') !== false || strpos($k, 'builder') !== false || strpos($k, '_et_') !== false || strpos($k, 'divi') !== false) {
    echo "BUILDER_META: " . $k . "\n";
    $builder_found = true;
  }
}
if(!$builder_found) echo "NO_BUILDER_META\n";
"""

sftp = c.open_sftp()
with sftp.open(f"/home/{USER}/tmp_diag.php", "wb") as f:
    f.write(php.encode("utf-8"))
sftp.close()

_, stdout, stderr = c.exec_command(f"php /home/{USER}/tmp_diag.php 2>&1")
out = stdout.read().decode("utf-8", errors="replace")
print(out[:3000])
c.exec_command(f"rm /home/{USER}/tmp_diag.php")
c.close()
print("Diagnostico completado.")
