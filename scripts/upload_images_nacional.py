import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, json, requests
from pathlib import Path

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

IMAGES_DIR = Path(r"C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\data\images\ads\ATLETICO NACIONAL 2026")

hashes = {}
errors = []

print(f"Subiendo imágenes desde: {IMAGES_DIR}\n")

for img_path in sorted(IMAGES_DIR.iterdir()):
    if img_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
        continue

    print(f"  Subiendo: {img_path.name[:60]}...")
    with open(img_path, 'rb') as f:
        r = requests.post(
            f"{BASE}/{AD_ACCOUNT}/adimages",
            files={'filename': (img_path.name, f, 'image/jpeg')},
            data={'access_token': token}
        )

    data = r.json()
    if 'images' in data:
        for fname, img_data in data['images'].items():
            h = img_data.get('hash', '')
            hashes[img_path.name] = h
            print(f"    ✅ hash: {h}")
    elif 'error' in data:
        errors.append((img_path.name, data['error']['message']))
        print(f"    ❌ Error: {data['error']['message']}")
    else:
        errors.append((img_path.name, str(data)))
        print(f"    ❌ Respuesta inesperada: {data}")

print(f"\n{'='*60}")
print(f"RESUMEN: {len(hashes)} subidas OK / {len(errors)} errores")
print(f"\nHASHES PARA DCO:")
for name, h in hashes.items():
    print(f'  "{h}",  # {name[:50]}')

if errors:
    print(f"\nERRORES:")
    for name, msg in errors:
        print(f"  {name}: {msg}")

# Guardar en JSON para usar en el siguiente script
output = {"hashes": hashes, "errors": errors}
out_path = Path(r"C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\data") / "nacional_image_hashes.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\nGuardado en: {out_path}")
