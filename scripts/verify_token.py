import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, json, requests

def load_token():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    with open(env_path) as f:
        for line in f:
            if line.startswith('META_ACCESS_TOKEN='):
                return line.split('=', 1)[1].strip()
    return None

token = load_token()
if not token:
    print("ERROR: META_ACCESS_TOKEN no encontrado en .env")
    sys.exit(1)

debug = requests.get(
    f"https://graph.facebook.com/v21.0/debug_token",
    params={"input_token": token, "access_token": token}
).json()

perms_resp = requests.get(
    f"https://graph.facebook.com/v21.0/me/permissions",
    params={"access_token": token}
).json()

data = debug.get("data", {})
granted = [p["permission"] for p in perms_resp.get("data", []) if p.get("status") == "granted"]

out = {
    "type": data.get("type", "unknown"),
    "app_id": data.get("app_id", ""),
    "expires_at": data.get("expires_at", 0),
    "is_valid": data.get("is_valid", False),
    "permissions_granted": granted,
    "has_ads_management": "ads_management" in granted,
}

with open(os.path.join(os.path.dirname(__file__), '..', 'token_info.json'), 'w') as f:
    json.dump(out, f, indent=2)

print(json.dumps(out, indent=2, ensure_ascii=False))
