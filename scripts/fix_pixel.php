<?php
$wp_path = '/home/u122447978/domains/b370sports.com/public_html/';
$c = file_get_contents($wp_path . 'wp-config.php');
preg_match("/define\s*\(\s*'DB_NAME'\s*,\s*'([^']+)'\s*\)/", $c, $n);
preg_match("/define\s*\(\s*'DB_USER'\s*,\s*'([^']+)'\s*\)/", $c, $u);
preg_match("/define\s*\(\s*'DB_PASSWORD'\s*,\s*'([^']+)'\s*\)/", $c, $p);

$db = new mysqli('localhost', $u[1], $p[1], $n[1]);

// Leer config actual
$r = $db->query("SELECT option_value FROM wp_options WHERE option_name='pixelyoursite_facebook' LIMIT 1");
$row = $r->fetch_assoc();
$config = maybe_unserialize_manual($row['option_value']);

echo "CONFIG ACTUAL:\n";
echo $row['option_value'];

function maybe_unserialize_manual($data) {
    if (@unserialize($data) !== false) return @unserialize($data);
    return json_decode($data, true);
}
