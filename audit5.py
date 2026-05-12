# -*- coding: utf-8 -*-
"""
B370 Audit Part 5 — Price extraction + checkout direct + pixel fbq trace
"""
import urllib.request
import ssl
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': MOBILE_UA, 'Accept': 'text/html,*/*'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='replace'), r.geturl()
    except Exception as e:
        return None, str(e)

# ─── PRODUCT: price + pixel fbq trace ───
print("=== PRODUCTO LOCAL HOMBRE 2026 — ANALISIS PROFUNDO ===")
prod_html, prod_url = fetch("https://b370sports.com/product/local-hombre-2026/")
if prod_html:
    print(f"URL: {prod_url} | Chars: {len(prod_html)}")

    # Price — try multiple patterns
    prices = re.findall(r'[\$\s]*([\d]{2,3}[\.,]\d{3})', prod_html)
    wc_prices = re.findall(r'woocommerce-Price-amount[^>]*>.*?<bdi>(.*?)</bdi>', prod_html, re.DOTALL | re.IGNORECASE)
    price_meta = re.findall(r'"price"\s*:\s*"([\d.,]+)"', prod_html)
    print(f"  Precios encontrados (regex): {list(set(prices))[:5]}")
    print(f"  woocommerce-Price-amount: {wc_prices[:3]}")
    print(f"  price en JSON: {price_meta[:3]}")

    # fbq direct calls
    fbq_calls = re.findall(r'fbq\([^)]{0,150}\)', prod_html)
    print(f"\n  fbq() calls directas: {fbq_calls[:5]}")

    # PYS inline config on this page
    pys_ev = re.findall(r'pysOptions\s*=\s*(\{.{0,800})', prod_html, re.DOTALL)
    if pys_ev:
        print(f"\n  pysOptions en producto: {pys_ev[0][:500]}")

    # ViewContent event?
    view_content = re.search(r'ViewContent|view_content', prod_html, re.IGNORECASE)
    print(f"\n  Evento ViewContent: {'SI' if view_content else 'NO'}")

    # Add to cart button HTML
    atc_btn = re.findall(r'<button[^>]*add_to_cart[^>]*>([^<]+)', prod_html, re.IGNORECASE)
    if not atc_btn:
        atc_btn = re.findall(r'<button[^>]*single_add_to_cart[^>]*>([^<]+)', prod_html, re.IGNORECASE)
    print(f"\n  Boton ATC texto: {atc_btn[:3]}")

    # Variation form — tallas
    talla_options = re.findall(r'<option[^>]*value=["\']([^"\']+)["\'][^>]*>([^<]+)</option>', prod_html, re.IGNORECASE)
    talla_filtered = [(v, t) for v, t in talla_options if any(s in v.upper() or s in t.upper() for s in ['S', 'M', 'L', 'XL', 'XXL', 'S,', 'TALLA'])]
    print(f"\n  Opciones de talla: {talla_filtered[:10]}")

    # Addi widget
    addi_widget = re.findall(r'addi[^<]{0,200}', prod_html, re.IGNORECASE)
    print(f"\n  Addi widget: {addi_widget[:2]}")

# ─── CHECKOUT directo ───
print("\n=== CHECKOUT DIRECTO ===")
co_html, co_url = fetch("https://b370sports.com/checkout/")
if co_html:
    print(f"URL final: {co_url} | Chars: {len(co_html)}")

    # Payment gateways registered in WooCommerce
    # They appear in wc_checkout_params or similar localized variables
    wc_params = re.findall(r'wc_checkout_params\s*=\s*(\{.{0,600})', co_html, re.DOTALL)
    if wc_params:
        print(f"\n  wc_checkout_params: {wc_params[0][:400]}")

    # Payment method radio buttons
    pay_radios = re.findall(r'value=["\']payment_method_([^"\']+)["\']', co_html, re.IGNORECASE)
    if not pay_radios:
        pay_radios = re.findall(r'id=["\']payment_method_([^"\']+)["\']', co_html, re.IGNORECASE)
    print(f"\n  Payment method values: {pay_radios}")

    # Payment gateway titles
    pay_titles = re.findall(r'<li[^>]*class=["\'][^"\']*wc_payment_method[^"\']*["\'][^>]*>.*?<label[^>]*>([^<]{3,60})', co_html, re.IGNORECASE | re.DOTALL)
    print(f"  Payment titles: {pay_titles[:6]}")

    # Wompi
    wompi_ref = re.findall(r'wompi[^<"]{0,120}', co_html, re.IGNORECASE)
    print(f"\n  Wompi refs: {[w.strip()[:80] for w in wompi_ref[:3]]}")

    # Contra-entrega
    cod_ref = re.findall(r'(?:contra.?entrega|cod|efectivo)[^<"]{0,80}', co_html, re.IGNORECASE)
    print(f"  COD refs: {[c.strip()[:60] for c in cod_ref[:3]]}")

# ─── MOBILE UX — CTAs above fold ───
print("\n=== MOBILE UX — CTAs ABOVE FOLD (homepage) ===")
home_html, _ = fetch("https://b370sports.com")
if home_html:
    # Body content before first script block = approx above fold
    body_start = home_html.find('<body')
    body_html = home_html[body_start:body_start+15000] if body_start > -1 else home_html[:15000]

    # Find all visible anchor text and buttons
    all_anchors = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>\s*([^<]{2,60})\s*</a>', body_html, re.IGNORECASE)
    nav_and_cta = [(href, txt.strip()) for href, txt in all_anchors if txt.strip() and not txt.strip().startswith('<')]
    print("  Links/CTAs en primeros 15000 chars del body:")
    for href, txt in nav_and_cta[:20]:
        print(f"    [{txt}] -> {href[:60]}")

    # Buttons
    all_btns = re.findall(r'<button[^>]*>([^<]{1,60})</button>', body_html, re.IGNORECASE)
    print(f"\n  Botones: {all_btns[:10]}")

    # Hero / banner section
    hero = re.findall(r'(?:hero|banner|slider|wp-block-cover|wp-block-media)[^>]*>.*?</(?:section|div)>', body_html[:8000], re.IGNORECASE | re.DOTALL)
    print(f"\n  Hero/banner sections encontrados: {len(hero)}")
    if hero:
        # Extract text from first hero
        hero_text = re.sub(r'<[^>]+>', ' ', hero[0])
        hero_text = re.sub(r'\s+', ' ', hero_text).strip()
        print(f"  Hero text: {hero_text[:200]}")

print("\n=== DONE ===")
