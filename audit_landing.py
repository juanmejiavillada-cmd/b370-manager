"""
B370 Landing Page Audit
Verifica: Meta Pixel, velocidad mobile (PageSpeed), producto, checkout, mobile UX
"""
import urllib.request
import urllib.parse
import ssl
import re
import json
import sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS_MOBILE = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-CO,es;q=0.9',
}

def fetch(url, headers=None, timeout=30):
    h = {**HEADERS_MOBILE, **(headers or {})}
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='ignore'), r.geturl(), r.status
    except Exception as e:
        return None, url, str(e)

def section(title):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)

# ─────────────────────────────────────────────
# 1. HOMEPAGE — Meta Pixel + Mobile UX
# ─────────────────────────────────────────────
section("1. HOMEPAGE — META PIXEL + MOBILE UX")
html, final_url, status = fetch("https://b370sports.com")
if html is None:
    print(f"ERROR cargando homepage: {status}")
else:
    print(f"Status: HTTP 200 OK | URL final: {final_url} | Chars: {len(html)}")

    # --- Meta Pixel ---
    kw_found = [kw for kw in ['fbq', 'facebook.net', 'fbevents.js', 'connect.facebook.net'] if kw in html]
    pixel_ids = re.findall(r"fbq\s*\(\s*['\"]init['\"]\s*,\s*['\"](\d+)['\"]", html)

    print(f"\n[META PIXEL]")
    if kw_found:
        print(f"  Keywords encontradas: {kw_found}")
        if pixel_ids:
            print(f"  >> Pixel ID: {pixel_ids[0]}")
        else:
            # Try alternate patterns
            alt = re.findall(r"'(\d{13,16})'", html)
            print(f"  Pixel ID no encontrado con patron fbq('init',...)")
            print(f"  IDs numericos largos en el HTML (posibles): {alt[:5]}")
    else:
        print("  NINGUNA keyword de Meta Pixel encontrada en el HTML")
        print("  >> CRITICO: Pixel podria no estar instalado o carga via GTM/async")

    # --- Viewport ---
    print(f"\n[VIEWPORT META TAG]")
    viewport = re.findall(r'<meta[^>]+name=["\']viewport["\'][^>]*>', html, re.IGNORECASE)
    if not viewport:
        viewport = re.findall(r'<meta[^>]+viewport[^>]*>', html, re.IGNORECASE)
    if viewport:
        print(f"  ENCONTRADO: {viewport[0][:120]}")
    else:
        print("  NO ENCONTRADO — problema critico mobile")

    # --- WhatsApp ---
    print(f"\n[WHATSAPP]")
    wa = re.findall(r'(wa\.me[^\s"<]{0,60}|whatsapp[^\s"<]{0,60})', html, re.IGNORECASE)
    if wa:
        print(f"  Encontrado: {wa[:3]}")
    else:
        print("  No encontrado en homepage")

    # --- CTAs above fold proxy (first 8000 chars) ---
    print(f"\n[CTAs — primeros 8000 chars del HTML]")
    fold = html[:8000]
    hrefs = re.findall(r'<a[^>]+href=["\']([^"\']{0,80})["\'][^>]*>([^<]{0,60})<', fold, re.IGNORECASE)
    btns = re.findall(r'<button[^>]*>([^<]{1,60})</button>', fold, re.IGNORECASE)
    cta_keywords = ['comprar', 'tienda', 'shop', 'carrito', 'ver', 'catalogo', 'colección', 'productos', 'add']
    relevant = [(href, txt.strip()) for href, txt in hrefs if any(k in txt.lower() or k in href.lower() for k in cta_keywords)]
    print(f"  CTAs relevantes: {relevant[:8]}")
    print(f"  Botones: {btns[:6]}")

# ─────────────────────────────────────────────
# 2. PAGESPEED INSIGHTS — MOBILE
# ─────────────────────────────────────────────
section("2. PAGESPEED INSIGHTS — MOBILE")
psi_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://b370sports.com&strategy=mobile"
psi_html, _, psi_status = fetch(psi_url, headers={'User-Agent': 'Python-audit/1.0'}, timeout=60)

if psi_html is None:
    print(f"ERROR: {psi_status}")
else:
    try:
        data = json.loads(psi_html)
        lr = data.get('lighthouseResult', {})
        cats = lr.get('categories', {})
        audits = lr.get('audits', {})

        perf_score = cats.get('performance', {}).get('score', 'N/A')
        if isinstance(perf_score, float):
            perf_score = int(perf_score * 100)

        def metric(key):
            a = audits.get(key, {})
            return a.get('displayValue', 'N/A'), a.get('score', 'N/A')

        lcp_val, lcp_sc = metric('largest-contentful-paint')
        tbt_val, tbt_sc = metric('total-blocking-time')
        cls_val, cls_sc = metric('cumulative-layout-shift')
        fcp_val, fcp_sc = metric('first-contentful-paint')
        si_val,  si_sc  = metric('speed-index')
        tti_val, tti_sc = metric('interactive')

        print(f"  Performance Score: {perf_score}/100")
        print(f"  FCP  (First Contentful Paint): {fcp_val}  (score: {fcp_sc})")
        print(f"  LCP  (Largest Contentful Paint): {lcp_val}  (score: {lcp_sc})")
        print(f"  TBT  (Total Blocking Time): {tbt_val}  (score: {tbt_sc})")
        print(f"  CLS  (Cumulative Layout Shift): {cls_val}  (score: {cls_sc})")
        print(f"  Speed Index: {si_val}  (score: {si_sc})")
        print(f"  TTI  (Time to Interactive): {tti_val}  (score: {tti_sc})")

        # Opportunities
        opps = []
        for k, v in audits.items():
            if v.get('score') is not None and isinstance(v['score'], float) and v['score'] < 0.5:
                title = v.get('title', k)
                desc = v.get('displayValue', '')
                opps.append(f"    - {title}: {desc}")
        if opps:
            print(f"\n  Principales oportunidades de mejora:")
            for o in opps[:8]:
                print(o)

    except Exception as e:
        print(f"Error parseando PSI: {e}")
        print(psi_html[:500])

# ─────────────────────────────────────────────
# 3. PÁGINA DE PRODUCTO
# ─────────────────────────────────────────────
section("3. PÁGINA DE PRODUCTO")

# First try shop/tienda to find a real product URL
for shop_url in ['https://b370sports.com/shop', 'https://b370sports.com/tienda', 'https://b370sports.com/productos']:
    shop_html, shop_final, shop_status = fetch(shop_url)
    if shop_html and len(shop_html) > 500:
        print(f"Shop page cargada: {shop_final} ({len(shop_html)} chars)")
        break
    else:
        print(f"  {shop_url} -> {shop_status}")
        shop_html = None

product_url = None
if shop_html:
    # WooCommerce product links pattern
    prod_links = re.findall(r'href=["\']([^"\']*(?:/producto/|/product/)[^"\']+)["\']', shop_html, re.IGNORECASE)
    if not prod_links:
        prod_links = re.findall(r'href=["\'](https://b370sports\.com/[^"\']+)["\']', shop_html)
    if prod_links:
        product_url = prod_links[0]
        print(f"Primer producto encontrado: {product_url}")

if not product_url:
    # Try direct known product slug guesses
    for slug in ['/producto/camiseta-atletico-nacional', '/product/camiseta', '/tienda']:
        test_html, _, _ = fetch(f"https://b370sports.com{slug}")
        if test_html and 'agregar al carrito' in test_html.lower():
            product_url = f"https://b370sports.com{slug}"
            break
    if not product_url:
        print("No se pudo encontrar URL de producto directamente. Revisando homepage para links de productos...")
        if html:
            prod_links2 = re.findall(r'href=["\']([^"\']*(?:/producto/|/product/)[^"\']+)["\']', html, re.IGNORECASE)
            if prod_links2:
                product_url = prod_links2[0]
                print(f"Producto desde homepage: {product_url}")

if product_url:
    prod_html, prod_final, prod_status = fetch(product_url)
    if prod_html:
        print(f"Producto cargado: {prod_final}")

        add_cart = bool(re.search(r'agregar.al.carrito|add.to.cart|add_to_cart', prod_html, re.IGNORECASE))
        price = bool(re.search(r'woocommerce-Price-amount|class=["\'][^"\']*price[^"\']*["\']|\$\s*[\d.,]+', prod_html, re.IGNORECASE))
        images = re.findall(r'<img[^>]+class=["\'][^"\']*wp-post-image[^"\']*["\'][^>]*>', prod_html, re.IGNORECASE)
        gallery = re.findall(r'woocommerce-product-gallery', prod_html, re.IGNORECASE)
        wa_prod = re.findall(r'(wa\.me[^\s"<]{0,80}|whatsapp[^\s"<]{0,60})', prod_html, re.IGNORECASE)

        print(f"\n  Boton 'Agregar al carrito': {'SI' if add_cart else 'NO - CRITICO'}")
        print(f"  Precio visible: {'SI' if price else 'NO - CRITICO'}")
        print(f"  Imagen producto (wp-post-image): {'SI' if images else 'NO'}")
        print(f"  Galeria WooCommerce: {'SI' if gallery else 'NO'}")
        print(f"  WhatsApp en producto: {wa_prod[:2] if wa_prod else 'NO'}")

        # Check for variable product selectors
        variations = bool(re.search(r'variations_form|woocommerce-variation|select_attribute', prod_html, re.IGNORECASE))
        print(f"  Selector de variaciones (tallas): {'SI' if variations else 'NO'}")

        # Pixel on product page
        px_prod = [kw for kw in ['fbq', 'facebook.net', 'fbevents'] if kw in prod_html]
        print(f"  Pixel en pagina de producto: {px_prod if px_prod else 'NO ENCONTRADO'}")
    else:
        print(f"ERROR cargando producto: {prod_status}")
else:
    print("No se encontro URL de producto para verificar")

# ─────────────────────────────────────────────
# 4. CHECKOUT
# ─────────────────────────────────────────────
section("4. CHECKOUT")
co_html, co_final, co_status = fetch("https://b370sports.com/checkout")
if co_html is None:
    print(f"ERROR: {co_status}")
else:
    print(f"Checkout cargado: {co_final} ({len(co_html)} chars)")

    is_empty_cart = bool(re.search(r'carrito.est.+vac|cart.is.empty|empty.cart', co_html, re.IGNORECASE))
    has_form = bool(re.search(r'woocommerce-checkout|checkout.form|billing_first_name', co_html, re.IGNORECASE))

    # Payment methods
    payment_methods = {}
    for method, kws in {
        'Wompi': ['wompi'],
        'PSE': ['pse'],
        'Addi': ['addi'],
        'Contra-entrega': ['contra.entrega', 'contraentrega', 'cash.on.delivery', 'cod'],
        'Tarjeta': ['tarjeta', 'credit.card', 'visa', 'mastercard'],
        'PayU': ['payu'],
        'ePayco': ['epayco'],
        'Mercado Pago': ['mercadopago', 'mercado.pago'],
        'Transferencia': ['transferencia', 'bank.transfer'],
    }.items():
        found = any(re.search(kw, co_html, re.IGNORECASE) for kw in kws)
        payment_methods[method] = found

    print(f"\n  Carrito vacio (redirect?): {'SI - puede ser normal sin items' if is_empty_cart else 'NO'}")
    print(f"  Formulario checkout presente: {'SI' if has_form else 'NO'}")
    print(f"\n  Metodos de pago detectados:")
    for method, found in payment_methods.items():
        print(f"    {method}: {'SI' if found else 'no detectado'}")

    # Errors
    errors = re.findall(r'(?:error|Error|ERROR)[^<]{0,100}', co_html)
    if errors:
        print(f"\n  Posibles errores en pagina: {errors[:3]}")

# ─────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────
section("RESUMEN — LISTO PARA PAUTA?")
print("  Ver resultados arriba por seccion.")
print("  Script completado.")
