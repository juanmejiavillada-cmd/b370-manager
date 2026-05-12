#!/usr/bin/env python3
"""Deploy b370-urgency.php v1.3 — adds 4 mental triggers."""
import paramiko, os, sys
from dotenv import load_dotenv

load_dotenv()

URGENCY_PHP = r'''<?php
/**
 * Plugin Name: B370 Urgency Elements
 * Description: WhatsApp button, delivery strip, countdown, social proof, stock urgency.
 * Version: 1.3
 */
if (!defined('ABSPATH')) exit;

// ── 1. WhatsApp button — after full form ──
add_action('woocommerce_after_add_to_cart_form', function() {
    global $product;
    if (!$product) return;
    $msg     = rawurlencode('Hola B370, quiero pedir: ' . $product->get_name());
    $wa_link = 'https://wa.me/573218159715?text=' . $msg;
    echo '<a href="' . esc_url($wa_link) . '" target="_blank" rel="noopener" class="b370-wa-btn">'
       . '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12.004 2.003A9.997 9.997 0 002 12c0 1.763.463 3.417 1.27 4.855L2 22l5.282-1.243A9.953 9.953 0 0012.004 22C17.524 22 22 17.523 22 12c0-5.522-4.476-9.997-9.996-9.997zm0 18.188a8.18 8.18 0 01-4.17-1.143l-.299-.178-3.134.737.764-3.038-.195-.311A8.158 8.158 0 013.818 12c0-4.519 3.667-8.185 8.186-8.185 4.519 0 8.186 3.666 8.186 8.185 0 4.52-3.667 8.186-8.186 8.186z"/></svg>'
       . ' Pedir por WhatsApp'
       . '</a>';
}, 10);

// ── 2. Delivery strip + shipping countdown ──
add_action('woocommerce_after_add_to_cart_form', function() {
    echo '<div class="b370-delivery-strip">'
       . '<span class="b370-ds-item"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg> Llega en 2-5 d&iacute;as</span>'
       . '<span class="b370-ds-sep">&bull;</span>'
       . '<span class="b370-ds-item"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg> Paga al recibir</span>'
       . '<span class="b370-ds-sep">&bull;</span>'
       . '<span class="b370-ds-item"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"/></svg> Env&iacute;o a todo Colombia</span>'
       . '</div>'
       . '<div class="b370-ship-countdown">'
       . '<svg class="b370-clock" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
       . '<span id="b370-ship-msg"></span>'
       . '</div>';
}, 20);

// ── 3. Social proof: active viewers ──
add_action('woocommerce_single_product_summary', function() {
    echo '<div class="b370-viewers">'
       . '<span class="b370-dot"></span>'
       . '<span id="b370-v-count">7</span> personas est&aacute;n viendo esto ahora'
       . '</div>';
}, 22);

// ── 4. Stock urgency — simple + variable ──
add_action('woocommerce_single_product_summary', function() {
    global $product;
    if (!$product) return;

    // Simple product
    if ($product->is_type('simple') && $product->managing_stock()) {
        $qty = (int) $product->get_stock_quantity();
        if ($qty > 0 && $qty <= 10) {
            if ($qty === 1)     $msg = '&iexcl;Queda solo 1! Pide ahora antes de que se agote.';
            elseif ($qty <= 3)  $msg = '&iexcl;Solo quedan ' . $qty . '! Se est&aacute;n agotando.';
            else                $msg = '&iexcl;Quedan ' . $qty . ' disponibles!';
            echo '<p class="b370-stock-urgency">' . $msg . '</p>';
        }
    }

    // Variable product: encode per-variation stock for JS
    if ($product->is_type('variable')) {
        $stock_data = [];
        foreach ($product->get_available_variations() as $v) {
            $vid = $v['variation_id'];
            $var_obj = wc_get_product($vid);
            if ($var_obj && $var_obj->managing_stock()) {
                $stock_data[$vid] = (int) $var_obj->get_stock_quantity();
            }
        }
        if (!empty($stock_data)) {
            echo '<script>window.b370StockData=' . wp_json_encode($stock_data) . ';</script>';
        }
        // Placeholder shown by JS when a size is selected
        echo '<p class="b370-stock-urgency" id="b370-var-stock" style="display:none"></p>';
    }
}, 25);

// ── 5. JS (footer) ──
add_action('wp_footer', function() {
    if (!is_product()) return;
    global $product;
    $prod_name = $product ? wp_json_encode($product->get_name()) : '""';
    ?>
<script>
(function(){
    // --- Active viewers ---
    var vEl = document.getElementById('b370-v-count');
    if (vEl) {
        var v = Math.floor(Math.random() * 9) + 3;
        vEl.textContent = v;
        setInterval(function() {
            v = Math.max(2, Math.min(15, v + (Math.random() < 0.5 ? 1 : -1)));
            vEl.textContent = v;
        }, Math.floor(Math.random() * 20000) + 25000);
    }

    // --- Shipping countdown ---
    var shipEl = document.getElementById('b370-ship-msg');
    if (shipEl) {
        function pad(n) { return n < 10 ? '0' + n : '' + n; }
        function tick() {
            var now  = new Date();
            var col  = new Date(now.toLocaleString('en-US', {timeZone:'America/Bogota'}));
            var day  = col.getDay();
            var h    = col.getHours();
            var m    = col.getMinutes();
            var s    = col.getSeconds();
            if (day === 0 || day === 6) {
                shipEl.textContent = 'Los pedidos del fin de semana se despachan el lunes.';
                return;
            }
            if (h >= 16) {
                shipEl.innerHTML = 'Pedido hoy — lo despachamos <strong>mañana temprano</strong>.';
                return;
            }
            var total = 16 * 3600 - (h * 3600 + m * 60 + s);
            var hh = Math.floor(total / 3600);
            var mm = Math.floor((total % 3600) / 60);
            var ss = total % 60;
            shipEl.innerHTML = 'Pide en las próximas <strong>' + hh + ':' + pad(mm) + ':' + pad(ss) + '</strong> y lo despachamos <strong>HOY</strong>';
        }
        tick();
        setInterval(tick, 1000);
    }

    // --- Variation stock ---
    var varEl = document.getElementById('b370-var-stock');
    if (varEl && window.b370StockData && window.jQuery) {
        jQuery(document).on('found_variation', function(e, variation) {
            var qty = window.b370StockData[variation.variation_id];
            if (qty !== undefined && qty > 0 && qty <= 10) {
                varEl.textContent = qty === 1
                    ? '¡Queda solo 1 en esta talla! Pide ahora.'
                    : qty <= 3
                        ? '¡Solo quedan ' + qty + ' en esta talla! Se agotan.'
                        : '¡Quedan ' + qty + ' en esta talla!';
                varEl.style.display = 'block';
            } else {
                varEl.style.display = 'none';
            }
        });
        jQuery(document).on('reset_data', function() { varEl.style.display = 'none'; });
    }

    // --- Recent sale toast ---
    var cities = ['Medellín','Bogotá','Cali','Barranquilla','Cartagena','Bucaramanga','Manizales','Pereira','Ibagué','Montería','Santa Marta','Cúcuta'];
    var prod = <?php echo $prod_name; ?>;
    function showToast() {
        var city = cities[Math.floor(Math.random() * cities.length)];
        var el = document.getElementById('b370-toast');
        if (!el) return;
        document.getElementById('b370-toast-city').textContent = city;
        el.classList.add('b370-toast-show');
        setTimeout(function() { el.classList.remove('b370-toast-show'); }, 5500);
        setTimeout(showToast, 80000 + Math.floor(Math.random() * 70000));
    }
    setTimeout(showToast, 9000 + Math.floor(Math.random() * 8000));
})();
</script>
<div id="b370-toast" class="b370-toast" role="status" aria-live="polite">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="#25D366" flex-shrink="0" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12.004 2.003A9.997 9.997 0 002 12c0 1.763.463 3.417 1.27 4.855L2 22l5.282-1.243A9.953 9.953 0 0012.004 22C17.524 22 22 17.523 22 12c0-5.522-4.476-9.997-9.996-9.997zm0 18.188a8.18 8.18 0 01-4.17-1.143l-.299-.178-3.134.737.764-3.038-.195-.311A8.158 8.158 0 013.818 12c0-4.519 3.667-8.185 8.186-8.185 4.519 0 8.186 3.666 8.186 8.185 0 4.52-3.667 8.186-8.186 8.186z"/></svg>
    <div class="b370-toast-body">
        <span>Alguien en <strong id="b370-toast-city"></strong> acaba de pedir esta camiseta</span>
        <small>Hace un momento</small>
    </div>
    <button class="b370-toast-close" onclick="document.getElementById('b370-toast').classList.remove('b370-toast-show')" aria-label="Cerrar">&times;</button>
</div>
    <?php
}, 20);

// ── 6. CSS ──
add_action('wp_head', function() {
    if (!is_product()) return;
    ?>
<style>
/* WhatsApp button */
.b370-wa-btn{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;background:#25D366;color:#fff!important;font-weight:700;font-size:1rem;padding:14px 20px;border-radius:8px;text-decoration:none!important;margin:12px 0 0;min-height:48px;transition:background .2s,transform .15s;box-sizing:border-box}
.b370-wa-btn:hover{background:#1da855;transform:translateY(-1px);color:#fff!important}
.b370-wa-btn svg{flex-shrink:0}

/* Delivery strip */
.b370-delivery-strip{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;font-size:.78rem;color:#555;margin:10px 0 4px}
.b370-ds-item{display:inline-flex;align-items:center;gap:4px;white-space:nowrap}
.b370-ds-item svg{flex-shrink:0;color:#006A4E}
.b370-ds-sep{color:#ccc;font-size:.6rem}

/* Shipping countdown */
.b370-ship-countdown{display:flex;align-items:center;gap:6px;font-size:.8rem;color:#1b5e20;background:#e8f5e9;border-radius:6px;padding:7px 11px;margin:4px 0 8px}
.b370-clock{flex-shrink:0;color:#2e7d32}
.b370-ship-countdown strong{color:#1b5e20}

/* Active viewers */
.b370-viewers{display:flex;align-items:center;gap:7px;font-size:.8rem;color:#555;margin:0 0 8px}
.b370-dot{width:8px;height:8px;border-radius:50%;background:#e74c3c;animation:b370pulse 1.6s ease-in-out infinite;flex-shrink:0}
@keyframes b370pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.8)}}

/* Stock urgency */
.b370-stock-urgency{color:#c0392b;font-weight:700;font-size:.92rem;margin:6px 0;padding:7px 12px;background:#fdf3f3;border-left:3px solid #e74c3c;border-radius:4px}

/* Recent sale toast */
.b370-toast{position:fixed;bottom:22px;left:18px;z-index:99999;background:#fff;border:1px solid #e5e5e5;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.13);padding:12px 14px;display:flex;align-items:flex-start;gap:10px;max-width:270px;width:calc(100vw - 36px);transform:translateY(130%);transition:transform .45s cubic-bezier(.175,.885,.32,1.275);pointer-events:none}
.b370-toast.b370-toast-show{transform:translateY(0);pointer-events:auto}
.b370-toast-body{flex:1;display:flex;flex-direction:column;gap:2px}
.b370-toast-body span{font-size:.8rem;font-weight:500;color:#222;line-height:1.35}
.b370-toast-body strong{font-weight:700}
.b370-toast-body small{font-size:.7rem;color:#999}
.b370-toast-close{background:none;border:none;cursor:pointer;color:#bbb;font-size:1.1rem;padding:0;line-height:1;flex-shrink:0;margin-top:-1px}
.b370-toast-close:hover{color:#666}
</style>
    <?php
});
'''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    os.getenv('SSH_HOST'),
    port=int(os.getenv('SSH_PORT', 22)),
    username=os.getenv('SSH_USER'),
    password=os.getenv('SSH_PASS')
)

remote_path = '/home/u122447978/domains/b370sports.com/public_html/wp-content/mu-plugins/b370-urgency.php'

with ssh.open_sftp() as sftp:
    with sftp.open(remote_path, 'w') as f:
        f.write(URGENCY_PHP.encode('utf-8'))

print('Uploaded b370-urgency.php v1.3')

# Purge cache
stdin, stdout, stderr = ssh.exec_command(
    'cd /home/u122447978/domains/b370sports.com/public_html && '
    'wp litespeed-purge all --allow-root 2>/dev/null && echo cache-ok || echo cache-skip'
)
print('Cache:', stdout.read().decode().strip())

# Verify version
stdin, stdout, stderr = ssh.exec_command(
    'grep "Version:" /home/u122447978/domains/b370sports.com/public_html/wp-content/mu-plugins/b370-urgency.php'
)
print('Version check:', stdout.read().decode().strip())

ssh.close()
print('Done.')
