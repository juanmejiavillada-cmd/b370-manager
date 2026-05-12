"""
B370 Audit Part 2 — Product URL finder + PSI + deep pixel check
"""
import urllib.request
import ssl
import json
import re
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': MOBILE_UA, 'Accept': 'text/html,*/*'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='ignore'), r.geturl()
    except Exception as e:
        return None, str(e)

# ─── FIND REAL PRODUCT ───
print("=== BUSCANDO PRODUCTOS EN /tienda ===")
html, final = fetch("https://b370sports.com/tienda/")
if html:
    all_hrefs = re.findall(r'href=["\'](https://b370sports\.com[^"\']+)["\']', html)
    unique = list(dict.fromkeys(all_hrefs))
    print(f"Total hrefs: {len(unique)}")
    print("Primeros 30:")
    for h in unique[:30]:
        print(f"  {h}")

    # Find product-specific links
    prod_links = [h for h in unique if '/producto/' in h or '/product/' in h]
    print(f"\nLinks de producto: {prod_links[:10]}")

    # Also look for WooCommerce add-to-cart links
    atc = re.findall(r'href=["\'](https://b370sports\.com[^"\']*add-to-cart[^"\']*)["\']', html)
    print(f"Add-to-cart links: {atc[:5]}")

    # Look for product container patterns
    product_ids = re.findall(r'post-(\d+).*?product', html[:50000])
    print(f"Product post IDs: {list(set(product_ids))[:10]}")

# ─── PIXEL DEEP CHECK ───
print("\n=== PIXEL CHECK PROFUNDO — HOMEPAGE ===")
home_html, _ = fetch("https://b370sports.com")
if home_html:
    # GTM check
    gtm = re.findall(r'GTM-[A-Z0-9]+', home_html)
    print(f"Google Tag Manager IDs: {gtm}")

    # Any pixel-related scripts
    script_srcs = re.findall(r'<script[^>]+src=["\'](https?://[^"\']+)["\']', home_html, re.IGNORECASE)
    print(f"\nScript externos cargados:")
    for s in script_srcs:
        print(f"  {s}")

    # Look for noscript pixel img tag
    noscript_fb = re.findall(r'<noscript[^>]*>.*?facebook.*?</noscript>', home_html, re.IGNORECASE | re.DOTALL)
    print(f"\nNoscript Facebook: {noscript_fb[:2]}")

    # Check _fbp cookie hint or dataLayer
    datalayer = re.findall(r'dataLayer\.push\([^)]{0,200}\)', home_html)
    print(f"\ndataLayer pushes: {datalayer[:3]}")

    # Full raw search for 'fb' patterns
    fb_context = re.findall(r'.{0,30}(fbq|facebook\.net|fbevents|_fbp|FB\.init).{0,50}', home_html, re.IGNORECASE)
    print(f"\nContexto 'fb' hits: {fb_context[:5]}")

# ─── PAGESPEED INSIGHTS ───
print("\n=== PAGESPEED INSIGHTS MOBILE ===")
time.sleep(2)
psi_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https%3A%2F%2Fb370sports.com&strategy=mobile"
req2 = urllib.request.Request(psi_url, headers={'User-Agent': 'Python/3.x audit'})
try:
    with urllib.request.urlopen(req2, context=ctx, timeout=90) as r:
        data = json.loads(r.read().decode())
    lr = data.get('lighthouseResult', {})
    audits = lr.get('audits', {})
    cats = lr.get('categories', {})

    perf = cats.get('performance', {}).get('score', 'N/A')
    if isinstance(perf, float): perf = int(perf * 100)

    def m(k):
        a = audits.get(k, {})
        return a.get('displayValue', 'N/A'), a.get('score', 'N/A')

    print(f"Performance Score: {perf}/100")
    print(f"FCP:  {m('first-contentful-paint')}")
    print(f"LCP:  {m('largest-contentful-paint')}")
    print(f"TBT:  {m('total-blocking-time')}")
    print(f"CLS:  {m('cumulative-layout-shift')}")
    print(f"SI:   {m('speed-index')}")
    print(f"TTI:  {m('interactive')}")

    print("\nAudits con score < 0.5 (problemas):")
    for k, v in audits.items():
        sc = v.get('score')
        if isinstance(sc, float) and sc < 0.5:
            print(f"  [{int(sc*100)}] {v.get('title','?')}: {v.get('displayValue','')}")

except Exception as e:
    print(f"PSI Error: {e}")

# ─── PRODUCTO REAL ───
print("\n=== VERIFICACION PRODUCTO REAL ===")
# Try WooCommerce REST API to get first product URL
wc_url = "https://b370sports.com/wp-json/wc/v3/products?per_page=1&status=publish"
try:
    req3 = urllib.request.Request(wc_url, headers={'User-Agent': MOBILE_UA})
    with urllib.request.urlopen(req3, context=ctx, timeout=15) as r:
        products = json.loads(r.read().decode())
    if products:
        p = products[0]
        print(f"Producto via API: {p.get('name')} | URL: {p.get('permalink')}")
        prod_url = p.get('permalink')
    else:
        prod_url = None
except Exception as e:
    print(f"WC API error (esperado sin auth): {e}")
    prod_url = None

if not prod_url and html:
    # Try to find from tienda page more aggressively
    # WooCommerce uses woocommerce_loop_add_to_cart_link or product post type
    slugs = re.findall(r'https://b370sports\.com/([a-z0-9\-]+)/', html)
    freq = {}
    for s in slugs:
        if s not in ('tienda', 'wp-content', 'wp-includes', 'categoria', 'tag', 'page', 'feed'):
            freq[s] = freq.get(s, 0) + 1
    sorted_slugs = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    print(f"Slugs mas frecuentes en /tienda: {sorted_slugs[:10]}")

    # Try first high-frequency slug as product
    for slug, count in sorted_slugs[:5]:
        url_try = f"https://b370sports.com/{slug}/"
        test_html, test_final = fetch(url_try)
        if test_html and ('agregar al carrito' in test_html.lower() or 'add-to-cart' in test_html.lower()):
            prod_url = url_try
            print(f"Producto encontrado en: {url_try}")
            break

if prod_url:
    prod_html, prod_final = fetch(prod_url)
    if prod_html:
        print(f"\nProducto cargado: {prod_final}")
        checks = {
            'Agregar al carrito': bool(re.search(r'agregar.al.carrito|add.to.cart', prod_html, re.IGNORECASE)),
            'Precio': bool(re.search(r'woocommerce-Price-amount|price.*\d{2,}', prod_html, re.IGNORECASE)),
            'Imagen producto': bool(re.search(r'wp-post-image|woocommerce-product-gallery__image', prod_html, re.IGNORECASE)),
            'Variaciones talla': bool(re.search(r'variations_form|attribute_pa_tallas', prod_html, re.IGNORECASE)),
            'WhatsApp': bool(re.search(r'wa\.me|whatsapp', prod_html, re.IGNORECASE)),
            'Meta Pixel': bool(re.search(r'fbq|fbevents', prod_html, re.IGNORECASE)),
        }
        for k, v in checks.items():
            print(f"  {k}: {'SI' if v else 'NO'}")

print("\n=== DONE ===")
