<?php
/**
 * Vista: Productos (Módulo 1 — Selector de producto)
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

$client    = new B370_Manager_Products();
$selected  = isset( $_GET['product_id'] ) ? (int) $_GET['product_id'] : 0;
$error_msg = '';
$products  = [];

if ( ! $client->has_credentials() ) {
	$error_msg = 'Aún no has guardado las credenciales de WooCommerce. Ve a <a href="' . esc_url( admin_url( 'admin.php?page=b370-manager-settings' ) ) . '">Configuración</a> y pégalas ahí.';
} else {
	$products = $client->get_variable_products();
	if ( is_wp_error( $products ) ) {
		$error_msg = 'No pude conectar con WooCommerce: ' . esc_html( $products->get_error_message() );
		$products  = [];
	}
}

$selected_product = null;
if ( $selected && ! is_wp_error( $products ) ) {
	$full = $client->get_product_with_variations( $selected );
	if ( ! is_wp_error( $full ) ) {
		$selected_product = $full;
	} else {
		$error_msg = 'No pude cargar el producto: ' . esc_html( $full->get_error_message() );
	}
}
?>

<h1>B370 Manager — Productos</h1>
<p class="b370-lead">Elige un producto variable de la tienda para gestionar sus variaciones, imágenes y stock.</p>

<?php if ( $error_msg ) : ?>
	<div class="notice notice-error"><p><?php echo wp_kses_post( $error_msg ); ?></p></div>
<?php endif; ?>

<?php if ( $products ) : ?>
	<form method="get" class="b370-card">
		<input type="hidden" name="page" value="b370-manager" />
		<label for="b370-product-select"><strong>Producto:</strong></label>
		<select name="product_id" id="b370-product-select" class="b370-select">
			<option value="0">— Escoge un producto —</option>
			<?php foreach ( $products as $p ) :
				$id   = (int) $p['id'];
				$name = isset( $p['name'] ) ? $p['name'] : '(sin nombre)';
				$vcount = isset( $p['variations'] ) && is_array( $p['variations'] ) ? count( $p['variations'] ) : 0;
				?>
				<option value="<?php echo esc_attr( $id ); ?>" <?php selected( $selected, $id ); ?>>
					#<?php echo esc_html( $id ); ?> — <?php echo esc_html( $name ); ?> (<?php echo (int) $vcount; ?> variaciones)
				</option>
			<?php endforeach; ?>
		</select>
		<button type="submit" class="button button-primary">Gestionar producto</button>
	</form>
<?php endif; ?>

<?php if ( $selected_product ) : ?>
	<div class="b370-card">
		<h2><?php echo esc_html( $selected_product['name'] ); ?></h2>
		<p>
			<strong>ID:</strong> <?php echo (int) $selected_product['id']; ?> &nbsp;·&nbsp;
			<strong>Estado:</strong> <?php echo esc_html( $selected_product['status'] ?? '-' ); ?> &nbsp;·&nbsp;
			<a href="<?php echo esc_url( $selected_product['permalink'] ?? '#' ); ?>" target="_blank">Ver en la tienda ↗</a>
		</p>

		<h3>Variaciones existentes (<?php echo count( $selected_product['variations_resolved'] ?? [] ); ?>)</h3>
		<?php if ( empty( $selected_product['variations_resolved'] ) ) : ?>
			<p><em>Este producto aún no tiene variaciones.</em></p>
		<?php else : ?>
			<table class="widefat striped b370-variations">
				<thead>
					<tr>
						<th>ID</th>
						<th>Atributos</th>
						<th>SKU</th>
						<th>Precio</th>
						<th>Stock</th>
					</tr>
				</thead>
				<tbody>
				<?php foreach ( $selected_product['variations_resolved'] as $v ) :
					$attrs = [];
					if ( ! empty( $v['attributes'] ) && is_array( $v['attributes'] ) ) {
						foreach ( $v['attributes'] as $a ) {
							$attrs[] = ( $a['name'] ?? '' ) . ': ' . ( $a['option'] ?? '' );
						}
					}
					?>
					<tr>
						<td><?php echo (int) $v['id']; ?></td>
						<td><?php echo esc_html( implode( ' / ', $attrs ) ); ?></td>
						<td><code><?php echo esc_html( $v['sku'] ?? '' ); ?></code></td>
						<td><?php echo esc_html( $v['price'] ?? '' ); ?></td>
						<td><?php echo esc_html( (string) ( $v['stock_quantity'] ?? '—' ) ); ?></td>
					</tr>
				<?php endforeach; ?>
				</tbody>
			</table>
		<?php endif; ?>

		<p class="b370-next">
			Siguiente paso: <a href="<?php echo esc_url( admin_url( 'admin.php?page=b370-manager-images&product_id=' . (int) $selected_product['id'] ) ); ?>">Subir imágenes</a>
			o <a href="<?php echo esc_url( admin_url( 'admin.php?page=b370-manager-quenti&product_id=' . (int) $selected_product['id'] ) ); ?>">Importar stock desde Quenti</a>.
		</p>
	</div>
<?php endif; ?>
