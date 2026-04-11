<?php
/**
 * Lector de archivos .xlsx sin dependencias externas.
 *
 * Un .xlsx es un archivo ZIP que contiene XML. Esta clase extrae las filas
 * de la primera hoja usando solo funciones de PHP estándar (ZipArchive + SimpleXML).
 *
 * Limitaciones intencionadas (suficientes para el Excel de Quenti):
 *  - Lee solo la primera hoja (Sheet1 / hoja activa)
 *  - Soporta celdas de texto (shared strings) y numéricas
 *  - No lee fórmulas ni formatos de fecha complejos
 *  - Requiere ext-zip y ext-simplexml (disponibles en cualquier Hostinger/cPanel)
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class B370_Xlsx_Reader {

	/**
	 * Lee un archivo .xlsx y devuelve un array de filas asociativas.
	 * La primera fila se usa como cabeceras.
	 *
	 * @param string $file_path  Ruta absoluta al .xlsx
	 * @return array|WP_Error
	 */
	public static function read( $file_path ) {
		if ( ! file_exists( $file_path ) ) {
			return new WP_Error( 'b370_xlsx_not_found', 'No se encontró el archivo: ' . $file_path );
		}

		if ( ! class_exists( 'ZipArchive' ) ) {
			return new WP_Error( 'b370_no_zip', 'La extensión ZipArchive no está disponible en este servidor.' );
		}

		$zip = new ZipArchive();
		if ( $zip->open( $file_path ) !== true ) {
			return new WP_Error( 'b370_xlsx_open', 'No se pudo abrir el archivo .xlsx.' );
		}

		// ── 1. Shared strings (texto de las celdas) ──────────────
		$shared_strings = [];
		$ss_xml = $zip->getFromName( 'xl/sharedStrings.xml' );
		if ( $ss_xml !== false ) {
			$ss = @simplexml_load_string( $ss_xml );
			if ( $ss ) {
				foreach ( $ss->si as $si ) {
					// Puede ser <t> directo o varios <r><t> (rich text)
					if ( isset( $si->t ) ) {
						$shared_strings[] = (string) $si->t;
					} else {
						$text = '';
						foreach ( $si->r as $r ) {
							$text .= (string) $r->t;
						}
						$shared_strings[] = $text;
					}
				}
			}
		}

		// ── 2. Encontrar la primera hoja ─────────────────────────
		$sheet_path = self::first_sheet_path( $zip );
		if ( ! $sheet_path ) {
			$zip->close();
			return new WP_Error( 'b370_xlsx_no_sheet', 'No se encontró ninguna hoja en el archivo.' );
		}

		$sheet_xml = $zip->getFromName( $sheet_path );
		$zip->close();

		if ( $sheet_xml === false ) {
			return new WP_Error( 'b370_xlsx_sheet_read', 'No se pudo leer la hoja del archivo.' );
		}

		// ── 3. Parsear la hoja ───────────────────────────────────
		$sheet = @simplexml_load_string( $sheet_xml );
		if ( ! $sheet ) {
			return new WP_Error( 'b370_xlsx_parse', 'No se pudo parsear el XML de la hoja.' );
		}

		// Registrar namespace si existe
		$ns = $sheet->getNamespaces( true );
		$default_ns = isset( $ns[''] ) ? $ns[''] : '';

		$raw_rows = [];
		$sheet_data = $default_ns
			? $sheet->children( $default_ns )->sheetData
			: $sheet->sheetData;

		if ( ! $sheet_data ) {
			return [];
		}

		foreach ( $sheet_data->row as $row ) {
			$row_data = [];
			$max_col  = 0;

			foreach ( $row->c as $cell ) {
				$col_idx = self::col_index( (string) $cell['r'] );
				$type    = (string) $cell['t'];
				$val     = isset( $cell->v ) ? (string) $cell->v : '';

				if ( $type === 's' && $val !== '' ) {
					// Shared string
					$val = $shared_strings[ (int) $val ] ?? '';
				} elseif ( $type === 'inlineStr' && isset( $cell->is->t ) ) {
					$val = (string) $cell->is->t;
				}
				// Numérico, booleano, error → val ya es el string del número

				$row_data[ $col_idx ] = $val;
				$max_col = max( $max_col, $col_idx );
			}

			// Rellenar huecos con ''
			$full_row = [];
			for ( $i = 0; $i <= $max_col; $i++ ) {
				$full_row[] = $row_data[ $i ] ?? '';
			}
			$raw_rows[] = $full_row;
		}

		if ( empty( $raw_rows ) ) {
			return [];
		}

		// ── 4. Primera fila = cabeceras ──────────────────────────
		$headers = array_map( 'trim', array_shift( $raw_rows ) );
		$out     = [];

		foreach ( $raw_rows as $r ) {
			$assoc = [];
			foreach ( $headers as $i => $h ) {
				$assoc[ $h ] = $r[ $i ] ?? '';
			}
			$out[] = $assoc;
		}

		return $out;
	}

	// ─────────────────────────────────────────────────────────────
	// Helpers privados
	// ─────────────────────────────────────────────────────────────

	/**
	 * Localiza la ruta de la primera hoja dentro del ZIP.
	 * Lee workbook.xml.rels para seguir los IDs de relación.
	 */
	private static function first_sheet_path( ZipArchive $zip ) {
		// Intentar ruta directa más común primero
		$candidates = [ 'xl/worksheets/sheet1.xml', 'xl/worksheets/Sheet1.xml' ];
		foreach ( $candidates as $c ) {
			if ( $zip->locateName( $c ) !== false ) {
				return $c;
			}
		}

		// Parsear workbook.xml.rels
		$rels_xml = $zip->getFromName( 'xl/_rels/workbook.xml.rels' );
		if ( $rels_xml === false ) {
			return null;
		}
		$rels = @simplexml_load_string( $rels_xml );
		if ( ! $rels ) {
			return null;
		}

		foreach ( $rels->Relationship as $rel ) {
			$type = (string) $rel['Type'];
			if ( strpos( $type, 'worksheet' ) !== false ) {
				$target = 'xl/' . ltrim( (string) $rel['Target'], '/' );
				if ( $zip->locateName( $target ) !== false ) {
					return $target;
				}
			}
		}

		return null;
	}

	/**
	 * Convierte la referencia de celda (ej. "B3", "AA1") en índice de columna 0-based.
	 */
	private static function col_index( $cell_ref ) {
		// Extraer solo letras (columna)
		preg_match( '/^([A-Z]+)/', strtoupper( $cell_ref ), $m );
		if ( empty( $m[1] ) ) {
			return 0;
		}
		$letters = $m[1];
		$idx     = 0;
		$len     = strlen( $letters );
		for ( $i = 0; $i < $len; $i++ ) {
			$idx = $idx * 26 + ( ord( $letters[ $i ] ) - ord( 'A' ) + 1 );
		}
		return $idx - 1;
	}
}
