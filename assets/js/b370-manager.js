/**
 * B370 Manager — JS del admin
 *
 * Cubre:
 *  Módulo 2 (images.php)  — drag & drop por slot, subida AJAX, guardar slots
 *  Módulo 3 (quenti.php)  — drag & drop del Excel, parseo AJAX
 *  Módulo 4 (quenti.php)  — preview de variaciones
 *  Módulo 5 (quenti.php)  — ejecución chunked, log, undo
 */
(function ($) {
	'use strict';

	// ── Utilidades ──────────────────────────────────────────────

	function ajax(action, data, opts) {
		return $.ajax($.extend({
			url:    b370.ajax_url,
			method: 'POST',
			data:   $.extend({ action: action, nonce: b370.nonce }, data),
		}, opts || {}));
	}

	function showMsg($el, msg, type) {
		$el.text(msg)
		   .removeClass('b370-msg-ok b370-msg-error b370-msg-info')
		   .addClass('b370-msg-' + (type || 'info'))
		   .show();
	}

	// ════════════════════════════════════════════════════════════
	// MÓDULO 2 — Imágenes
	// ════════════════════════════════════════════════════════════

	function initImages() {
		if ( ! $('#b370-images-panel').length ) return;

		var productId = parseInt($('#b370-product-id').val(), 10);

		// Clic en dropzone abre el file input
		$(document).on('click', '.b370-slot-dropzone', function (e) {
			if ( $(e.target).hasClass('b370-slot-clear') ) return;
			$(this).find('.b370-slot-file').trigger('click');
		});

		// Drag & drop visual
		$(document).on('dragover dragenter', '.b370-slot-dropzone', function (e) {
			e.preventDefault();
			$(this).addClass('b370-drop-over');
		}).on('dragleave drop', '.b370-slot-dropzone', function (e) {
			$(this).removeClass('b370-drop-over');
		});

		$(document).on('drop', '.b370-slot-dropzone', function (e) {
			e.preventDefault();
			var files = e.originalEvent.dataTransfer.files;
			if ( files.length ) {
				uploadSlotFile($(this), files[0]);
			}
		});

		// Cambio en file input
		$(document).on('change', '.b370-slot-file', function () {
			if ( this.files.length ) {
				uploadSlotFile($(this).closest('.b370-slot-dropzone'), this.files[0]);
			}
		});

		// Botón Quitar
		$(document).on('click', '.b370-slot-clear', function (e) {
			e.stopPropagation();
			var slot = $(this).data('slot');
			var $dz  = $('.b370-slot-dropzone[data-slot="' + slot + '"]');
			$dz.html('<span class="b370-slot-placeholder">＋</span><input type="file" class="b370-slot-file" accept="image/*" style="display:none">')
			   .removeClass('has-image');
			$('.b370-slot-id[name="slots[' + slot + ']"]').val('0');
			$(this).remove();
		});

		function uploadSlotFile($dz, file) {
			var slot   = $dz.data('slot');
			var $status = $dz.closest('.b370-slot').find('.b370-slot-status');
			showMsg($status, 'Subiendo...', 'info');

			var fd = new FormData();
			fd.append('action',     'b370_upload_image');
			fd.append('nonce',      b370.nonce);
			fd.append('product_id', productId);
			fd.append('file',       file);

			$.ajax({
				url:         b370.ajax_url,
				method:      'POST',
				data:        fd,
				processData: false,
				contentType: false,
			}).done(function (res) {
				if ( ! res.success ) {
					showMsg($status, '❌ ' + res.data.message, 'error');
					return;
				}
				// Mostrar preview
				$dz.html('<img src="' + res.data.thumb + '" class="b370-slot-preview" alt="">'
					+ '<input type="file" class="b370-slot-file" accept="image/*" style="display:none">')
				   .addClass('has-image');
				$('.b370-slot-id[name="slots[' + slot + ']"]').val(res.data.id);
				showMsg($status, '✅ Lista', 'ok');
			}).fail(function () {
				showMsg($status, '❌ Error de red', 'error');
			});
		}

		// Guardar todos los slots
		$('#b370-btn-save-slots').on('click', function () {
			var $btn = $(this);
			var $sp  = $('#b370-slots-spinner');
			var $msg = $('#b370-slots-msg');

			var slots = {};
			$('.b370-slot-id').each(function () {
				var m = this.name.match(/slots\[(.+?)\]/);
				if ( m ) slots[m[1]] = $(this).val();
			});

			$btn.prop('disabled', true);
			$sp.show();

			ajax('b370_save_slots', { product_id: productId, slots: slots })
				.done(function (res) {
					if ( res.success ) {
						showMsg($msg, '✅ Imágenes guardadas', 'ok');
					} else {
						showMsg($msg, '❌ ' + res.data.message, 'error');
					}
				})
				.fail(function () { showMsg($msg, '❌ Error de red', 'error'); })
				.always(function () { $btn.prop('disabled', false); $sp.hide(); });
		});
	}

	// ════════════════════════════════════════════════════════════
	// MÓDULO 3 — Parsear Excel de Quenti
	// ════════════════════════════════════════════════════════════

	var parsedToken  = '';
	var parsedRows   = [];
	var previewItems = [];
	var sessionVarIds = [];   // IDs creados en esta sesión (para undo)

	function initQuenti() {
		if ( ! $('#b370-step2').length ) return;

		var $dz      = $('#b370-dropzone');
		var $input   = $('#b370-xlsx-input');
		var $status  = $('#b370-parse-status');

		// Clic en dropzone → abrir file picker
		$dz.on('click', function () { $input.trigger('click'); });

		$dz.on('dragover dragenter', function (e) {
			e.preventDefault();
			$dz.addClass('b370-drop-over');
		}).on('dragleave drop', function (e) {
			$dz.removeClass('b370-drop-over');
		});

		$dz.on('drop', function (e) {
			e.preventDefault();
			var files = e.originalEvent.dataTransfer.files;
			if ( files.length ) parseXlsx(files[0]);
		});

		$input.on('change', function () {
			if ( this.files.length ) parseXlsx(this.files[0]);
		});

		function parseXlsx(file) {
			$status.show().html('<span class="b370-status-info">⏳ Analizando el archivo...</span>');
			$('#b370-step3, #b370-step4, #b370-step5').hide();

			var fd = new FormData();
			fd.append('action', 'b370_parse_quenti');
			fd.append('nonce',  b370.nonce);
			fd.append('xlsx',   file);

			$.ajax({
				url: b370.ajax_url, method: 'POST',
				data: fd, processData: false, contentType: false,
			}).done(function (res) {
				if ( ! res.success ) {
					$status.html('<span class="b370-status-error">❌ ' + escHtml(res.data.message) + '</span>');
					return;
				}
				var d = res.data;
				parsedToken = d.token;
				parsedRows  = d.rows;
				$('#b370-token').val(parsedToken);

				$status.html(
					'<span class="b370-status-ok">✅ Archivo procesado</span> — ' +
					'<strong>' + d.parsed + '</strong> filas parseadas ' +
					'(<strong>' + d.skipped + '</strong> ignoradas) · ' +
					'<strong>' + d.families + '</strong> familias únicas'
				);
				$('#b370-step3').show();
			}).fail(function () {
				$status.html('<span class="b370-status-error">❌ Error de red al subir el archivo.</span>');
			});
		}
	}

	// ════════════════════════════════════════════════════════════
	// MÓDULO 4 — Preview de variaciones
	// ════════════════════════════════════════════════════════════

	function initPreview() {
		$('#b370-btn-preview').on('click', function () {
			var productId = parseInt($('#b370-product-id').val(), 10);
			var token     = $('#b370-token').val();
			if ( ! productId || ! token ) return;

			var tallas = [];
			$('.b370-talla-cb:checked').each(function () { tallas.push($(this).val()); });

			var prices = {};
			$('.b370-price-input').each(function () {
				prices[$(this).data('key')] = parseInt($(this).val(), 10) || 0;
			});

			var $btn = $(this).prop('disabled', true).text('Calculando...');

			ajax('b370_preview_vars', {
				product_id:      productId,
				token:           token,
				tallas:          tallas,
				skip_no_calidad: $('#b370-skip-no-calidad').is(':checked') ? 1 : 0,
			}).done(function (res) {
				if ( ! res.success ) {
					alert('❌ ' + res.data.message);
					return;
				}
				previewItems = res.data.items;
				renderPreview(res.data);
				$('#b370-step4').show();
				$('html, body').animate({ scrollTop: $('#b370-step4').offset().top - 32 }, 300);
			}).fail(function () {
				alert('Error de red al calcular el preview.');
			}).always(function () {
				$btn.prop('disabled', false).text('Ver preview de cambios');
			});
		});
	}

	function renderPreview(data) {
		var $body = $('#b370-preview-body').empty();
		var $sum  = $('#b370-preview-summary');

		$sum.html(
			'<span class="b370-badge b370-badge-create">➕ ' + data.creates + ' crear</span> ' +
			'<span class="b370-badge b370-badge-update">✏️ ' + data.updates + ' actualizar</span> ' +
			'<strong>' + (data.creates + data.updates) + ' cambios en total</strong>'
		);

		$.each(data.items, function (i, item) {
			var badge = item.action === 'create'
				? '<span class="b370-badge b370-badge-create">crear</span>'
				: '<span class="b370-badge b370-badge-update">actualizar</span>';

			$body.append(
				'<tr data-index="' + i + '">' +
				'<td><input type="checkbox" class="b370-item-cb" checked></td>' +
				'<td>' + badge + '</td>' +
				'<td>' + escHtml(item.talla)    + '</td>' +
				'<td>' + escHtml(item.calidad || '—') + '</td>' +
				'<td>' + escHtml(item.acabado)  + '</td>' +
				'<td><code>' + escHtml(item.sku) + '</code></td>' +
				'<td>' + item.stock + '</td>' +
				'<td>' + fmtPrice(item.price)   + '</td>' +
				'</tr>'
			);
		});

		updateRunBtn();
	}

	// Checkbox "seleccionar todos"
	$(document).on('change', '#b370-check-all', function () {
		$('.b370-item-cb').prop('checked', $(this).is(':checked'));
		updateRunBtn();
	});
	$(document).on('change', '.b370-item-cb', function () { updateRunBtn(); });

	function updateRunBtn() {
		var n = $('.b370-item-cb:checked').length;
		$('#b370-btn-run').text('▶ Ejecutar (' + n + ' cambios)');
	}

	// ════════════════════════════════════════════════════════════
	// MÓDULO 5 — Ejecución chunked
	// ════════════════════════════════════════════════════════════

	function initExec() {
		$('#b370-btn-run').on('click', function () {
			var productId = parseInt($('#b370-product-id').val(), 10);
			if ( ! productId ) return;

			// Recolectar solo los items marcados
			var selected = [];
			$('#b370-preview-body tr').each(function () {
				if ( $(this).find('.b370-item-cb').is(':checked') ) {
					var idx = parseInt($(this).data('index'), 10);
					selected.push(previewItems[idx]);
				}
			});

			if ( ! selected.length ) {
				alert('No hay cambios seleccionados.');
				return;
			}

			$('#b370-step5').show();
			$('html, body').animate({ scrollTop: $('#b370-step5').offset().top - 32 }, 300);
			$('#b370-log').empty();
			$('#b370-result-summary').hide();
			$('#b370-btn-run, #b370-btn-preview').prop('disabled', true);
			$('#b370-run-spinner').show();

			sessionVarIds = [];
			runChunk(productId, selected, 0, { ok: 0, fail: 0 });
		});

		$('#b370-btn-undo').on('click', function () {
			var productId = parseInt($('#b370-product-id').val(), 10);
			if ( ! sessionVarIds.length ) return;

			if ( ! confirm('¿Eliminar las ' + sessionVarIds.length + ' variaciones creadas en esta sesión?') ) return;

			ajax('b370_undo_session', { product_id: productId, var_ids: sessionVarIds })
				.done(function (res) {
					if ( res.success ) {
						appendLog('↩ Deshecho: ' + res.data.deleted.length + ' variaciones eliminadas.', 'info');
						sessionVarIds = [];
						$('#b370-btn-undo').hide();
					} else {
						appendLog('❌ Error al deshacer: ' + res.data.message, 'error');
					}
				});
		});
	}

	function runChunk(productId, items, offset, counts) {
		if ( offset >= items.length ) {
			finishExec(counts);
			return;
		}

		var item = items[offset];
		var pct  = Math.round((offset / items.length) * 100);
		$('#b370-progress-bar').css('width', pct + '%');
		$('#b370-progress-text').text(offset + ' / ' + items.length);

		ajax('b370_exec_one', {
			product_id: productId,
			item:       JSON.stringify(item),
		}).done(function (res) {
			if ( res.success ) {
				counts.ok++;
				var icon = res.data.action === 'created' ? '✅ creada' : '✏️ actualizada';
				appendLog(icon + ' — ' + item.talla + ' / ' + (item.calidad || '—') + ' / ' + item.acabado + ' (ID ' + res.data.id + ')', 'ok');
				if ( res.data.action === 'created' ) {
					sessionVarIds.push(res.data.id);
				}
			} else {
				counts.fail++;
				appendLog('❌ Error — ' + item.talla + ': ' + res.data.message, 'error');
			}
		}).fail(function () {
			counts.fail++;
			appendLog('❌ Error de red en ' + item.talla, 'error');
		}).always(function () {
			// Siguiente item (sin recursión síncrona — deja respirar al navegador)
			setTimeout(function () {
				runChunk(productId, items, offset + 1, counts);
			}, 80);
		});
	}

	function finishExec(counts) {
		$('#b370-progress-bar').css('width', '100%');
		$('#b370-progress-text').text('Completado');
		$('#b370-run-spinner').hide();
		$('#b370-btn-run, #b370-btn-preview').prop('disabled', false);

		var $sum = $('#b370-result-summary').show();
		$sum.html(
			'<strong>Resultado:</strong> ' +
			'<span class="b370-badge b370-badge-create">✅ ' + counts.ok + ' OK</span> ' +
			( counts.fail ? '<span class="b370-badge b370-badge-error">❌ ' + counts.fail + ' errores</span>' : '' )
		);

		if ( sessionVarIds.length ) {
			$('#b370-btn-undo').show();
		}
	}

	// ════════════════════════════════════════════════════════════
	// Helpers UI
	// ════════════════════════════════════════════════════════════

	function appendLog(msg, type) {
		var cls = type === 'ok' ? 'b370-log-ok' : ( type === 'error' ? 'b370-log-error' : 'b370-log-info' );
		var $log = $('#b370-log');
		$log.append('<div class="b370-log-line ' + cls + '">' + escHtml(msg) + '</div>');
		$log.scrollTop($log[0].scrollHeight);
	}

	function escHtml(str) {
		return String(str)
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;');
	}

	function fmtPrice(n) {
		if ( ! n ) return '—';
		return '$ ' + parseInt(n, 10).toLocaleString('es-CO');
	}

	// ════════════════════════════════════════════════════════════
	// Init
	// ════════════════════════════════════════════════════════════

	$(function () {
		initImages();
		initQuenti();
		initPreview();
		initExec();
	});

})(jQuery);
