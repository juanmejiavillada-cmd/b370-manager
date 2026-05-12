import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, json, time, requests
from datetime import datetime, timezone

AD_ID = "120237636946710179"

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    env = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

env = load_env()
token = env.get('META_ACCESS_TOKEN', '')

if not token:
    print("ERROR: META_ACCESS_TOKEN no encontrado")
    sys.exit(1)

BASE = "https://graph.facebook.com/v21.0"

def log(script, acct, exit_code, out_bytes, error, summary):
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    log_path = os.path.join(os.path.dirname(__file__), '..', 'meta_api.log')
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{ts} | {script} | acct={acct} | exit={exit_code} | out_bytes={out_bytes} | error={error} | summary={summary}\n")

def call(url, params):
    params['access_token'] = token
    r = requests.get(url, params=params)
    time.sleep(3)
    return r

# 1. Obtener el creative_id del anuncio
r1 = call(f"{BASE}/{AD_ID}", {"fields": "id,name,creative{id,name,body,title,image_url,video_id,thumbnail_url,object_story_spec}"})
data1 = r1.json()
log("get_creative.py", AD_ID, 0 if 'error' not in data1 else 1,
    len(r1.content), data1.get('error', {}).get('message', 'none'),
    "fetch ad creative details")

print("=== AD + CREATIVE ===")
print(json.dumps(data1, indent=2, ensure_ascii=False))

if 'error' in data1:
    print(f"\nERROR API: {data1['error']}")
    sys.exit(1)

creative = data1.get('creative', {})
creative_id = creative.get('id', '')
print(f"\n>>> CREATIVE ID: {creative_id}")
