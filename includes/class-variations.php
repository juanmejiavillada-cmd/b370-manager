<?php
/**
 * Lógica de variaciones: preview, creación/actualización, undo.
 *
 * Usa la API interna de WooCommerce (wc_get_product / WC_Product_Variation)
 * para evitar el round-trip HTTP de la REST API en escrituras.
 *
 * Flujo esperado:
 *   1. build_preview()  → devuelve lista de items a crear/actualizar
 *   2. exec_one()       → ejecuta un item (llamado N veces desde JS en chunks)
 *   3. delete_many()    → deshace las creaciones de la sesión
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class B370_Manager_Variations {

	// ─────────────────────────────────────────────────────────────
	// Mapeo de atributos del producto
	// ─────────────────────────────────────────────────────────────

	/**
	 * Devuelve los atributos de variación del producto, enriquecidos con el "rol"
	 * que B370 asigna a cada uno (talla / calidad / acabado / unknown).
	 *
	 * @param int $product_id
	 * @return array  slug => [ slug, label, is_taxonomy, options[], role ]
	 */
	public static function get_variation_attrs( $product_id ) {
		$product = wc_get_product( (int) $product_id );
		if ( ! $product ) {
			return [];
		}

		$result = [];
		foreach ( $product->get_attributes() as $slug => $attr ) {
			if ( ! $attr->get_variation() ) {
				continue;
			}
			$label = $attr->is_taxonomy()
				? wc_attribute_label( $attr->get_name() )
				: $attr->get_name();

			$label_lc = strtolower( $label );
			$slug_lc  = strtolower( $slug );

			if ( str_contains( $label_lc, 'talla' ) || str_contains( $slug_lc, 'talla' ) ) {
				$role = 'talla';
			} elseif ( str_contains( $label_lc, 'calidad' ) || str_contains( $slug_lc, 'calidad' ) ) {
				$role = 'calidad';
			} elseif ( str_contains( $label_lc, 'acabado' ) || str_contains( $slug_lc, 'acabado' ) ) {
				$role = 'acabado';
			} else {
				$role = 'unknown';
			}

			$result[ $slug ] = [
				'slug'        => $slug,
				'label'       => $label,
				'is_taxonomy' => $attr->is_taxonomy(),
				'options'     => $attr->get_options(),
				'role'        => $role,
			];
		}
		return $result;
	}

	// ─────────────────────────────────────────────────────────────
	// Indexar variaciones existentes
	// ─────────────────────────────────────────────────────────────

	/**
	 * Indexa las variaciones existentes por clave compuesta talla|calidad|acabado.
	 *
	 * @param int $product_id
	 * @return array  key => [ id, sku, stock, price ]
	 */
	public static function index_existing( $product_id ) {
		$product = wc_get_product( (int) $product_id );
		if ( ! $product || $product->get_type() !== 'variable' ) {
			return [];
		}

		$attr_map = self::get_variation_attrs( $product_id );
		$indexed  = [];

		foreach ( $product->get_children() as $var_id ) {
			$var = wc_get_product( $var_id );
			if ( ! $var ) {
				continue;
			}
			$var_attrs = $var->get_variation_attributes();

			$talla = ''; $calidad = ''; $acabado = '';
			foreach ( $attr_map as $slug => $info ) {
				$val = $var_attrs[ 'attribute_' . $slug ] ?? '';
				if ( $info['role'] === 'talla' )   { $talla   = $val; }
				if ( $info['role'] === 'calidad' )  { $calidad = $val; }
				if ( $info['role'] === 'acabado' )  { $acabado = $val; }
			}

			$key            = "{$talla}|{$calidad}|{$acabado}";
			$indexed[ $key ] = [
				'id'    => $var_id,
				'sku'   => $var->get_sku(),
				'stock' => $var->get_stock_quantity(),
				'price' => $var->get_regular_price(),
			];
		}
		return $indexed;
	}

	// ─────────────────────────────────────────────────────────────
	// Preview
	// ─────────────────────────────────────────────────────────────

	/**
	 * Construye la lista de items a ejecutar comparando Quenti contra WooCommerce.
	 *
	 * @param int   $product_id
	 * @param array $quenti_rows   Filas devueltas por B370_Manager_Quenti::parse_row()
	 * @param array $config {
	 *   tallas[]        Tallas a incluir. Vacío = todas.
	 *   skip_no_calidad bool
	 *   precios         array  mismo formato que B370_OPT_PRECIOS
	 * }
	 * @return array  items listos para exec_one()
	 */
	public static function build_preview( $product_id, array $quenti_rows, array $config ) {
		$existing       = self::index_existing( $product_id );
		$precios        = $config['precios'] ?? get_option( B370_OPT_PRECIOS, [] );
		$tallas         = $config['tallas'] ?? [];
		$skip_no_calidad = ! empty( $config['skip_no_calidad'] );

		$preview = [];
		$seen    = [];

		foreach ( $quenti_rows as $row ) {
			if ( $tallas && ! in_array( $row['talla'], $tallas, true ) ) {
				continue;
			}
			if ( $skip_no_calidad && empty( $row['calidad'] ) ) {
				continue;
			}

			$key = self::row_key( $row );
			if ( isset( $seen[ $key ] ) ) {
				continue; // dedup: mismo talla+calidad+acabado → primera fila gana
			}
			$seen[ $key ] = true;

			$existing_item = $existing[ $key ] ?? null;
			$price         = self::resolve_price( $row, $precios );

			$preview[] = [
				'key'         => $key,
				'talla'       => $row['talla'],
				'calidad'     => $row['calidad'] ?? '',
				'acabado'     => $row['acabado'] ?? '',
				'sku'         => $row['sku'],
				'stock'       => (int) $row['stock'],
				'price'       => $price,
				'action'      => $existing_item ? 'update' : 'create',
				'existing_id' => $existing_item ? (int) $existing_item['id'] : null,
			];
		}

		// Crear primero, luego actualizar (cosmético)
		usort( $preview, fn( $a, $b ) => strcmp( $a['action'], $b['action'] ) );

		return $preview;
	}

	// ─────────────────────────────────────────────────────────────
	// Ejecución de un item
	// ─────────────────────────────────────────────────────────────

	/**
	 * Crea o actualiza una variación según el item devuelto por build_preview().
	 *
	 * @param int   $product_id
	 * @param array $item  [ talla, calidad, acabado, sku, stock, price, existing_id, image_id? ]
	 * @return array|WP_Error  [ id, action ]
	 */
	public static function exec_one( $product_id, array $item ) {
		$product = wc_get_product( (int) $product_id );
		if ( ! $product || $product->get_type() !== 'variable' ) {
			return new WP_Error( 'b370_no_product', 'Producto no encontrado o no es variable: ' . $product_id );
		}

		$attr_map  = self::get_variation_attrs( $product_id );
		$set_attrs = [];

		foreach ( $attr_map as $slug => $info ) {
			$val = '';
			if ( $info['role'] === 'talla' )   { $val = $item['talla']   ?? ''; }
			if ( $info['role'] === 'calidad' )  { $val = $item['calidad'] ?? ''; }
			if ( $info['role'] === 'acabado' )  { $val = $item['acabado'] ?? ''; }

			if ( $val === '' ) {
				continue;
			}
			if ( $info['is_taxonomy'] ) {
				$val = self::ensure_term( $slug, $val );
			}
			$set_attrs[ $slug ] = $val;
		}

		// ¿Crear o actualizar?
		if ( ! empty( $item['existing_id'] ) ) {
			$var = wc_get_product( (int) $item['existing_id'] );
			if ( ! $var ) {
				return new WP_Error( 'b370_no_variation', 'Variación no encontrada: ' . $item['existing_id'] );
			}
			$action = 'updated';
		} else {
			$var = new WC_Product_Variation();
			$var->set_parent_id( (int) $product_id );
			if ( $set_attrs ) {
				$var->set_attributes( $set_attrs );
			}
			$var->set_status( 'publish' );
			$action = 'created';
		}

		if ( ! empty( $item['sku'] ) ) {
			$var->set_sku( (string) $item['sku'] );
		}
		if ( isset( $item['stock'] ) && $item['stock'] !== null && $item['stock'] !== '' ) {
			$var->set_manage_stock( true );
			$qty = (int) $item['stock'];
			$var->set_stock_quantity( $qty );
			$var->set_stock_status( $qty > 0 ? 'instock' : 'outofstock' );
		}
		if ( ! empty( $item['price'] ) ) {
			$var->set_regular_price( (string) (int) $item['price'] );
		}
		if ( ! empty( $item['image_id'] ) ) {
			$var->set_image_id( (int) $item['image_id'] );
		}

		$var_id = $var->save();

		if ( ! $var_id || is_wp_error( $var_id ) ) {
			$msg = is_wp_error( $var_id ) ? $var_id->get_error_message() : 'Error desconocido al guardar';
			return new WP_Error( 'b370_save_failed', $msg );
		}

		// Limpiar caché del producto padre para que WC recalcule precios
		wc_delete_product_transients( (int) $product_id );

		return [ 'id' => $var_id, 'action' => $action ];
	}

	// ─────────────────────────────────────────────────────────────
	// Undo
	// ─────────────────────────────────────────────────────────────

	/**
	 * Elimina variaciones recién creadas (undo de sesión).
	 * Solo elimina variaciones que pertenezcan al producto indicado.
	 *
	 * @param int   $product_id
	 * @param int[] $var_ids
	 * @return array  [ deleted[], failed[] ]
	 */
	public static function delete_many( $product_id, array $var_ids ) {
		$deleted = [];
		$failed  = [];

		foreach ( $var_ids as $var_id ) {
			$var = wc_get_product( (int) $var_id );
			if ( $var && (int) $var->get_parent_id() === (int) $product_id ) {
				$var->delete( true );
				wc_delete_product_transients( (int) $product_id );
				$deleted[] = (int) $var_id;
			} else {
				$failed[] = (int) $var_id;
			}
		}

		return [ 'deleted' => $deleted, 'failed' => $failed ];
	}

	// ─────────────────────────────────────────────────────────────
	// Helpers internos
	// ─────────────────────────────────────────────────────────────

	/** Clave compuesta de una fila de Quenti: talla|calidad|acabado */
	private static function row_key( $row ) {
		return ( $row['talla'] ?? '' ) . '|' . ( $row['calidad'] ?? '' ) . '|' . ( $row['acabado'] ?? '' );
	}

	/**
	 * Resuelve el precio final: prioriza config (plugin), luego precio de Quenti.
	 */
	private static function resolve_price( $row, $precios ) {
		$map = [
			'version_fan'   => 'version_fan',
			'tipo_original' => 'tipo_original',
			'1.1'           => 'uno_uno',
		];
		$k = $map[ $row['calidad'] ?? '' ] ?? null;
		if ( $k && isset( $precios[ $k ] ) && (int) $precios[ $k ] > 0 ) {
			return (int) $precios[ $k ];
		}
		return (int) ( $row['precio'] ?? 0 );
	}

	/**
	 * Garantiza que un término existe en un atributo taxonomía.
	 * Lo crea si no existe. Devuelve el slug del término.
	 */
	private static function ensure_term( $taxonomy, $value ) {
		if ( ! taxonomy_exists( $taxonomy ) ) {
			return sanitize_title( $value );
		}
		$term = get_term_by( 'name', $value, $taxonomy )
			 ?: get_term_by( 'slug', sanitize_title( $value ), $taxonomy );

		if ( ! $term ) {
			$inserted = wp_insert_term( $value, $taxonomy );
			if ( is_wp_error( $inserted ) ) {
				return sanitize_title( $value );
			}
			$term = get_term( $inserted['term_id'], $taxonomy );
		}

		return $term ? $term->slug : sanitize_title( $value );
	}
}
