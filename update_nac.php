<?php
require_once('/home/u122447978/domains/b370sports.com/public_html/wp-load.php');
$html = file_get_contents('/tmp/nacional_html.txt');
$content = '<!-- wp:html -->' . $html . '<!-- /wp:html -->';
$r = wp_update_post(array(
    'ID'           => 3295,
    'post_title'   => 'Camisetas Atletico Nacional 2026 - Local, Visitante y Tercera | B370',
    'post_content' => $content,
));
echo is_wp_error($r) ? 'ERR:'.$r->get_error_message() : 'OK:'.$r;
