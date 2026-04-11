<?php
/**
 * Menú admin de B370 Manager + todos los handlers AJAX.
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

		// ── AJAX handlers ──────────────────────────────────────────
		// Módulo 3: parsear Excel de Quenti
		add_action( 'wp_ajax_b370_parse_quenti',    [ $this, 'ajax_parse_quenti' ] );
		// Módulo 4: preview de variaciones
		add_action( 'wp_ajax_b370_preview_vars',    [ $this, 'ajax_preview_vars' ] );
		// Módulo 5: ejecutar un item
		add_action( 'wp_ajax_b370_exec_one',        [ $this, 'ajax_exec_one' ] );
		// Módulo 5: undo (eliminar variaciones de sesión)
		add_action( 'wp_ajax_b370_undo_session',    [ $this, 'ajax_undo_session' ] );
		// Módulo 2: subir imagen
		add_action( 'wp_ajax_b370_upload_image',    [ $this, 'ajax_upload_image' ] );
		// Módulo 2: guardar asignación de slots
		add_action( 'wp_ajax_b370_save_slots',      [ $this, 'ajax_save_slots' ] );
	}

	// ─────────────────────────────────────────────────────────────
	// Menú
	// ─────────────────────────────────────────────────────────────

	public function register_menu() {
		$cap  = 'manage_woocommerce';
		$slug = 'b370-manager';

		add_menu_page(
			'B370 Manager', 'B370 Manager', $cap, $slug,
			[ $this, 'render_products' ],
			'dashicons-products', 56
		);
		add_submenu_page( $slug, 'Productos',       'Productos',       $cap, $slug,                   [ $this, 'render_products' ] );
		add_submenu_page( $slug, 'Imágenes',        'Imágenes',        $cap, 'b370-manager-images',   [ $this, 'render_images' ] );
		add_submenu_page( $slug, 'Importar Quenti', 'Importar Quenti', $cap, 'b370-manager-quenti',   [ $this, 'render_quenti' ] );
		add_submenu_page( $slug, 'Configuración',   'Configuración',   $cap, 'b370-manager-settings', [ $this, 'render_settings' ] );
	}

	// ─────────────────────────────────────────────────────────────
	// Assets
	// ─────────────────────────────────────────────────────────────

	public function enqueue_assets( $hook ) {
		if ( strpos( (string) $hook, 'b370-manager' ) === false ) {
			return;
		}
		wp_enqueue_style(
			'b370-manager-admin',
			B370_MANAGER_URL . 'admin/css/b370-admin.css',
			[], B370_MANAGER_VERSION
		);
		wp_enqueue_script(
			'b370-manager-admin',
			B370_MANAGER_URL . 'assets/js/b370-manager.js',
			[ 'jquery' ], B370_MANAGER_VERSION, true
		);
		wp_localize_script( 'b370-manager-admin', 'b370', [
			'ajax_url' => admin_url( 'admin-ajax.php' ),
			'nonce'    => wp_create_nonce( 'b370_ajax' ),
		] );
	}

	// ─────────────────────────────────────────────────────────────
	// Vistas
	// ─────────────────────────────────────────────────────────────

	public function render_products()  { $this->load_view( 'products' ); }
	public function render_images()    { $this->load_view( 'images' ); }
	public function render_quenti()    { $this->load_view( 'quenti' ); }
	public function render_settings()  { $this->load_view( 'settings' ); }

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

	// ─────────────────────────────────────────────────────────────
	// Settings save
	// ─────────────────────────────────────────────────────────────

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

		$precios_in = isset( $_POST['b370_precios'] ) && is_array( $_POST['b370_precios'] )
			? wp_unslash( $_POST['b370_precios'] ) : [];
		$precios = [];
		foreach ( [ 'version_fan', 'tipo_original', 'uno_uno', 'retro', 'buzo_an', 'gaban_an', 'con_parches', 'sin_parches' ] as $k ) {
			$precios[ $k ] = isset( $precios_in[ $k ] ) ? (int) preg_replace( '/\D/', '', (string) $precios_in[ $k ] ) : 0;
		}
		update_option( B370_OPT_PRECIOS, $precios );

		add_action( 'admin_notices', function () {
			echo '<div class="notice notice-success is-dismissible"><p>Configuración guardada correctamente.</p></div>';
		} );
	}

	// ─────────────────────────────────────────────────────────────
	// AJAX: Módulo 3 — Parsear Excel de Quenti
	// ─────────────────────────────────────────────────────────────

	public function ajax_parse_quenti() {
		$this->check_ajax();

		if ( empty( $_FILES['xlsx'] ) || $_FILES['xlsx']['error'] !== UPLOAD_ERR_OK ) {
			wp_send_json_error( [ 'message' => 'No se recibió el archivo o hubo un error al subir.' ] );
		}

		$file = $_FILES['xlsx'];
		$ext  = strtolower( pathinfo( $file['name'], PATHINFO_EXTENSION ) );
		if ( ! in_array( $ext, [ 'xlsx', 'xls' ], true ) ) {
			wp_send_json_error( [ 'message' => 'Solo se aceptan archivos .xlsx o .xls' ] );
		}

		// Mover a carpeta temporal del plugin
		$tmp_dir  = get_temp_dir();
		$tmp_file = $tmp_dir . 'b370_quenti_' . wp_generate_password( 12, false ) . '.' . $ext;

		if ( ! move_uploaded_file( $file['tmp_name'], $tmp_file ) ) {
			wp_send_json_error( [ 'message' => 'No se pudo mover el archivo temporal.' ] );
		}

		$rows = B370_Manager_Quenti::read_xlsx( $tmp_file );
		@unlink( $tmp_file );

		if ( is_wp_error( $rows ) ) {
			wp_send_json_error( [ 'message' => $rows->get_error_message() ] );
		}

		$parsed   = [];
		$skipped  = 0;
		foreach ( $rows as $row ) {
			$p = B370_Manager_Quenti::parse_row( $row );
			if ( $p ) {
				$parsed[] = $p;
			} else {
				$skipped++;
			}
		}

		$families = B370_Manager_Quenti::group_by_family( $parsed );

		// Guardar en transient para el siguiente paso (preview)
		$token = wp_generate_password( 20, false );
		set_transient( 'b370_parsed_' . $token, $parsed, 30 * MINUTE_IN_SECONDS );

		wp_send_json_success( [
			'token'         => $token,
			'total_rows'    => count( $rows ),
			'parsed'        => count( $parsed ),
			'skipped'       => $skipped,
			'families'      => count( $families ),
			'rows'          => $parsed,
		] );
	}

	// ─────────────────────────────────────────────────────────────
	// AJAX: Módulo 4 — Preview de variaciones
	// ─────────────────────────────────────────────────────────────

	public function ajax_preview_vars() {
		$this->check_ajax();

		$product_id = (int) ( $_POST['product_id'] ?? 0 );
		$token      = sanitize_text_field( $_POST['token'] ?? '' );
		$tallas     = array_filter( array_map( 'sanitize_text_field', (array) ( $_POST['tallas'] ?? [] ) ) );
		$skip_nc    = ! empty( $_POST['skip_no_calidad'] );

		if ( ! $product_id || ! $token ) {
			wp_send_json_error( [ 'message' => 'Faltan product_id o token.' ] );
		}

		$parsed = get_transient( 'b370_parsed_' . $token );
		if ( ! $parsed ) {
			wp_send_json_error( [ 'message' => 'La sesión expiró. Vuelve a subir el Excel.' ] );
		}

		$config = [
			'tallas'          => $tallas,
			'skip_no_calidad' => $skip_nc,
			'precios'         => get_option( B370_OPT_PRECIOS, [] ),
		];

		$preview = B370_Manager_Variations::build_preview( $product_id, $parsed, $config );

		wp_send_json_success( [
			'items'   => $preview,
			'creates' => count( array_filter( $preview, fn( $i ) => $i['action'] === 'create' ) ),
			'updates' => count( array_filter( $preview, fn( $i ) => $i['action'] === 'update' ) ),
		] );
	}

	// ─────────────────────────────────────────────────────────────
	// AJAX: Módulo 5 — Ejecutar un item
	// ─────────────────────────────────────────────────────────────

	public function ajax_exec_one() {
		$this->check_ajax();

		$product_id = (int) ( $_POST['product_id'] ?? 0 );
		$item_json  = wp_unslash( $_POST['item'] ?? '' );
		$item       = json_decode( $item_json, true );

		if ( ! $product_id || ! is_array( $item ) ) {
			wp_send_json_error( [ 'message' => 'Datos incompletos.' ] );
		}

		$result = B370_Manager_Variations::exec_one( $product_id, $item );

		if ( is_wp_error( $result ) ) {
			wp_send_json_error( [
				'message' => $result->get_error_message(),
				'item'    => $item,
			] );
		}

		wp_send_json_success( $result );
	}

	// ─────────────────────────────────────────────────────────────
	// AJAX: Módulo 5 — Undo de sesión
	// ─────────────────────────────────────────────────────────────

	public function ajax_undo_session() {
		$this->check_ajax();

		$product_id = (int) ( $_POST['product_id'] ?? 0 );
		$var_ids    = array_map( 'intval', (array) ( $_POST['var_ids'] ?? [] ) );

		if ( ! $product_id || ! $var_ids ) {
			wp_send_json_error( [ 'message' => 'Faltan product_id o var_ids.' ] );
		}

		$result = B370_Manager_Variations::delete_many( $product_id, $var_ids );
		wp_send_json_success( $result );
	}

	// ─────────────────────────────────────────────────────────────
	// AJAX: Módulo 2 — Subir imagen
	// ─────────────────────────────────────────────────────────────

	public function ajax_upload_image() {
		$this->check_ajax();

		$product_id = (int) ( $_POST['product_id'] ?? 0 );
		if ( ! $product_id ) {
			wp_send_json_error( [ 'message' => 'Falta product_id.' ] );
		}
		if ( empty( $_FILES['file'] ) || $_FILES['file']['error'] !== UPLOAD_ERR_OK ) {
			wp_send_json_error( [ 'message' => 'No se recibió el archivo.' ] );
		}

		$att_id = B370_Manager_Images::upload( $_FILES['file'], $product_id );
		if ( is_wp_error( $att_id ) ) {
			wp_send_json_error( [ 'message' => $att_id->get_error_message() ] );
		}

		wp_send_json_success( [
			'id'    => $att_id,
			'thumb' => B370_Manager_Images::thumb_url( $att_id, 'medium' ),
			'url'   => wp_get_attachment_url( $att_id ),
		] );
	}

	// ─────────────────────────────────────────────────────────────
	// AJAX: Módulo 2 — Guardar slots
	// ─────────────────────────────────────────────────────────────

	public function ajax_save_slots() {
		$this->check_ajax();

		$product_id = (int) ( $_POST['product_id'] ?? 0 );
		$slots_raw  = isset( $_POST['slots'] ) && is_array( $_POST['slots'] ) ? $_POST['slots'] : [];

		if ( ! $product_id ) {
			wp_send_json_error( [ 'message' => 'Falta product_id.' ] );
		}

		$slots = [];
		foreach ( B370_Manager_Images::SLOTS as $slot ) {
			$slots[ $slot ] = isset( $slots_raw[ $slot ] ) ? (int) $slots_raw[ $slot ] : 0;
		}

		$result = B370_Manager_Images::assign_slots( $product_id, $slots );
		if ( is_wp_error( $result ) ) {
			wp_send_json_error( [ 'message' => $result->get_error_message() ] );
		}

		wp_send_json_success( [ 'saved' => true ] );
	}

	// ─────────────────────────────────────────────────────────────
	// Helper: verificar nonce + capacidad para AJAX
	// ─────────────────────────────────────────────────────────────

	private function check_ajax() {
		if ( ! check_ajax_referer( 'b370_ajax', 'nonce', false ) ) {
			wp_send_json_error( [ 'message' => 'Nonce inválido. Recarga la página.' ], 403 );
		}
		if ( ! current_user_can( 'manage_woocommerce' ) ) {
			wp_send_json_error( [ 'message' => 'No tienes permisos para esta acción.' ], 403 );
		}
	}
}
