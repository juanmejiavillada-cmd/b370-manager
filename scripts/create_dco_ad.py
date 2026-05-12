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
ADSET_ID = "120243092386570179"
PIXEL_ID = "2015110402400663"
URL = "https://b370sports.com/atletico-nacional-2026/"

IMAGE_HASHES = [
    "65219ded179a323a29e411f7f50608aa",
    "7f419be1b258bcd141d9becaa256906e",
    "f8175db9d5c25ee72f3d56ecc039a66f",
    "9a101a485aea56c91eae8c1fe93659ab",
    "a9ba12127b66805835e11db9104a0044",
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

# Crear el anuncio con creative inline (asset_feed_spec + object_story_spec)
print("[1] Creando anuncio DCO con creative inline...")
asset_feed_spec = {
    "images": [{"hash": h} for h in IMAGE_HASHES],
    "bodies": [{"text": b} for b in BODIES],
    "titles": [{"text": t} for t in TITLES],
    "descriptions": [{"text": d} for d in DESCRIPTIONS],
    "link_urls": [{"website_url": URL}],
    "call_to_action_types": ["SHOP_NOW"],
    "ad_formats": ["SINGLE_IMAGE"],
}

# Paso 1: crear adcreative separado
print("[1a] Creando adcreative DCO...")
creative_payload = {
    "name": "B370 | Nacional 2026 | DCO Creative | 5img × 5copy",
    "object_story_spec": json.dumps({"page_id": PAGE_ID}),
    "asset_feed_spec": json.dumps(asset_feed_spec),
    "access_token": token,
}
r_cr = requests.post(f"{BASE}/{AD_ACCOUNT}/adcreatives", data=creative_payload)
cr_data = r_cr.json()
print(f"  Status: {r_cr.status_code}")
print(f"  Response: {json.dumps(cr_data, ensure_ascii=False, indent=2)}")

if 'error' in cr_data:
    print(f"❌ Error creando creative: {cr_data['error']['message']}")
    sys.exit(1)

creative_id = cr_data['id']
print(f"  ✅ Creative ID: {creative_id}")

# Paso 2: crear el ad referenciando el creative
ad_payload = {
    "name": "B370 | Nacional 2026 | DCO | 5img × 5copy",
    "adset_id": ADSET_ID,
    "creative": json.dumps({"creative_id": creative_id}),
    "tracking_specs": json.dumps([{"action.type": ["offsite_conversion"], "fb_pixel": [PIXEL_ID]}]),
    "status": "PAUSED",
    "access_token": token,
}

r2 = requests.post(f"{BASE}/{AD_ACCOUNT}/ads", data=ad_payload)
ad_data = r2.json()
print(f"  Status: {r2.status_code}")
print(f"  Response: {json.dumps(ad_data, ensure_ascii=False, indent=2)}")

if 'error' in ad_data:
    print(f"❌ Error creando ad: {ad_data['error']['message']}")
    sys.exit(1)

ad_id = ad_data.get('id')
print(f"  ✅ Ad ID: {ad_id}")

# Paso 3: Activar el anuncio
print("\n[3] Activando anuncio...")
r3 = requests.post(
    f"{BASE}/{ad_id}",
    data={"status": "ACTIVE", "access_token": token}
)
act_data = r3.json()
if act_data.get('success'):
    print(f"  ✅ Anuncio ACTIVO")
else:
    print(f"  Respuesta: {act_data}")

print(f"\n✅ DCO listo — Ad ID: {ad_id}")
print(f"   5 imágenes × 5 copys × 5 títulos × 5 descripciones")
print(f"   Meta probará las combinaciones y optimizará sola.")
