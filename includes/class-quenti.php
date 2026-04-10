<?php
/**
 * Parser del Excel de Quenti.
 *
 * Estructura esperada del .xlsx (hoja única):
 *   A id_proucto  B nombre  C referencia  D codigo_barras ...
 *   H existencias ... J precioVenta_con_impuesto
 *
 * Regla de parsing del campo `nombre` (validada contra CUENTI INVENTARIO 6 ABRIL.xlsx):
 *   <CAMISETA|BUSO> DE <BASE> [<CALIDAD>] [CON PARCHES] /<TALLA>
 *
 * Decisiones acordadas con Juanjo:
 * - Tallas: S, M, L, XL, 2XL, 3XL (NO XXL).
 * - Calidad: 'version_fan' | 'tipo_original' | '1.1' | null
 * - Acabado: 'con_parches' solo se taggea explícito; la ausencia = 'sin_parches' implícito.
 * - RETRO es parte del nombre base, NO se extrae como atributo.
 * - Solo procesamos CAMISETA y BUSO (resto del inventario se ignora por ahora).
 *
 * Este archivo NO depende de WordPress, para poder probarse aisladamente con tests/test_quenti_parser.php.
 */

if ( ! defined( 'ABSPATH' ) && ! defined( 'B370_QUENTI_STANDALONE' ) ) {
	// Permite incluir el archivo desde el test CLI sin abortar.
	define( 'B370_QUENTI_STANDALONE', true );
}

class B370_Manager_Quenti {

	const CALIDAD_FAN      = 'version_fan';
	const CALIDAD_ORIGINAL = 'tipo_original';
	const CALIDAD_UNO_UNO  = '1.1';

	const ACABADO_CON = 'con_parches';
	const ACABADO_SIN = 'sin_parches';

	const TIPO_CAMISETA = 'camiseta';
	const TIPO_BUSO     = 'buso';

	/**
	 * Tallas válidas en WooCommerce (post-normalización).
	 * NOTA: 3XL/4XL/5XL/6XL y XS NO existen aún como opciones del atributo Tallas
	 * en b370sports.com. El Módulo 4 debe crearlas en la primera corrida si se
	 * detectan en el Excel. XXL se normaliza a 2XL.
	 */
	public static $valid_sizes = [ 'XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL', '6XL' ];

	/**
	 * Normaliza una cadena: mayúsculas, sin tildes, espacios colapsados, trim.
	 */
	public static function normalize( $s ) {
		if ( $s === null ) {
			return '';
		}
		$s = (string) $s;
		// Quitar BOM y espacios invisibles.
		$s = preg_replace( '/^\xEF\xBB\xBF/', '', $s );
		// Mayúsculas (multibyte).
		if ( function_exists( 'mb_strtoupper' ) ) {
			$s = mb_strtoupper( $s, 'UTF-8' );
		} else {
			$s = strtoupper( $s );
		}
		// Reemplazar vocales acentuadas y Ñ (tolerante a mojibake del Excel).
		$from = [ 'Á','É','Í','Ó','Ú','Ü','Ñ' ];
		$to   = [ 'A','E','I','O','U','U','N' ];
		$s    = str_replace( $from, $to, $s );
		// Colapsar espacios.
		$s = preg_replace( '/\s+/', ' ', $s );
		return trim( $s );
	}

	/**
	 * Normaliza una talla. 2XL y XXL se unifican en 2XL.
	 * Devuelve null si no es talla válida.
	 */
	public static function normalize_size( $raw ) {
		$s = self::normalize( $raw );
		$s = str_replace( ' ', '', $s );
		if ( $s === 'XXL' ) {
			$s = '2XL';
		}
		if ( $s === 'XXXL' ) {
			$s = '3XL';
		}
		return in_array( $s, self::$valid_sizes, true ) ? $s : null;
	}

	/**
	 * Parsea una fila del Excel (array asociativo o indexado).
	 *
	 * @param array $row  Fila con al menos: nombre, codigo_barras, existencias, precioVenta_con_impuesto
	 * @return array|null  Estructura parseada o null si la fila no es CAMISETA/BUSO con formato válido.
	 */
	public static function parse_row( array $row ) {
		// Permitir acceso por clave o por posición 0-indexada del Excel.
		$name      = $row['nombre']                   ?? ( $row[1]  ?? '' );
		$sku       = $row['codigo_barras']            ?? ( $row[3]  ?? '' );
		$stock     = $row['existencias']              ?? ( $row[7]  ?? 0 );
		$price     = $row['precioVenta_con_impuesto'] ?? ( $row[9]  ?? 0 );

		$parsed = self::parse_name( (string) $name );
		if ( $parsed === null ) {
			return null;
		}

		return array_merge( $parsed, [
			'sku'      => trim( (string) $sku ),
			'stock'    => (int) $stock,
			'precio'   => (int) $price,
			'raw_name' => (string) $name,
		] );
	}

	/**
	 * Parsea solo el campo nombre.
	 *
	 * @return array|null  ['tipo','base','calidad','acabado','talla'] o null si no matchea.
	 */
	public static function parse_name( $name ) {
		$n = self::normalize( $name );
		if ( $n === '' ) {
			return null;
		}

		// Debe empezar por CAMISETA o BUSO, con "DE"/"DEL" opcional.
		// Ejemplos reales: "CAMISETA DE ARSENAL...", "CAMISETA DEL DIM...",
		// "CAMISETA COLOMBIA LOCAL 2026 FAN..." (sin artículo).
		if ( ! preg_match( '/^(?P<head>CAMISETA|BUSO)(?:\s+DEL?)?\s+(?P<rest>.+)$/', $n, $mh ) ) {
			return null;
		}
		$tipo = ( $mh['head'] === 'BUSO' ) ? self::TIPO_BUSO : self::TIPO_CAMISETA;
		$rest = $mh['rest'];

		// Extraer talla del sufijo /<TALLA>.
		if ( ! preg_match( '#^(?P<body>.+?)\s*/\s*(?P<size>[A-Z0-9]+)\s*$#u', $rest, $m ) ) {
			return null;
		}
		$body = trim( $m['body'] );
		$size = self::normalize_size( $m['size'] );
		if ( $size === null ) {
			// Talla no soportada por el plugin (ej. numérica de guayos) → ignorar fila.
			return null;
		}

		// Detectar acabado ANTES de detectar calidad, porque "CON PARCHES"
		// suele ir pegado a "TIPO ORIGINAL".
		$acabado = self::ACABADO_SIN; // implícito por ausencia de token
		if ( preg_match( '/\bCON\s+PARCHES\b/', $body ) ) {
			$acabado = self::ACABADO_CON;
			$body    = trim( preg_replace( '/\bCON\s+PARCHES\b/', '', $body ) );
			$body    = preg_replace( '/\s+/', ' ', $body );
		}
		// Algunos productos llevan "SIN PARCHES" explícito (poco frecuente).
		if ( preg_match( '/\bSIN\s+PARCHES\b/', $body ) ) {
			$acabado = self::ACABADO_SIN;
			$body    = trim( preg_replace( '/\bSIN\s+PARCHES\b/', '', $body ) );
			$body    = preg_replace( '/\s+/', ' ', $body );
		}

		// Detectar calidad.
		// NOTA: en Quenti "VERSION FAN" es raro (56 filas); lo común es "FAN" solo (870 filas).
		// "1,1" con coma (256 filas) es equivalente a "1.1" — decimal colombiano.
		// Orden importa: "TIPO ORIGINAL" antes que otros, "1.1" antes que "FAN" porque
		// hay filas como "MANCHESTER UNITED 1,1 FAN" donde prima 1.1.
		$calidad  = null;
		$patterns = [
			self::CALIDAD_ORIGINAL => '/\bTIPO\s+ORIGINAL\b/',
			self::CALIDAD_UNO_UNO  => '/(?<![\d\.,])1[.,]1(?![\d])/',
			self::CALIDAD_FAN      => '/\bFAN\b/',
		];
		foreach ( $patterns as $code => $re ) {
			if ( preg_match( $re, $body ) ) {
				$calidad = $code;
				$body    = trim( preg_replace( $re, '', $body ) );
				$body    = preg_replace( '/\s+/', ' ', $body );
				break;
			}
		}

		// Regla de consistencia: solo TIPO ORIGINAL puede tener CON PARCHES.
		if ( $acabado === self::ACABADO_CON && $calidad !== self::CALIDAD_ORIGINAL ) {
			// Lo respetamos pero lo marcamos como sospechoso — el matcher del Módulo 3
			// decidirá si alertar a Beto.
			// (no abortamos el parse)
		}

		$base = trim( $body );
		if ( $base === '' ) {
			return null;
		}

		return [
			'tipo'    => $tipo,
			'base'    => $base,
			'calidad' => $calidad,
			'acabado' => $acabado,
			'talla'   => $size,
		];
	}

	/**
	 * Agrupa filas parseadas por "familia" (tipo + base), para sugerir el
	 * match contra el producto padre de WooCommerce seleccionado.
	 *
	 * @param array $parsed_rows  Lista de arrays devueltos por parse_row().
	 * @return array  [ familia_key => [ 'tipo','base','variaciones' => [...] ] ]
	 */
	public static function group_by_family( array $parsed_rows ) {
		$out = [];
		foreach ( $parsed_rows as $r ) {
			if ( ! $r ) {
				continue;
			}
			$key = $r['tipo'] . '|' . $r['base'];
			if ( ! isset( $out[ $key ] ) ) {
				$out[ $key ] = [
					'tipo'        => $r['tipo'],
					'base'        => $r['base'],
					'variaciones' => [],
				];
			}
			$out[ $key ]['variaciones'][] = [
				'calidad' => $r['calidad'],
				'acabado' => $r['acabado'],
				'talla'   => $r['talla'],
				'sku'     => $r['sku'],
				'stock'   => $r['stock'],
				'precio'  => $r['precio'],
			];
		}
		return $out;
	}

	/**
	 * Lee un archivo .xlsx usando PhpSpreadsheet si está disponible.
	 * Si no lo está, devuelve WP_Error con instrucciones.
	 *
	 * @return array|WP_Error  Lista de filas asociativas.
	 */
	public static function read_xlsx( $file_path ) {
		if ( ! class_exists( '\PhpOffice\PhpSpreadsheet\IOFactory' ) ) {
			if ( class_exists( 'WP_Error' ) ) {
				return new WP_Error(
					'b370_missing_phpspreadsheet',
					'Falta PhpSpreadsheet. Incluye el vendor/ preempaquetado del plugin.'
				);
			}
			return [];
		}
		$reader = \PhpOffice\PhpSpreadsheet\IOFactory::createReaderForFile( $file_path );
		$reader->setReadDataOnly( true );
		$spreadsheet = $reader->load( $file_path );
		$sheet       = $spreadsheet->getActiveSheet();
		$rows        = $sheet->toArray( null, true, true, false );

		if ( empty( $rows ) ) {
			return [];
		}
		$headers = array_map( 'strval', array_shift( $rows ) );
		$out     = [];
		foreach ( $rows as $r ) {
			$assoc = [];
			foreach ( $headers as $i => $h ) {
				$assoc[ $h ] = $r[ $i ] ?? null;
			}
			$out[] = $assoc;
		}
		return $out;
	}
}
