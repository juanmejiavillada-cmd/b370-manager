# -*- coding: utf-8 -*-
"""
B370 Audit Part 4 — PSI final attempt + real product via WC JSON sitemap + checkout deep
"""
import urllib.request
import ssl
import json
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'

def fetch(url, timeout=30, ua=None):
    req = urllib.request.Request(url, headers={'User-Agent': ua or MOBILE_UA, 'Accept': 'text/html,application/json,*/*'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='replace'), r.geturl(), r.status
    except Exception as e:
        return None, str(e), 0

# ─── PAGESPEED (sin API key, try different approach) ───
print("=== PAGESPEED INSIGHTS MOBILE ===")
time.sleep(5)

# Try different URL format
psi_variants = [
    "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://b370sports.com&strategy=mobile&fields=lighthouseResult.categories.performance.score,lighthouseResult.audits",
    "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://b370sports.com&strategy=mobile",
]

psi_data = None
for psi_url in psi_variants:
    psi_html, psi_final, psi_status = fetch(psi_url, timeout=90, ua='B370-audit/4.0')
    if psi_html and psi_status == 200:
        try:
            psi_data = json.loads(psi_html)
            print(f"  PSI cargado exitosamente")
            break
        except:
            pass
    else:
        print(f"  PSI attempt: {psi_final} (status {psi_status})")
    time.sleep(3)

if psi_data:
    lr = psi_data.get('lighthouseResult', {})
    audits = lr.get('audits', {})
    cats = lr.get('categories', {})

    perf = cats.get('performance', {}).get('score', 'N/A')
    if isinstance(perf, float): perf = int(perf * 100)

    def m(k):
        a = audits.get(k, {})
        return a.get('displayValue', 'N/A'), round(a.get('score', -1), 2)

    print(f"  Performance Score: {perf}/100")
    fcp = m('first-contentful-paint')
    lcp = m('largest-contentful-paint')
    tbt = m('total-blocking-time')
    cls = m('cumulative-layout-shift')
    si  = m('speed-index')
    tti = m('interactive')

    print(f"  FCP:   {fcp[0]}  (score: {fcp[1]})")
    print(f"  LCP:   {lcp[0]}  (score: {lcp[1]})")
    print(f"  TBT:   {tbt[0]}  (score: {tbt[1]})")
    print(f"  CLS:   {cls[0]}  (score: {cls[1]})")
    print(f"  SI:    {si[0]}   (score: {si[1]})")
    print(f"  TTI:   {tti[0]}  (score: {tti[1]})")

    print("\n  Audits con score bajo (<0.5):")
    for k, v in audits.items():
        sc = v.get('score')
        if isinstance(sc, float) and sc < 0.5:
            print(f"    [{int(sc*100):3d}%] {v.get('title','?')}: {v.get('displayValue','')}")
else:
    print("  PSI no disponible (rate limit API publica sin key)")
    print("  ALTERNATIVA: corre manualmente en https://pagespeed.web.dev/?url=https://b370sports.com&form_factor=mobile")

# ─── REAL PRODUCT via WP Sitemap ───
print("\n=== PRODUCTO REAL — WP SITEMAP ===")
sitemap_html, _, _ = fetch("https://b370sports.com/wp-sitemap.xml")
if sitemap_html:
    # Find product sitemap
    product_sitemaps = re.findall(r'<loc>(https://b370sports\.com/wp-sitemap-posts-product-\d+\.xml)</loc>', sitemap_html)
    print(f"  Product sitemaps: {product_sitemaps}")

    if product_sitemaps:
        psm_html, _, _ = fetch(product_sitemaps[0])
        if psm_html:
            prod_urls = re.findall(r'<loc>(https://b370sports\.com[^<]+)</loc>', psm_html)
            print(f"  Primeras URLs de productos en sitemap: {prod_urls[:5]}")

            if prod_urls:
                # Test first real product
                prod_url = prod_urls[0]
                print(f"\n  Cargando: {prod_url}")
                prod_html, prod_final, _ = fetch(prod_url)
                if prod_html:
                    checks = {
                        'Agregar al carrito': bool(re.search(r'agregar.al.carrito|single_add_to_cart_button', prod_html, re.IGNORECASE)),
                        'Precio visible': bool(re.search(r'woocommerce-Price-amount', prod_html, re.IGNORECASE)),
                        'Imagen galeria': bool(re.search(r'woocommerce-product-gallery', prod_html, re.IGNORECASE)),
                        'Variaciones talla': bool(re.search(r'attribute_pa_tallas|pa_tallas|Tallas', prod_html, re.IGNORECASE)),
                        'WhatsApp boton': bool(re.search(r'wa\.me|whatsapp', prod_html, re.IGNORECASE)),
                        'Meta Pixel (fbq)': bool(re.search(r'\bfbq\b', prod_html, re.IGNORECASE)),
                        'Pixel via PYS': bool(re.search(r'pixelyoursite|pysOptions', prod_html, re.IGNORECASE)),
                        'Addi (cuotas)': bool(re.search(r'addi', prod_html, re.IGNORECASE)),
                    }
                    for k, v in checks.items():
                        print(f"    {k}: {'SI' if v else 'NO'}")

                    # Get product name and price
                    name = re.findall(r'<h1[^>]*class=["\'][^"\']*product_title[^"\']*["\'][^>]*>([^<]+)', prod_html, re.IGNORECASE)
                    price = re.findall(r'<bdi>\s*\$\s*([\d.,]+)\s*</bdi>', prod_html, re.IGNORECASE)
                    print(f"\n    Nombre producto: {name}")
                    print(f"    Precio: {price}")
    else:
        # Try post sitemap
        all_sitmaps = re.findall(r'<loc>(https://b370sports\.com/wp-sitemap[^<]+)</loc>', sitemap_html)
        print(f"  Todos los sitemaps: {all_sitmaps}")

# ─── CHECKOUT REAL (simular con producto en carrito no es posible sin JS) ───
print("\n=== CHECKOUT / CARRITO ANALISIS ===")
cart_html, cart_final, _ = fetch("https://b370sports.com/carrito/")
if cart_html:
    # Look for payment method registrations in JS
    payment_js = re.findall(r'payment_method["\']?\s*[:=]\s*["\']([^"\']+)["\']', cart_html, re.IGNORECASE)
    payment_labels = re.findall(r'<label[^>]*for=["\']payment_method_([^"\']+)["\'][^>]*>([^<]{2,60})', cart_html, re.IGNORECASE)

    print(f"  URL final: {cart_final}")
    print(f"  Metodos en JS: {list(set(payment_js))[:8]}")
    print(f"  Labels de pago: {payment_labels[:6]}")

    # Wompi specific
    wompi_detail = re.findall(r'wompi[^\n]{0,200}', cart_html, re.IGNORECASE)
    print(f"\n  Wompi contexto: {wompi_detail[:2]}")

    # Addi
    addi_detail = re.findall(r'addi[^\n]{0,100}', cart_html, re.IGNORECASE)
    print(f"  Addi contexto: {addi_detail[:2]}")

print("\n=== DONE ===")
