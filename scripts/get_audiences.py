import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, json, time, requests
from datetime import datetime, timezone

AD_ACCOUNT = "act_25577388011912523"

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
token = env.get('META_ACCESS_TOKEN', '')
BASE = "https://graph.facebook.com/v21.0"

r = requests.get(
    f"{BASE}/{AD_ACCOUNT}/customaudiences",
    params={"access_token": token, "fields": "id,name,approximate_count,delivery_status,subtype"}
)
time.sleep(3)
data = r.json()

ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
with open(os.path.join(os.path.dirname(__file__), '..', 'meta_api.log'), 'a', encoding='utf-8') as f:
    f.write(f"{ts} | get_audiences.py | acct={AD_ACCOUNT} | exit={0 if 'error' not in data else 1} | out_bytes={len(r.content)} | error={'none' if 'error' not in data else data['error'].get('message','?')} | summary=fetch custom audiences\n")

audiences = data.get('data', [])
print(f"Total audiencias: {len(audiences)}\n")
for a in audiences:
    print(f"ID: {a['id']} | Nombre: {a['name']} | Tipo: {a.get('subtype','?')} | Tamaño: {a.get('approximate_count','?')}")
