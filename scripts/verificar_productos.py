import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('195.35.15.241', port=65002, username='u122447978', password='Operacionesb370.', timeout=30)

WC_CK = "ck_820f0c1aded087d593791f97abbdeec382b15492"
WC_CS = "cs_6a5f94897927878d28d8d76096e9758e2b103c49"
WC_URL = "https://b370sports.com"

# Check product 3246 (created by curl/WC REST)
for pid in [3245, 3246]:
    cmd = f"curl -s '{WC_URL}/wp-json/wc/v3/products/{pid}' -u '{WC_CK}:{WC_CS}'"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    resp = stdout.read().decode().strip()
    try:
        data = json.loads(resp)
        print(f"\n--- Product {pid} ---")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Type: {data.get('type', 'N/A')}")
        print(f"  Status: {data.get('status', 'N/A')}")
        cats = [c['name'] for c in data.get('categories', [])]
        print(f"  Categories: {cats}")
        attrs = [(a['name'], a['options']) for a in data.get('attributes', [])]
        print(f"  Attributes: {attrs}")
        images = [img['id'] for img in data.get('images', [])]
        print(f"  Images: {images}")
    except Exception as e:
        print(f"Product {pid}: {resp[:200]}")

# Delete post 3245 (the empty WP post created before)
print("\n--- Deleting post 3245 (empty WP-CLI created post) ---")
del_cmd = f"curl -s -X DELETE '{WC_URL}/wp-json/wc/v3/products/3245?force=true' -u '{WC_CK}:{WC_CS}'"
stdin, stdout, stderr = ssh.exec_command(del_cmd)
resp = stdout.read().decode().strip()
try:
    data = json.loads(resp)
    print(f"  Deleted: {data.get('id', 'N/A')} - {data.get('name', data.get('code', 'unknown'))}")
except:
    print("  Response:", resp[:200])

ssh.close()
