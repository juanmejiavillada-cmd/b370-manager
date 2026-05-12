# -*- coding: utf-8 -*-
"""
B370 Audit Part 3 — Pixel ID extraction + PSI + product real URL
"""
import urllib.request
import ssl
import json
import re
import sys
import time

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'

def fetch(url, timeout=30, ua=None):
    req = urllib.request.Request(url, headers={'User-Agent': ua or MOBILE_UA, 'Accept': 'text/html,*/*'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='replace'), r.geturl()
    except Exception as e:
        return None, str(e)

# ─── 1. PIXEL VIA PixelYourSite SCRIPT ───
print("=== 1. META PIXEL — VERIFICACION PROFUNDA ===")

# Fetch the pixelyoursite public.js output (it contains the pixel config)
pys_url = "https://b370sports.com/wp-content/plugins/pixelyoursite/dist/scripts/public.js?ver=11.2.0.4"
pys_html, _ = fetch(pys_url)
if pys_html:
    pixel_ids = re.findall(r'["\']?(?:pixel_id|pixelID|fb_pixel_id|fbPixelId)["\']?\s*[:=]\s*["\']?(\d{10,16})["\']?', pys_html, re.IGNORECASE)
    print(f"  Pixel IDs en public.js: {pixel_ids}")
    # Show first 500 chars
    print(f"  Primeros 300 chars: {pys_html[:300]}")
else:
    print("  No se pudo cargar public.js")

# Also try the homepage with a broader search now that we know pixelyoursite is there
home_html, _ = fetch("https://b370sports.com")
if home_html:
    # PixelYourSite puts config in inline script
    pys_config = re.findall(r'pys\s*=\s*\{[^}]{0,500}', home_html)
    if pys_config:
        print(f"\n  pys config found: {pys_config[0][:300]}")

    # Try broader numeric ID patterns near facebook/pixel keywords
    # Look for 15-16 digit numbers (Meta pixel IDs)
    all_long_nums = re.findall(r'\b(\d{15,16})\b', home_html)
    print(f"\n  Numeros 15-16 digitos (tipico pixel ID): {list(set(all_long_nums))[:5]}")

    # 13-digit pixel IDs also common
    all_13_nums = re.findall(r'\b(\d{13,14})\b', home_html)
    print(f"  Numeros 13-14 digitos: {list(set(all_13_nums))[:5]}")

    # Look for pysOptions or similar WP-localized scripts
    wp_localize = re.findall(r'var\s+\w+\s*=\s*\{[^}]{0,600}\}', home_html)
    for wl in wp_localize:
        if any(k in wl.lower() for k in ['pixel', 'facebook', 'fb_', 'meta']):
            print(f"\n  WP localized var con pixel: {wl[:400]}")

    # Look for any inline script mentioning pixel
    inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', home_html, re.DOTALL | re.IGNORECASE)
    for sc in inline_scripts:
        if any(k in sc.lower() for k in ['pixel', 'fbq', 'facebook', 'pys']):
            print(f"\n  Script inline con pixel/fbq/pys (primeros 500): {sc[:500]}")
            break

# ─── 2. PAGESPEED ───
print("\n=== 2. PAGESPEED INSIGHTS MOBILE ===")
time.sleep(3)
psi_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https%3A%2F%2Fb370sports.com&strategy=mobile"
psi_html, psi_final = fetch(psi_url, timeout=90, ua='Python-audit/3.0')
if psi_html:
    try:
        data = json.loads(psi_html)
        lr = data.get('lighthouseResult', {})
        audits = lr.get('audits', {})
        cats = lr.get('categories', {})

        perf = cats.get('performance', {}).get('score', 'N/A')
        if isinstance(perf, float): perf = int(perf * 100)

        def m(k):
            a = audits.get(k, {})
            return a.get('displayValue', 'N/A'), round(a.get('score', -1), 2)

        print(f"  Performance Score: {perf}/100")
        print(f"  FCP  (First Contentful Paint): {m('first-contentful-paint')}")
        print(f"  LCP  (Largest Contentful Paint): {m('largest-contentful-paint')}")
        print(f"  TBT  (Total Blocking Time): {m('total-blocking-time')}")
        print(f"  CLS  (Cumulative Layout Shift): {m('cumulative-layout-shift')}")
        print(f"  Speed Index: {m('speed-index')}")
        print(f"  TTI  (Time to Interactive): {m('interactive')}")

        print("\n  Audits fallidos (score < 0.5):")
        for k, v in audits.items():
            sc = v.get('score')
            if isinstance(sc, float) and sc < 0.5:
                print(f"    [{int(sc*100):3d}%] {v.get('title','?')}: {v.get('displayValue','')}")

    except Exception as e:
        print(f"  PSI parse error: {e}")
        print(f"  Raw (first 300): {psi_html[:300]}")
else:
    print(f"  PSI fetch failed: {psi_final}")

# ─── 3. PRODUCT PAGE ───
print("\n=== 3. PAGINA DE PRODUCTO ===")
tienda_html, _ = fetch("https://b370sports.com/tienda/")
if tienda_html:
    # WooCommerce renders products with specific classes/patterns
    # Try to find post slugs by looking at WC loop item markup
    # Pattern: href to b370sports.com that is NOT a file/plugin path
    all_links = re.findall(r'href=["\'](https://b370sports\.com/([a-z0-9\-]+)/?)["\'"]', tienda_html)
    candidate_slugs = [slug for (full, slug) in all_links if '.' not in slug and slug not in (
        'feed', 'tienda', 'shop', 'carrito', 'checkout', 'mi-cuenta', 'blog', 'contacto'
    )]
    print(f"  Candidate product slugs: {list(dict.fromkeys(candidate_slugs))[:15]}")

    # Try each as a product page
    for slug in list(dict.fromkeys(candidate_slugs))[:6]:
        test_url = f"https://b370sports.com/{slug}/"
        test_html, test_final = fetch(test_url, timeout=15)
        if test_html:
            has_atc = bool(re.search(r'agregar.al.carrito|add.to.cart|single_add_to_cart_button', test_html, re.IGNORECASE))
            is_product = bool(re.search(r'product_type|woocommerce-product|single-product', test_html, re.IGNORECASE))
            if has_atc or is_product:
                print(f"\n  PRODUCTO ENCONTRADO: {test_final}")
                checks = {
                    'Agregar al carrito': has_atc,
                    'Precio': bool(re.search(r'woocommerce-Price-amount|\$[\s]*[\d\.]+', test_html, re.IGNORECASE)),
                    'Imagen': bool(re.search(r'woocommerce-product-gallery|wp-post-image', test_html, re.IGNORECASE)),
                    'Variaciones talla': bool(re.search(r'variations_form|attribute_pa_tallas|pa_tallas', test_html, re.IGNORECASE)),
                    'WhatsApp': bool(re.search(r'wa\.me|whatsapp', test_html, re.IGNORECASE)),
                    'Meta Pixel': bool(re.search(r'fbq|fbevents|pixelyoursite', test_html, re.IGNORECASE)),
                }
                for k, v in checks.items():
                    status = 'SI' if v else 'NO'
                    print(f"    {k}: {status}")
                break
            else:
                print(f"  {slug}: no es pagina de producto")
        else:
            print(f"  {slug}: error")

# ─── 4. CHECKOUT METHODS ───
print("\n=== 4. CHECKOUT — METODOS DE PAGO ===")
co_html, co_final = fetch("https://b370sports.com/checkout")
if co_html:
    print(f"  URL final: {co_final}")
    payment_search = {
        'Wompi': r'wompi',
        'PSE': r'\bpse\b',
        'Addi': r'addi',
        'Contra-entrega/COD': r'contra.?entrega|cod|cash.on.delivery|pago.en.efectivo',
        'Tarjeta credito': r'tarjeta.de.cr[eé]dito|credit.card|visa|mastercard',
        'WooCommerce payments': r'woocommerce-payments|wcpay',
    }
    for name, pattern in payment_search.items():
        found = bool(re.search(pattern, co_html, re.IGNORECASE))
        print(f"  {name}: {'SI' if found else 'no detectado'}")

    # Is it actually the checkout or redirecting to cart?
    is_cart = 'carrito' in co_final
    print(f"\n  Redirige a /carrito/ (sin items): {'SI - normal sin productos' if is_cart else 'NO'}")

    # Try to extract payment method names from form
    pay_methods = re.findall(r'<li[^>]+payment_method[^>]*>[^<]*<(?:label|input)[^>]*>([^<]{2,50})', co_html, re.IGNORECASE)
    print(f"  Metodos visibles en form: {pay_methods[:6]}")

print("\n=== DONE ===")
