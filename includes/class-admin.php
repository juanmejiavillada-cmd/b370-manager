<?php
/**
 * Menú admin de B370 Manager.
 *
 * Registra "B370 Manager" como menú de nivel superior con submenús:
 * - Productos
 * - Imágenes
 * - Importar Quenti
 * - Configuración
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class B370_Manager_Admin {

	private static $instance = null;

	public static function instance() {
		if ( self::$instance === null ) {
			self::$instance = new self();
		}
		return self::$instance;
	}

	private function __construct() {
		add_action( 'admin_menu',            [ $this, 'register_menu' ] );
		add_action( 'admin_enqueue_scripts', [ $this, 'enqueue_assets' ] );
		add_action( 'admin_init',            [ $this, 'handle_settings_save' ] );
	}

	/**
	 * Registra el menú y los submenús.
	 */
	public function register_menu() {
		$cap  = 'manage_woocommerce';
		$slug = 'b370-manager';

		add_menu_page(
			'B370 Manager',
			'B370 Manager',
			$cap,
			$slug,
			[ $this, 'render_products' ],
			'dashicons-products',
			56
		);

		add_submenu_page( $slug, 'Productos',       'Productos',       $cap, $slug,                    [ $this, 'render_products' ] );
		add_submenu_page( $slug, 'Imágenes',        'Imágenes',        $cap, 'b370-manager-images',    [ $this, 'render_images' ] );
		add_submenu_page( $slug, 'Importar Quenti', 'Importar Quenti', $cap, 'b370-manager-quenti',    [ $this, 'render_quenti' ] );
		add_submenu_page( $slug, 'Configuración',   'Configuración',   $cap, 'b370-manager-settings',  [ $this, 'render_settings' ] );
	}

	/**
	 * Carga CSS/JS solo en las páginas del plugin.
	 */
	public function enqueue_assets( $hook ) {
		if ( strpos( (string) $hook, 'b370-manager' ) === false ) {
			return;
		}
		wp_enqueue_style(
			'b370-manager-admin',
			B370_MANAGER_URL . 'admin/css/b370-admin.css',
			[],
			B370_MANAGER_VERSION
		);
		wp_enqueue_script(
			'b370-manager-admin',
			B370_MANAGER_URL . 'assets/js/b370-manager.js',
			[ 'jquery' ],
			B370_MANAGER_VERSION,
			true
		);
	}

	/* ------------------------- Renderers ------------------------- */

	public function render_products() {
		$this->load_view( 'products' );
	}

	public function render_images() {
		$this->load_view( 'images' );
	}

	public function render_quenti() {
		$this->load_view( 'quenti' );
	}

	public function render_settings() {
		$this->load_view( 'settings' );
	}

	private function load_view( $name ) {
		$file = B370_MANAGER_DIR . 'admin/views/' . $name . '.php';
		if ( ! file_exists( $file ) ) {
			echo '<div class="wrap"><h1>B370 Manager</h1><p>Vista <code>' . esc_html( $name ) . '</code> no encontrada.</p></div>';
			return;
		}
		echo '<div class="wrap b370-wrap">';
		include $file;
		echo '</div>';
	}

	/* ------------------------- Settings save ------------------------- */

	/**
	 * Guarda credenciales y precios por defecto desde el formulario de Settings.
	 */
	public function handle_settings_save() {
		if ( ! isset( $_POST['b370_settings_nonce'] ) ) {
			return;
		}
		if ( ! current_user_can( 'manage_woocommerce' ) ) {
			return;
		}
		if ( ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['b370_settings_nonce'] ) ), 'b370_save_settings' ) ) {
			return;
		}

		$url    = isset( $_POST['b370_wc_url'] )    ? esc_url_raw( wp_unslash( $_POST['b370_wc_url'] ) )           : '';
		$key    = isset( $_POST['b370_wc_key'] )    ? sanitize_text_field( wp_unslash( $_POST['b370_wc_key'] ) )    : '';
		$secret = isset( $_POST['b370_wc_secret'] ) ? sanitize_text_field( wp_unslash( $_POST['b370_wc_secret'] ) ) : '';

		update_option( B370_OPT_WC_URL,    $url );
		update_option( B370_OPT_WC_KEY,    $key );
		update_option( B370_OPT_WC_SECRET, $secret );

		// Precios por defecto.
		$precios_in = isset( $_POST['b370_precios'] ) && is_array( $_POST['b370_precios'] )
			? wp_unslash( $_POST['b370_precios'] )
			: [];
		$precios = [];
		foreach ( [ 'version_fan', 'tipo_original', 'uno_uno', 'retro', 'buzo_an', 'gaban_an', 'con_parches', 'sin_parches' ] as $k ) {
			$precios[ $k ] = isset( $precios_in[ $k ] ) ? (int) preg_replace( '/\D/', '', (string) $precios_in[ $k ] ) : 0;
		}
		update_option( B370_OPT_PRECIOS, $precios );

		add_action( 'admin_notices', function () {
			echo '<div class="notice notice-success is-dismissible"><p>Configuración guardada.</p></div>';
		} );
	}
}
