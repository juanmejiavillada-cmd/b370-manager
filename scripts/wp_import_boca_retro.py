import paramiko

host = '195.35.15.241'
port = 65002
user = 'u122447978'
password = 'Operacionesb370.'
wp_path = '/home/u122447978/domains/b370sports.com/public_html'

images = [
    ('BOCA-RETRO_1.jpg', 'Boca Retro 1'),
    ('BOCA-RETRO_2.jpg', 'Boca Retro 2'),
    ('BOCA-RETRO_3.jpg', 'Boca Retro 3'),
    ('BOCA-RETRO_4.jpg', 'Boca Retro 4'),
    ('BOCA-RETRO_5.jpg', 'Boca Retro 5'),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port=port, username=user, password=password, timeout=30)

ids = {}
for filename, title in images:
    cmd = f'wp media import /tmp/{filename} --title="{title}" --path={wp_path} --porcelain 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=90)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    media_id = out if out.isdigit() else None
    ids[filename] = media_id
    print(f'{filename}: ID={media_id}  RAW={out}  ERR={err}')

ssh.close()
print('\nRESUMEN IDs:', ids)
