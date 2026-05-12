<?php
/**
 * Módulo 2 — Gestión de imágenes.
 *
 * Sube archivos a la media library de WP y los asigna al producto:
 *   - imagen principal  → _thumbnail_id
 *   - galería WC        → _product_image_gallery  (IDs separados por coma)
 *   - galería WAVI      → wavi_value              (IDs separados por coma)
 *
 * Los slots son: main | gallery_2 | gallery_3 | gallery_4
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class B370_Manager_Images {

	// Slots disponibles y su meta-rol
	const SLOTS = [ 'main', 'gallery_2', 'gallery_3', 'gallery_4' ];

	// ─────────────────────────────────────────────────────────────
	// Subir imagen desde $_FILES
	// ─────────────────────────────────────────────────────────────

	/**
	 * Sube un archivo de imagen a la media library asociado al producto.
	 *
	 * @param array $file_data  Entrada de $_FILES['file'] (name, tmp_name, size, type, error)
	 * @param int   $product_id Post parent
	 * @return int|WP_Error  Attachment ID o error
	 */
	public static function upload( array $file_data, $product_id ) {
		if ( ! function_exists( 'wp_handle_upload' ) ) {
			require_once ABSPATH . 'wp-admin/includes/file.php';
		}
		if ( ! function_exists( 'wp_generate_attachment_metadata' ) ) {
			require_once ABSPATH . 'wp-admin/includes/image.php';
		}
		if ( ! function_exists( 'media_handle_upload' ) ) {
			require_once ABSPATH . 'wp-admin/includes/media.php';
		}

		// Validar tipo MIME antes de subir
		$allowed = [ 'image/jpeg', 'image/png', 'image/webp', 'image/gif' ];
		$finfo   = finfo_open( FILEINFO_MIME_TYPE );
		$mime    = finfo_file( $finfo, $file_data['tmp_name'] );
		finfo_close( $finfo );

		if ( ! in_array( $mime, $allowed, true ) ) {
			return new WP_Error( 'b370_invalid_mime', 'Tipo de archivo no permitido. Solo JPEG, PNG, WebP o GIF.' );
		}

		// Inyectar en $_FILES temporalmente para wp_handle_upload
		$_FILES['b370_upload'] = $file_data;

		$overrides = [ 'test_form' => false ];
		$uploaded  = wp_handle_upload( $_FILES['b370_upload'], $overrides );

		unset( $_FILES['b370_upload'] );

		if ( isset( $uploaded['error'] ) ) {
			return new WP_Error( 'b370_upload_failed', $uploaded['error'] );
		}

		$attachment = [
			'post_mime_type' => $uploaded['type'],
			'post_title'     => sanitize_file_name( pathinfo( $uploaded['file'], PATHINFO_FILENAME ) ),
			'post_content'   => '',
			'post_status'    => 'inherit',
			'post_parent'    => (int) $product_id,
		];

		$att_id = wp_insert_attachment( $attachment, $uploaded['file'], (int) $product_id );
		if ( is_wp_error( $att_id ) ) {
			return $att_id;
		}

		$meta = wp_generate_attachment_metadata( $att_id, $uploaded['file'] );
		wp_update_attachment_metadata( $att_id, $meta );

		return (int) $att_id;
	}

	// ─────────────────────────────────────────────────────────────
	// Asignar slots a un producto
	// ─────────────────────────────────────────────────────────────

	/**
	 * Asigna los attachment IDs a los slots del producto.
	 *
	 * @param int   $product_id
	 * @param array $slot_ids  [ 'main' => 123, 'gallery_2' => 456, ... ]  (0 = vacío)
	 * @return true|WP_Error
	 */
	public static function assign_slots( $product_id, array $slot_ids ) {
		$product = wc_get_product( (int) $product_id );
		if ( ! $product ) {
			return new WP_Error( 'b370_no_product', 'Producto no encontrado: ' . $product_id );
		}

		// Imagen principal
		if ( ! empty( $slot_ids['main'] ) ) {
			$product->set_image_id( (int) $slot_ids['main'] );
		}

		// Galería WooCommerce (gallery_2..4)
		$gallery = [];
		foreach ( [ 'gallery_2', 'gallery_3', 'gallery_4' ] as $slot ) {
			if ( ! empty( $slot_ids[ $slot ] ) ) {
				$gallery[] = (int) $slot_ids[ $slot ];
			}
		}
		if ( $gallery ) {
			$product->set_gallery_image_ids( $gallery );
		}

		$product->save();

		// WAVI gallery meta (todos los slots de galería, coma-separados)
		if ( $gallery ) {
			update_post_meta( (int) $product_id, 'wavi_value', implode( ',', $gallery ) );
		}

		return true;
	}

	// ─────────────────────────────────────────────────────────────
	// Leer slots actuales de un producto
	// ─────────────────────────────────────────────────────────────

	/**
	 * Devuelve los attachment IDs actuales por slot.
	 *
	 * @param int $product_id
	 * @return array  [ 'main' => id|0, 'gallery_2' => id|0, ... ]
	 */
	public static function get_slots( $product_id ) {
		$product = wc_get_product( (int) $product_id );
		$result  = array_fill_keys( self::SLOTS, 0 );

		if ( ! $product ) {
			return $result;
		}

		$result['main'] = (int) $product->get_image_id();

		$gallery_ids = $product->get_gallery_image_ids();
		foreach ( [ 'gallery_2', 'gallery_3', 'gallery_4' ] as $i => $slot ) {
			$result[ $slot ] = ! empty( $gallery_ids[ $i ] ) ? (int) $gallery_ids[ $i ] : 0;
		}

		return $result;
	}

	// ─────────────────────────────────────────────────────────────
	// Helper: URL miniatura por attachment ID
	// ─────────────────────────────────────────────────────────────

	/**
	 * @param int    $att_id
	 * @param string $size  'thumbnail' | 'medium' | 'full'
	 * @return string  URL o ''
	 */
	public static function thumb_url( $att_id, $size = 'thumbnail' ) {
		if ( ! $att_id ) {
			return '';
		}
		$src = wp_get_attachment_image_src( (int) $att_id, $size );
		return $src ? $src[0] : '';
	}
}
