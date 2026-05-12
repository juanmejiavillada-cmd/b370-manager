<?php
/**
 * Vista: Importar Quenti — Módulos 3, 4 y 5
 *
 * Flujo:
 *   Paso 1 (PHP)   → seleccionar producto
 *   Paso 2 (AJAX)  → subir Excel → parsear → ver familias
 *   Paso 3 (AJAX)  → configurar tallas / parches / precios → preview tabla
 *   Paso 4 (AJAX)  → ejecutar chunk a chunk → log en tiempo real
 *   Botón Deshacer → elimina las variaciones creadas en la sesión
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

$client   = new B370_Manager_Products();
$selected = isset( $_GET['product_id'] ) ? (int) $_GET['product_id'] : 0;
$products = [];
$error_msg = '';

if ( ! $client->has_credentials() ) {
	$error_msg = 'Guarda las credenciales en <a href="' . esc_url( admin_url( 'admin.php?page=b370-manager-settings' ) ) . '">Configuración</a> primero.';
} else {
	$products = $client->get_variable_products();
	if ( is_wp_error( $products ) ) {
		$error_msg = esc_html( $products->get_error_message() );
		$products  = [];
	}
}

$precios = get_option( B370_OPT_PRECIOS, [] );
$all_sizes = [ 'XS','S','M','L','XL','2XL','3XL','4XL','5XL','6XL' ];
?>

<h1>B370 Manager — Importar Quenti</h1>
<p class="b370-lead">Sube el Excel de Quenti, revisa el cruce y ejecuta la actualización de variaciones.</p>

<?php if ( $error_msg ) : ?>
	<div class="notice notice-error"><p><?php echo wp_kses_post( $error_msg ); ?></p></div>
<?php endif; ?>

<?php if ( $products ) : ?>
<!-- ════════════════════════════════════════════════════════
     PASO 1 — Selector de producto
════════════════════════════════════════════════════════ -->
<div class="b370-card" id="b370-step1">
	<h2>Paso 1 — Selecciona el producto</h2>
	<form method="get" id="b370-form-product">
		<input type="hidden" name="page" value="b370-manager-quenti" />
		<select name="product_id" id="b370-product-select" class="b370-select">
			<option value="0">— Escoge un producto —</option>
			<?php foreach ( $products as $p ) :
				$id     = (int) $p['id'];
				$pname  = isset( $p['name'] ) ? $p['name'] : '(sin nombre)';
				$vcount = isset( $p['variations'] ) && is_array( $p['variations'] ) ? count( $p['variations'] ) : 0;
			?>
				<option value="<?php echo esc_attr( $id ); ?>" <?php selected( $selected, $id ); ?>>
					#<?php echo esc_html( $id ); ?> — <?php echo esc_html( $pname ); ?> (<?php echo (int) $vcount; ?> var.)
				</option>
			<?php endforeach; ?>
		</select>
		<button type="submit" class="button button-primary">Seleccionar</button>
	</form>
</div>
<?php endif; ?>

<?php if ( $selected ) : ?>

<!-- ════════════════════════════════════════════════════════
     PASO 2 — Subir Excel de Quenti
════════════════════════════════════════════════════════ -->
<div class="b370-card" id="b370-step2">
	<h2>Paso 2 — Sube el Excel de Quenti</h2>
	<p class="description">Exporta el inventario desde Quenti como <code>.xlsx</code> y súbelo aquí.</p>

	<div id="b370-dropzone" class="b370-dropzone">
		<span class="b370-dropzone-icon">📂</span>
		<p>Arrastra el <code>.xlsx</code> aquí o haz clic para elegirlo</p>
		<input type="file" id="b370-xlsx-input" accept=".xlsx,.xls" style="display:none">
	</div>

	<div id="b370-parse-status" class="b370-status" style="display:none"></div>
</div>

<!-- ════════════════════════════════════════════════════════
     PASO 3 — Configurar + Preview
════════════════════════════════════════════════════════ -->
<div class="b370-card" id="b370-step3" style="display:none">
	<h2>Paso 3 — Configura y revisa el preview</h2>

	<div class="b370-config-grid">
		<div class="b370-config-col">
			<strong>Tallas a incluir</strong>
			<p class="description">Deja todo sin marcar para incluir todas.</p>
			<div class="b370-checkboxes" id="b370-talla-checks">
				<?php foreach ( $all_sizes as $sz ) : ?>
					<label class="b370-checkbox-label">
						<input type="checkbox" class="b370-talla-cb" value="<?php echo esc_attr( $sz ); ?>">
						<?php echo esc_html( $sz ); ?>
					</label>
				<?php endforeach; ?>
			</div>
		</div>

		<div class="b370-config-col">
			<strong>Opciones</strong>
			<label class="b370-checkbox-label" style="margin-top:10px">
				<input type="checkbox" id="b370-skip-no-calidad">
				Omitir filas sin calidad identificada
			</label>
		</div>

		<div class="b370-config-col">
			<strong>Precios (COP)</strong>
			<table class="b370-mini-table">
				<?php
				$price_labels = [
					'version_fan'   => 'Version Fan',
					'tipo_original' => 'Tipo Original',
					'uno_uno'       => '1.1',
					'retro'         => 'Retro',
				];
				foreach ( $price_labels as $pk => $plabel ) :
					$pval = isset( $precios[ $pk ] ) ? (int) $precios[ $pk ] : 0;
				?>
				<tr>
					<td><?php echo esc_html( $plabel ); ?></td>
					<td><input type="number" class="b370-price-input small-text" data-key="<?php echo esc_attr( $pk ); ?>" value="<?php echo esc_attr( $pval ); ?>" min="0" step="1000"></td>
				</tr>
				<?php endforeach; ?>
			</table>
		</div>
	</div>

	<button id="b370-btn-preview" class="button button-secondary" style="margin-top:16px">
		Ver preview de cambios
	</button>
</div>

<!-- ════════════════════════════════════════════════════════
     PASO 4 — Tabla de preview + Ejecutar
════════════════════════════════════════════════════════ -->
<div class="b370-card" id="b370-step4" style="display:none">
	<h2>Paso 4 — Preview de cambios</h2>

	<div id="b370-preview-summary" class="b370-preview-summary"></div>

	<div class="b370-table-wrap">
		<table class="widefat striped b370-preview-table" id="b370-preview-table">
			<thead>
				<tr>
					<th><input type="checkbox" id="b370-check-all" checked></th>
					<th>Acción</th>
					<th>Talla</th>
					<th>Calidad</th>
					<th>Acabado</th>
					<th>SKU</th>
					<th>Stock</th>
					<th>Precio</th>
				</tr>
			</thead>
			<tbody id="b370-preview-body"></tbody>
		</table>
	</div>

	<div style="margin-top:16px; display:flex; gap:12px; align-items:center; flex-wrap:wrap">
		<button id="b370-btn-run" class="button button-primary button-large">
			▶ Ejecutar (0 cambios)
		</button>
		<button id="b370-btn-undo" class="button button-secondary" style="display:none">
			↩ Deshacer última sesión
		</button>
		<span id="b370-run-spinner" class="spinner" style="float:none;display:none"></span>
	</div>
</div>

<!-- ════════════════════════════════════════════════════════
     PASO 5 — Log de ejecución
════════════════════════════════════════════════════════ -->
<div class="b370-card" id="b370-step5" style="display:none">
	<h2>Paso 5 — Ejecución</h2>

	<div class="b370-progress-bar-wrap">
		<div class="b370-progress-bar" id="b370-progress-bar"></div>
	</div>
	<p id="b370-progress-text" class="b370-progress-text">0 / 0</p>

	<div id="b370-log" class="b370-log"></div>

	<div id="b370-result-summary" style="display:none; margin-top:16px"></div>
</div>

<input type="hidden" id="b370-product-id" value="<?php echo esc_attr( $selected ); ?>">
<input type="hidden" id="b370-token" value="">

<?php endif; ?>
