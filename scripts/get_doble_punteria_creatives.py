import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, json, time, requests
from datetime import datetime, timezone

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

# IDs de los anuncios de Doble Puntería (AdSet1 - primeros 5)
AD_IDS = [
    "120243009267050179",  # Creative1
    "120243009267540179",  # Creative2
    "120243009267120179",  # Creative3
    "120243009266990179",  # Creative4
    "120243009266980179",  # Creative5
]

print("=== CREATIVOS DOBLE PUNTERÍA ===\n")
page_id = None

for ad_id in AD_IDS:
    r = requests.get(
        f"{BASE}/{ad_id}",
        params={
            "access_token": token,
            "fields": "name,creative{id,image_hash,image_url,video_id,thumbnail_url,object_story_spec,asset_feed_spec}"
        }
    )
    data = r.json()
    creative = data.get('creative', {})

    print(f"Ad: {data.get('name', ad_id)}")
    print(f"  Creative ID: {creative.get('id')}")

    story = creative.get('object_story_spec', {})
    if story.get('page_id') and not page_id:
        page_id = story.get('page_id')
        print(f"  Page ID: {page_id}")

    link_data = story.get('link_data', {})
    photo_data = story.get('photo_data', {})

    if link_data.get('image_hash'):
        print(f"  image_hash: {link_data['image_hash']}")
        print(f"  URL: {link_data.get('link', '')}")
        print(f"  Message: {link_data.get('message', '')[:80]}")
    elif photo_data.get('image_hash'):
        print(f"  image_hash (photo): {photo_data['image_hash']}")
    elif creative.get('image_hash'):
        print(f"  image_hash (direct): {creative['image_hash']}")
    elif creative.get('video_id'):
        print(f"  video_id: {creative['video_id']}")

    if creative.get('thumbnail_url'):
        print(f"  thumbnail: {creative['thumbnail_url'][:80]}...")

    print()
    time.sleep(3)

print(f"\nPage ID para nuevos creativos: {page_id}")
