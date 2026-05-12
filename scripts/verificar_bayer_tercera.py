import requests
from requests.auth import HTTPBasicAuth

WC_URL = 'https://b370sports.com'
WC_CK = 'ck_820f0c1aded087d593791f97abbdeec382b15492'
WC_CS = 'cs_6a5f94897927878d28d8d76096e9758e2b103c49'

auth = HTTPBasicAuth(WC_CK, WC_CS)
product_id = 3221
media_ids = [3214, 3215, 3216, 3217, 3218, 3219, 3220]

# Verify product and its images
resp = requests.get(
    f'{WC_URL}/wp-json/wc/v3/products/{product_id}',
    auth=auth
)
product = resp.json()
print(f'Product: {product["name"]} (ID {product["id"]})')
print(f'Status: {product["status"]}')
print(f'Images count: {len(product.get("images", []))}')
for img in product.get("images", []):
    print(f'  ID {img["id"]}: {img["src"][-50:]}')

# Verify via SSH that _thumbnail_id and _product_image_gallery are set correctly
import paramiko
host = '195.35.15.241'
port = 65002
user = 'u122447978'
password = 'Operacionesb370.'
wp_path = '/home/u122447978/domains/b370sports.com/public_html'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port=port, username=user, password=password, timeout=30)

print('\n--- WP post meta check ---')
cmd = f'wp post meta get {product_id} _thumbnail_id --path={wp_path} 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd)
stdout.channel.recv_exit_status()
out = stdout.read().decode().strip()
print(f'_thumbnail_id: {out}')

cmd2 = f'wp post meta get {product_id} _product_image_gallery --path={wp_path} 2>&1'
stdin, stdout, stderr = ssh.exec_command(cmd2)
stdout.channel.recv_exit_status()
out2 = stdout.read().decode().strip()
print(f'_product_image_gallery: {out2}')

ssh.close()

# If thumbnail is not set correctly, fix it
print('\n--- Checking if images need to be explicitly assigned ---')
# The WC REST API should have set these when images array was passed
# First image = thumbnail, rest = gallery
expected_thumbnail = str(media_ids[0])
expected_gallery = ','.join(str(i) for i in media_ids[1:])

# Parse out the actual ID from the meta (strip warnings)
actual_thumbnail = [line for line in out.split('\n') if line.strip().isdigit()]
actual_thumbnail = actual_thumbnail[-1] if actual_thumbnail else ''

if actual_thumbnail == expected_thumbnail:
    print(f'Thumbnail OK: {actual_thumbnail}')
else:
    print(f'Thumbnail mismatch. Expected {expected_thumbnail}, got {actual_thumbnail!r}')
    print('Will fix via WP-CLI...')

print(f'\nExpected gallery: {expected_gallery}')
print(f'Actual gallery: {out2}')
