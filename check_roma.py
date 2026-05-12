import requests, os
from dotenv import load_dotenv
load_dotenv()
url = os.getenv('WC_URL')
ck = os.getenv('WC_CK')
cs = os.getenv('WC_CS')
r = requests.get(url + '/wp-json/wc/v3/products', params={'search': 'Roma Retro', 'per_page': 10}, auth=(ck, cs))
print('Status:', r.status_code)
data = r.json()
if isinstance(data, list):
    for p in data:
        print('ID:', p['id'], '| Nombre:', p['name'], '| Status:', p['status'])
    print('Total:', len(data))
else:
    print(data)
