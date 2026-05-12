import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, json, time, requests

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

CAMPAIGN_ID = "120243009261500179"
ADSET1_ID = "120243009266450179"
ADSET2_ID = "120243009265490179"

def get(endpoint, fields):
    r = requests.get(f"{BASE}/{endpoint}", params={"access_token": token, "fields": fields})
    time.sleep(2)
    return r.json()

print("=== TARGETING AD SETS ===\n")
for adset_id, name in [(ADSET1_ID, "AdSet1"), (ADSET2_ID, "AdSet2")]:
    data = get(adset_id, "name,targeting,optimization_goal,billing_event,promoted_object,destination_type,daily_budget,lifetime_budget,bid_strategy")
    print(f"--- {name} ---")
    print(f"Optimization: {data.get('optimization_goal')}")
    print(f"Billing: {data.get('billing_event')}")
    print(f"Destination: {data.get('destination_type')}")
    print(f"Promoted object: {json.dumps(data.get('promoted_object', {}))}")
    targeting = data.get('targeting', {})
    print(f"Targeting:")
    print(f"  Age: {targeting.get('age_min')} - {targeting.get('age_max')}")
    print(f"  Geo: {json.dumps(targeting.get('geo_locations', {}))}")
    print(f"  Custom audiences: {json.dumps(targeting.get('custom_audiences', []))}")
    print(f"  Flexible spec: {json.dumps(targeting.get('flexible_spec', []))}")
    print(f"  Exclusions: {json.dumps(targeting.get('exclusions', {}))}")
    print(f"  Gender: {targeting.get('genders', 'all')}")
    print()

print("\n=== ADS DE ADSET2 ===\n")
ads2 = get(f"{ADSET2_ID}/ads", "id,name,creative{id,image_hash,image_url,video_id,object_story_spec,asset_feed_spec,title,body}")
for ad in ads2.get('data', []):
    creative = ad.get('creative', {})
    print(f"Ad: {ad.get('name')} | ID: {ad.get('id')}")
    print(f"  Creative ID: {creative.get('id')}")
    story = creative.get('object_story_spec', {})
    link_data = story.get('link_data', {})
    photo_data = story.get('photo_data', {})
    if link_data.get('image_hash'):
        print(f"  image_hash: {link_data['image_hash']}")
        print(f"  title: {link_data.get('name', '')}")
        print(f"  description: {link_data.get('description', '')}")
        print(f"  message: {link_data.get('message', '')[:100]}")
        print(f"  link: {link_data.get('link', '')}")
    elif creative.get('image_hash'):
        print(f"  image_hash (direct): {creative['image_hash']}")
    elif creative.get('video_id'):
        print(f"  video_id: {creative['video_id']}")
    print()

print("\n=== ADS DE ADSET1 (títulos y descripciones) ===\n")
ads1 = get(f"{ADSET1_ID}/ads", "id,name,creative{id,image_hash,object_story_spec}")
for ad in ads1.get('data', []):
    creative = ad.get('creative', {})
    story = creative.get('object_story_spec', {})
    link_data = story.get('link_data', {})
    print(f"Ad: {ad.get('name')}")
    if link_data:
        print(f"  title: {link_data.get('name', '(vacío)')}")
        print(f"  description: {link_data.get('description', '(vacío)')}")
        print(f"  message: {link_data.get('message', '(vacío)')[:100]}")
    print()
