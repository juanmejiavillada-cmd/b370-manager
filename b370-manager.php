<?php
/**
 * Plugin Name:       B370 Manager
 * Plugin URI:        https://b370sports.com
 * Description:       Gestor interno de catálogo para B370 Línea Deportiva. Crea y actualiza variaciones de WooCommerce, sube imágenes por tipo y sincroniza stock desde el Excel de Quenti.
 * Version:           0.1.0
 * Requires at least: 6.0
 * Requires PHP:      7.4
 * Author:            Juanjo (B370)
 * License:           Privado — uso interno B370
 * Text Domain:       b370-manager
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// Cargar PhpSpreadsheet (y cualquier otra dependencia Composer)
$b370_autoload = plugin_dir_path( __FILE__ ) . 'vendor/autoload.php';
if ( file_exists( $b370_autoload ) ) {
	require_once $b370_autoload;
}
unset( $b370_autoload );

define( 'B370_MANAGER_VERSION', '0.2.0' );
define( 'B370_MANAGER_FILE', __FILE__ );
define( 'B370_MANAGER_DIR', plugin_dir_path( __FILE__ ) );
define( 'B370_MANAGER_URL', plugin_dir_url( __FILE__ ) );
define( 'B370_MANAGER_BASENAME', plugin_basename( __FILE__ ) );

// Opciones (wp_options) usadas por el plugin.
define( 'B370_OPT_WC_KEY',     'b370_wc_api_key' );
define( 'B370_OPT_WC_SECRET',  'b370_wc_api_secret' );
define( 'B370_OPT_WC_URL',     'b370_wc_api_url' );
define( 'B370_OPT_PRECIOS',    'b370_precios_default' );

/**
 * Autoloader simple para las clases del plugin.
 * Busca includes/class-<slug>.php a partir de B370_Manager_<Slug>.
 */
spl_autoload_register( function ( $class ) {
	if ( strpos( $class, 'B370_Manager_' ) !== 0 ) {
		return;
	}
	$slug = strtolower( str_replace( [ 'B370_Manager_', '_' ], [ '', '-' ], $class ) );
	$file = B370_MANAGER_DIR . 'includes/class-' . $slug . '.php';
	if ( file_exists( $file ) ) {
		require_once $file;
	}
} );

/**
 * Activación: semillas de opciones y chequeos mínimos.
 */
register_activation_hook( __FILE__, function () {
	// URL por defecto de la tienda.
	if ( get_option( B370_OPT_WC_URL, null ) === null ) {
		update_option( B370_OPT_WC_URL, 'https://b370sports.com' );
	}

	// Precios por defecto (editables desde Settings).
	if ( get_option( B370_OPT_PRECIOS, null ) === null ) {
		update_option( B370_OPT_PRECIOS, [
			'version_fan'      => 80000,
			'tipo_original'    => 110000,
			'uno_uno'          => 120000,
			'retro'            => 80000,
			'buzo_an'          => 95000,
			'gaban_an'         => 150000,
			'con_parches'      => 0, // por definir
			'sin_parches'      => 0, // por definir
		] );
	}

	// Aviso si falta WooCommerce (no bloqueamos la activación).
	if ( ! class_exists( 'WooCommerce' ) ) {
		set_transient( 'b370_manager_wc_missing', 1, 60 );
	}
} );

/**
 * Aviso en admin si WooCommerce no está activo.
 */
add_action( 'admin_notices', function () {
	if ( get_transient( 'b370_manager_wc_missing' ) ) {
		echo '<div class="notice notice-warning is-dismissible"><p><strong>B370 Manager:</strong> WooCommerce no está activo. El plugin requiere WooCommerce para gestionar productos.</p></div>';
		delete_transient( 'b370_manager_wc_missing' );
	}
} );

/**
 * Arranque del plugin en init del admin.
 */
add_action( 'plugins_loaded', function () {
	// Instancia el menú si estamos en admin.
	if ( is_admin() ) {
		B370_Manager_Admin::instance();
	}
} );
