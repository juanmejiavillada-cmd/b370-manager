<?php
/**
 * Cliente WooCommerce REST API + helpers para productos variables.
 *
 * Usa wp_remote_* (no cURL directo) y autentica con HTTP Basic
 * (válido sobre HTTPS, que es el caso de b370sports.com).
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class B370_Manager_Products {

	/** @var string */
	private $base_url;

	/** @var string */
	private $key;

	/** @var string */
	private $secret;

	public function __construct() {
		$this->base_url = trailingslashit( (string) get_option( B370_OPT_WC_URL, 'https://b370sports.com' ) ) . 'wp-json/wc/v3/';
		$this->key      = (string) get_option( B370_OPT_WC_KEY, '' );
		$this->secret   = (string) get_option( B370_OPT_WC_SECRET, '' );
	}

	/**
	 * ¿Tenemos credenciales configuradas?
	 */
	public function has_credentials() {
		return $this->key !== '' && $this->secret !== '';
	}

	/**
	 * GET helper con autenticación Basic y manejo de errores.
	 *
	 * @param string $endpoint  Ej: 'products'
	 * @param array  $query     Query params
	 * @return array|WP_Error
	 */
	public function get( $endpoint, $query = [] ) {
		if ( ! $this->has_credentials() ) {
			return new WP_Error( 'b370_no_credentials', 'Faltan credenciales de WooCommerce REST API. Guárdalas en Configuración.' );
		}

		$url = add_query_arg( $query, $this->base_url . ltrim( $endpoint, '/' ) );

		$response = wp_remote_get( $url, [
			'timeout' => 30,
			'headers' => [
				'Authorization' => 'Basic ' . base64_encode( $this->key . ':' . $this->secret ),
				'Accept'        => 'application/json',
			],
		] );

		return $this->parse_response( $response );
	}

	/**
	 * POST/PUT helper.
	 */
	public function request( $method, $endpoint, $body = [], $query = [] ) {
		if ( ! $this->has_credentials() ) {
			return new WP_Error( 'b370_no_credentials', 'Faltan credenciales de WooCommerce REST API.' );
		}
		$url = add_query_arg( $query, $this->base_url . ltrim( $endpoint, '/' ) );

		$response = wp_remote_request( $url, [
			'method'  => strtoupper( $method ),
			'timeout' => 45,
			'headers' => [
				'Authorization' => 'Basic ' . base64_encode( $this->key . ':' . $this->secret ),
				'Content-Type'  => 'application/json',
				'Accept'        => 'application/json',
			],
			'body'    => wp_json_encode( $body ),
		] );

		return $this->parse_response( $response );
	}

	/**
	 * Decodifica la respuesta y normaliza errores HTTP.
	 */
	private function parse_response( $response ) {
		if ( is_wp_error( $response ) ) {
			return $response;
		}
		$code = (int) wp_remote_retrieve_response_code( $response );
		$body = wp_remote_retrieve_body( $response );
		$data = json_decode( $body, true );

		if ( $code < 200 || $code >= 300 ) {
			$msg = is_array( $data ) && isset( $data['message'] ) ? $data['message'] : "HTTP $code";
			return new WP_Error( 'b370_http_' . $code, $msg, [ 'status' => $code, 'body' => $data ] );
		}
		return is_array( $data ) ? $data : [];
	}

	/**
	 * Lista productos variables paginando hasta el final.
	 *
	 * @param int $per_page
	 * @return array|WP_Error  Lista plana de productos
	 */
	public function get_variable_products( $per_page = 100 ) {
		$all  = [];
		$page = 1;
		do {
			$batch = $this->get( 'products', [
				'type'     => 'variable',
				'status'   => 'publish',
				'per_page' => $per_page,
				'page'     => $page,
				'_fields'  => 'id,name,sku,permalink,variations',
			] );
			if ( is_wp_error( $batch ) ) {
				return $batch;
			}
			$all  = array_merge( $all, $batch );
			$page++;
		} while ( count( $batch ) === $per_page && $page < 50 ); // safety cap
		return $all;
	}

	/**
	 * Trae un producto concreto con sus variaciones resueltas.
	 */
	public function get_product_with_variations( $product_id ) {
		$product = $this->get( 'products/' . (int) $product_id );
		if ( is_wp_error( $product ) ) {
			return $product;
		}
		$variations = $this->get( 'products/' . (int) $product_id . '/variations', [ 'per_page' => 100 ] );
		if ( is_wp_error( $variations ) ) {
			return $variations;
		}
		$product['variations_resolved'] = $variations;
		return $product;
	}
}
