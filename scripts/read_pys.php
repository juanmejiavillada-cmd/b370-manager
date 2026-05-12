<?php
define('ABSPATH', '/home/u122447978/domains/b370sports.com/public_html/');
define('WPINC', 'wp-includes');

// Bootstrap WordPress DB
$wp_config = file_get_contents(ABSPATH . 'wp-config.php');
preg_match("/define\s*\(\s*'DB_NAME'\s*,\s*'([^']+)'/", $wp_config, $n);
preg_match("/define\s*\(\s*'DB_USER'\s*,\s*'([^']+)'/", $wp_config, $u);
preg_match("/define\s*\(\s*'DB_PASSWORD'\s*,\s*'([^']+)'/", $wp_config, $p);
preg_match("/\\\$table_prefix\s*=\s*'([^']+)'/", $wp_config, $t);

$prefix = isset($t[1]) ? $t[1] : 'wp_';
$db = new mysqli('localhost', $u[1], $p[1], $n[1]);
$db->set_charset('utf8mb4');

// Buscar todas las opciones que tengan 'pys' o 'pixel'
$r = $db->query("SELECT option_name FROM {$prefix}options WHERE option_name LIKE '%pys%' OR option_name LIKE '%pixel%' OR option_name LIKE '%facebook%'");
echo "=== TODAS LAS OPCIONES PYS/PIXEL/FACEBOOK ===\n";
while ($row = $r->fetch_assoc()) {
    echo $row['option_name'] . "\n";
}

// Intentar leer opciones comunes de PYS
$option_names = ['pixelyoursite_facebook', 'pys_facebook', 'pys-facebook', 'PixelYourSite_Facebook', 'pys_free_facebook'];
foreach ($option_names as $opt) {
    $stmt = $db->prepare("SELECT option_value FROM {$prefix}options WHERE option_name = ? LIMIT 1");
    $stmt->bind_param('s', $opt);
    $stmt->execute();
    $result = $stmt->get_result();
    $row = $result->fetch_assoc();
    if ($row) {
        echo "\n=== ENCONTRADO: $opt ===\n";
        echo substr($row['option_value'], 0, 3000) . "\n";
    }
}
