import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, json, requests

def load_env():
    env = {}
    with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

env = load_env()
token = env['META_ACCESS_TOKEN']
BASE = "https://graph.facebook.com/v21.0"
AD_ACCOUNT = "act_25577388011912523"
PAGE_ID = "118310441371257"
PIXEL_ID = "2015110402400663"
URL = "https://b370sports.com/atletico-nacional-2026/"

# 15 imágenes subidas a Meta
IMAGE_HASHES = [
    "fd963c7ab3f336195ed85cbc70cf111b",  # Advertising_poster_vintage_stadium
    "7532e50b4093924ff4e722152f36c508",  # Atlético_Nacional_jersey_campaign 1
    "a9ba12127b66805835e11db9104a0044",  # Atlético_Nacional_jersey_campaign 2
    "65015aa76a5ea7c1fae0c80af6cf6ff5",  # Cambia_camisa_de_imagen_original
    "0b81f80b1d53611d350dfca8b1de2eb0",  # Cambia_camiseta_y_círculos
    "a2b46597b82d28015d640286bcc6bf1c",  # Comprar_tu_talla_sea_brillante
    "ab16821497ec1c4a6a29cf8a014000a8",  # image.png 1857
    "b704cf48b79eb37aa2b6d6f876ef0ca9",  # image.png 1936
    "65219ded179a323a29e411f7f50608aa",  # image.png 2126
    "19236e1d3147c539d7e540a4a73194f9",  # PACK3-2026_1.jpg
]

BODIES = [
    "En B370 tenemos las versiones que necesitas, \n\n¡y te llegan rápido! \n\n🚀 Compra seguro con pago contra-entrega real. \n\n¡No te quedes sin tu outfit ideal! 💥",
    "Sabemos que te encanta la calidad premium, pero te preocupa la seguridad al comprar online y el precio.\n\nEn B370, te ofrecemos indumentaria Premium con pago contra-entrega REAL.\n\n¡Compran miles de clientes con confianza!\n\n¡Calidad, exclusividad y seguridad en un solo lugar! 💯",
    "✨ ¡Viste como los profesionales! \n\nMiles ya disfrutan la calidad premium de B370.\n\nElige entre versiones Top, Jugador o Fans y recibe directo en tu casa. \n\nCompra con la confianza del pago contra-entrega. \n\n¡Tu estilo importa! 😎",
    "🤯 No es solo una camiseta.\n\nEs el orgullo que llevas puesto. 🟢⚽\n\nLa nueva 2026 del Rey de Copas ya llegó.\n\nTe atendemos personalmente para que elijas la versión perfecta. \n\n¡No te arriesgues con tiendas dudosas! Tu tranquilidad vale oro. 🔒",
    "Nuevas Finales, Nueva camiseta. \n\nEl Verde no espera. 🟢🏆\n\nLocal, Tercera y Retros históricas disponibles ahora.\n\nPagas cuando la recibes.\nEn B370, vestimos la pasión.",
]

TITLES = [
    "¡Última Oportunidad Hoy!",
    "Solo Quedan Pocas Unidades",
    "5000+ Clientes Felices",
    "¿Te lo Vas a Perder?",
    "Gana 20% Más con B370",
]

DESCRIPTIONS = [
    "Envío Gratis a Colombia",
    "Calidad Certificada",
    "Recomendado por FB",
    "Entrega Rápida Garantizada",
    "Recíbela en 24-48 Horas",
]

def post(endpoint, payload):
    payload['access_token'] = token
    r = requests.post(f"{BASE}/{endpoint}", data=payload)
    return r.status_code, r.json()

# ── REUSAR campaña y ad set ya creados ───────────────────────
CAMPAIGN_ID = "120243094267410179"
ADSET_ID    = "120243094268100179"
print(f"[1] Campaña existente: {CAMPAIGN_ID}")
print(f"[2] Ad Set existente:  {ADSET_ID}")

# ── PASO 3: CREATIVE DCO ──────────────────────────────────────
print("\n[3] Creando adcreative DCO (15 img × 5 copys × 5 títulos × 5 desc)...")
asset_feed_spec = {
    "images": [{"hash": h} for h in IMAGE_HASHES],
    "bodies": [{"text": b} for b in BODIES],
    "titles": [{"text": t} for t in TITLES],
    "descriptions": [{"text": d} for d in DESCRIPTIONS],
    "link_urls": [{"website_url": URL}],
    "call_to_action_types": ["SHOP_NOW"],
    "ad_formats": ["SINGLE_IMAGE"],
}

status, data = post(f"{AD_ACCOUNT}/adcreatives", {
    "name": "B370 | Nacional 2026 | DCO Creative | 10img × 5copy",
    "object_story_spec": json.dumps({"page_id": PAGE_ID}),
    "asset_feed_spec": json.dumps(asset_feed_spec),
})
print(f"  HTTP {status} → {data}")
if 'error' in data:
    print(f"❌ {data['error']['message']}")
    sys.exit(1)
CREATIVE_ID = data['id']
print(f"  ✅ Creative ID: {CREATIVE_ID}")

# ── PASO 4: ANUNCIO ───────────────────────────────────────────
print("\n[4] Creando anuncio...")
status, data = post(f"{AD_ACCOUNT}/ads", {
    "name": "B370 | Nacional 2026 | DCO | 10img × 5copy",
    "adset_id": ADSET_ID,
    "creative": json.dumps({"creative_id": CREATIVE_ID}),
    "tracking_specs": json.dumps([{"action.type": ["offsite_conversion"], "fb_pixel": [PIXEL_ID]}]),
    "status": "PAUSED",
})
print(f"  HTTP {status} → {data}")
if 'error' in data:
    print(f"❌ {data['error']['message']}")
    sys.exit(1)
AD_ID = data['id']
print(f"  ✅ Ad ID: {AD_ID}")

# ── RESUMEN ───────────────────────────────────────────────────
print(f"""
{'='*60}
✅ CAMPAÑA V4 CREADA — EN PAUSA

Campaña:  {CAMPAIGN_ID}  →  $40.000 COP/día CBO
Ad Set:   {ADSET_ID}     →  Colombia 18-45 | AddToCart | DCO
Creative: {CREATIVE_ID}
Anuncio:  {AD_ID}        →  15 img × 5 copys × 5 títulos × 5 desc

Combinaciones posibles: {10 * 5 * 5 * 5:,}  (Meta elige las ganadoras)

Próximo paso: revisar en Ads Manager y ACTIVAR cuando estés listo.
URL destino: {URL}
{'='*60}
""")
