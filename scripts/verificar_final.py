import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('195.35.15.241', port=65002, username='u122447978', password='Operacionesb370.', timeout=30)

WC_CK = "ck_820f0c1aded087d593791f97abbdeec382b15492"
WC_CS = "cs_6a5f94897927878d28d8d76096e9758e2b103c49"
WC_URL = "https://b370sports.com"
PRODUCT_ID = 3246

# Get full product detail
cmd = f"curl -s '{WC_URL}/wp-json/wc/v3/products/{PRODUCT_ID}' -u '{WC_CK}:{WC_CS}'"
stdin, stdout, stderr = ssh.exec_command(cmd)
resp = stdout.read().decode().strip()
data = json.loads(resp)

print("=== PRODUCT FINAL STATE ===")
print(f"ID: {data['id']}")
print(f"Name: {data['name']}")
print(f"Type: {data['type']}")
print(f"Status: {data['status']}")
print(f"Categories: {[c['name'] for c in data['categories']]}")
print(f"Attributes: {[(a['name'], a['options']) for a in data['attributes']]}")
print(f"Images ({len(data['images'])} total):")
for img in data['images']:
    print(f"  ID={img['id']} src={img['src'][-50:]}")
print(f"Short description: {data['short_description'][:80]}...")

# Verify thumbnail via WP meta
wp_path = '/home/u122447978/domains/b370sports.com/public_html'
cmd2 = f"wp post meta get {PRODUCT_ID} _thumbnail_id --path={wp_path} 2>/dev/null"
stdin, stdout, stderr = ssh.exec_command(cmd2)
thumb = stdout.read().decode().strip()
print(f"\n_thumbnail_id (WP meta): {thumb}")

# Also verify gallery
cmd3 = f"wp post meta get {PRODUCT_ID} _product_image_gallery --path={wp_path} 2>/dev/null"
stdin, stdout, stderr = ssh.exec_command(cmd3)
gallery = stdout.read().decode().strip()
print(f"_product_image_gallery (WP meta): {gallery}")

# Get variations
cmd4 = f"curl -s '{WC_URL}/wp-json/wc/v3/products/{PRODUCT_ID}/variations?per_page=20' -u '{WC_CK}:{WC_CS}'"
stdin, stdout, stderr = ssh.exec_command(cmd4)
resp4 = stdout.read().decode().strip()
vars_data = json.loads(resp4)
print(f"\n=== VARIATIONS ({len(vars_data)}) ===")
for v in vars_data:
    attrs = [(a['name'], a['option']) for a in v['attributes']]
    print(f"  ID={v['id']} | SKU={v['sku']!r:20s} | Price={v['regular_price']} | Stock={v['stock_quantity']} | Attrs={attrs}")

ssh.close()
