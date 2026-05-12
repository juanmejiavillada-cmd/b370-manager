import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('195.35.15.241', port=65002, username='u122447978', password='Operacionesb370.', timeout=30)

# Create product via WP-CLI on the remote server
wp_path = '/home/u122447978/domains/b370sports.com/public_html'

guia_html = '<img src=\\"https://b370sports.com/wp-content/uploads/2025/11/GUIA-DE-TALLAS.png\\" alt=\\"Guia de tallas B370\\" style=\\"max-width:100%;height:auto;\\" />'

wp_cmd = f'''wp post create --path={wp_path} --post_type=product --post_status=publish --post_title="Manchester United Local" --porcelain 2>&1'''

stdin, stdout, stderr = ssh.exec_command(wp_cmd)
out = stdout.read().decode().strip()
print("post create output:", out)

# The MCP tools should be used instead - let's use WC REST via curl from the server
WC_CK = "ck_820f0c1aded087d593791f97abbdeec382b15492"
WC_CS = "cs_6a5f94897927878d28d8d76096e9758e2b103c49"
WC_URL = "https://b370sports.com"

product_payload = {
    "name": "Manchester United Local",
    "type": "variable",
    "status": "publish",
    "catalog_visibility": "visible",
    "categories": [{"id": 93}],
    "short_description": '<img src="https://b370sports.com/wp-content/uploads/2025/11/GUIA-DE-TALLAS.png" alt="Guia de tallas B370" style="max-width:100%;height:auto;" />',
    "images": [
        {"id": 3239},
        {"id": 3240},
        {"id": 3241},
        {"id": 3242},
        {"id": 3243},
        {"id": 3244},
    ],
    "attributes": [
        {
            "name": "Tallas",
            "slug": "tallas",
            "position": 0,
            "visible": True,
            "variation": True,
            "options": ["S", "M", "L", "XL", "XXL"],
        },
        {
            "name": "Calidad",
            "slug": "calidad",
            "position": 1,
            "visible": True,
            "variation": True,
            "options": ["Tipo original"],
        },
    ],
}

payload_json = json.dumps(product_payload).replace("'", "'\\''")
curl_cmd = f"""curl -s -X POST '{WC_URL}/wp-json/wc/v3/products' \\
  -u '{WC_CK}:{WC_CS}' \\
  -H 'Content-Type: application/json' \\
  -d '{payload_json}'"""

stdin, stdout, stderr = ssh.exec_command(curl_cmd)
response = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print("CURL response:")
try:
    data = json.loads(response)
    if "id" in data:
        print(f"Product ID: {data['id']}")
        print(f"Name: {data['name']}")
        print(f"Status: {data['status']}")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print("Raw response:", response[:2000])
    if err:
        print("STDERR:", err[:500])

ssh.close()
