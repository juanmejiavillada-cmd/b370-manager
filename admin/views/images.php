<?php
/**
 * Vista: Imágenes — Módulo 2
 *
 * 4 slots: principal (main) + galería 2, 3, 4
 * Cada slot tiene su propia zona drag & drop.
 * Al guardar se asignan _thumbnail_id, _product_image_gallery y wavi_value.
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

// Slots actuales del producto seleccionado
$current_slots = $selected ? B370_Manager_Images::get_slots( $selected ) : [];

$slot_labels = [
	'main'      => 'Imagen principal',
	'gallery_2' => 'Galería 2',
	'gallery_3' => 'Galería 3',
	'gallery_4' => 'Galería 4',
];
?>

<h1>B370 Manager — Imágenes</h1>
<p class="b370-lead">Sube las imágenes del producto y asígnalas a cada slot (principal + galería).</p>

<?php if ( $error_msg ) : ?>
	<div class="notice notice-error"><p><?php echo wp_kses_post( $error_msg ); ?></p></div>
<?php endif; ?>

<?php if ( $products ) : ?>
<div class="b370-card">
	<h2>Selecciona el producto</h2>
	<form method="get">
		<input type="hidden" name="page" value="b370-manager-images" />
		<select name="product_id" class="b370-select">
			<option value="0">— Escoge un producto —</option>
			<?php foreach ( $products as $p ) :
				$id    = (int) $p['id'];
				$pname = isset( $p['name'] ) ? $p['name'] : '(sin nombre)';
			?>
				<option value="<?php echo esc_attr( $id ); ?>" <?php selected( $selected, $id ); ?>>
					#<?php echo esc_html( $id ); ?> — <?php echo esc_html( $pname ); ?>
				</option>
			<?php endforeach; ?>
		</select>
		<button type="submit" class="button button-primary">Seleccionar</button>
	</form>
</div>
<?php endif; ?>

<?php if ( $selected ) : ?>

<div class="b370-card" id="b370-images-panel">
	<h2>Imágenes del producto</h2>
	<p class="description">Arrastra un archivo o haz clic en cada slot para cambiar la imagen.</p>

	<div class="b370-slots-grid">
		<?php foreach ( $slot_labels as $slot => $label ) :
			$att_id   = $current_slots[ $slot ] ?? 0;
			$thumb    = $att_id ? B370_Manager_Images::thumb_url( $att_id, 'medium' ) : '';
		?>
		<div class="b370-slot" data-slot="<?php echo esc_attr( $slot ); ?>">
			<div class="b370-slot-label"><?php echo esc_html( $label ); ?></div>

			<div class="b370-slot-dropzone <?php echo $thumb ? 'has-image' : ''; ?>"
				 data-slot="<?php echo esc_attr( $slot ); ?>">

				<?php if ( $thumb ) : ?>
					<img src="<?php echo esc_url( $thumb ); ?>" class="b370-slot-preview" alt="">
				<?php else : ?>
					<span class="b370-slot-placeholder">＋</span>
				<?php endif; ?>

				<input type="file" class="b370-slot-file" accept="image/*" style="display:none">
			</div>

			<div class="b370-slot-status"></div>

			<input type="hidden" class="b370-slot-id"
				   name="slots[<?php echo esc_attr( $slot ); ?>]"
				   value="<?php echo esc_attr( $att_id ); ?>">

			<?php if ( $att_id ) : ?>
				<button class="button b370-slot-clear" data-slot="<?php echo esc_attr( $slot ); ?>">
					Quitar
				</button>
			<?php endif; ?>
		</div>
		<?php endforeach; ?>
	</div>

	<div style="margin-top:24px; display:flex; gap:12px; align-items:center">
		<button id="b370-btn-save-slots" class="button button-primary button-large">
			Guardar imágenes
		</button>
		<span class="spinner" id="b370-slots-spinner" style="float:none;display:none"></span>
		<span id="b370-slots-msg" class="b370-inline-msg"></span>
	</div>
</div>

<input type="hidden" id="b370-product-id" value="<?php echo esc_attr( $selected ); ?>">

<?php endif; ?>
