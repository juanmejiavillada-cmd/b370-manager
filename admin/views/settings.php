<?php
/**
 * Vista: Configuración
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

$url     = get_option( B370_OPT_WC_URL, 'https://b370sports.com' );
$key     = get_option( B370_OPT_WC_KEY, '' );
$secret  = get_option( B370_OPT_WC_SECRET, '' );
$precios = get_option( B370_OPT_PRECIOS, [] );

$labels = [
	'version_fan'   => 'Version Fan',
	'tipo_original' => 'Tipo Original',
	'uno_uno'       => '1.1',
	'retro'         => 'Retro',
	'buzo_an'       => 'Buzo AN',
	'gaban_an'      => 'Gabán AN',
	'con_parches'   => 'Con parches (extra)',
	'sin_parches'   => 'Sin parches (extra)',
];
?>

<h1>B370 Manager — Configuración</h1>
<p class="b370-lead">Credenciales de la tienda y precios por defecto para generar variaciones.</p>

<form method="post" action="">
	<?php wp_nonce_field( 'b370_save_settings', 'b370_settings_nonce' ); ?>

	<div class="b370-card">
		<h2>Conexión con WooCommerce</h2>
		<table class="form-table">
			<tr>
				<th><label for="b370_wc_url">URL de la tienda</label></th>
				<td><input type="url" id="b370_wc_url" name="b370_wc_url" class="regular-text" value="<?php echo esc_attr( $url ); ?>" placeholder="https://b370sports.com" required></td>
			</tr>
			<tr>
				<th><label for="b370_wc_key">Consumer Key</label></th>
				<td><input type="text" id="b370_wc_key" name="b370_wc_key" class="regular-text" value="<?php echo esc_attr( $key ); ?>" autocomplete="off"></td>
			</tr>
			<tr>
				<th><label for="b370_wc_secret">Consumer Secret</label></th>
				<td>
					<input type="password" id="b370_wc_secret" name="b370_wc_secret" class="regular-text" value="<?php echo esc_attr( $secret ); ?>" autocomplete="off">
					<p class="description">Se genera en WooCommerce → Ajustes → Avanzado → API REST. Usa permisos de <strong>Lectura/Escritura</strong>.</p>
				</td>
			</tr>
		</table>
	</div>

	<div class="b370-card">
		<h2>Precios por defecto (COP)</h2>
		<p class="description">Estos valores se usarán como sugerencia al crear variaciones. Se pueden sobreescribir en el Módulo 4 producto por producto.</p>
		<table class="form-table">
			<?php foreach ( $labels as $key_p => $label ) :
				$val = isset( $precios[ $key_p ] ) ? (int) $precios[ $key_p ] : 0; ?>
				<tr>
					<th><label for="b370_precios_<?php echo esc_attr( $key_p ); ?>"><?php echo esc_html( $label ); ?></label></th>
					<td>
						<input
							type="text"
							id="b370_precios_<?php echo esc_attr( $key_p ); ?>"
							name="b370_precios[<?php echo esc_attr( $key_p ); ?>]"
							value="<?php echo esc_attr( $val ); ?>"
							class="small-text"
							inputmode="numeric">
						<span class="description">COP</span>
					</td>
				</tr>
			<?php endforeach; ?>
		</table>
	</div>

	<p><button type="submit" class="button button-primary button-large">Guardar configuración</button></p>
</form>
