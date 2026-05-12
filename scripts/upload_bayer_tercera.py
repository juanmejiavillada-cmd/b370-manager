import paramiko
import os

host = '195.35.15.241'
port = 65002
user = 'u122447978'
password = 'Operacionesb370.'
local_dir = r'C:\Proyectos\b370\PROTOCOLO 1.1 B370\B370-MANAGER\imagenes\para-subir'

images = [
    ('BAYER-MUNCHEN-TERCERA_1.jpg', 'Bayern Munich Tercera 1'),
    ('BAYER-MUNCHEN-TERCERA_2.jpg', 'Bayern Munich Tercera 2'),
    ('BAYER-MUNCHEN-TERCERA_3.jpg', 'Bayern Munich Tercera 3'),
    ('BAYER-MUNCHEN-TERCERA_4.jpg', 'Bayern Munich Tercera 4'),
    ('BAYER-MUNCHEN-TERCERA_5.jpg', 'Bayern Munich Tercera 5'),
    ('BAYER-MUNCHEN-TERCERA_6.jpg', 'Bayern Munich Tercera 6'),
    ('BAYER-MUNCHEN-TERCERA_7.jpg', 'Bayern Munich Tercera 7'),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port=port, username=user, password=password, timeout=30)
print('SSH connected')

# Step 1: Find WP path
print('\n--- Finding WordPress path ---')
stdin, stdout, stderr = ssh.exec_command('find /home -name "wp-config.php" -maxdepth 8 2>/dev/null | head -5')
stdout.channel.recv_exit_status()
wp_configs = stdout.read().decode().strip()
print(f'wp-config.php locations:\n{wp_configs}')

# Derive wp_path from first result
wp_path = None
if wp_configs:
    first_config = wp_configs.split('\n')[0]
    wp_path = os.path.dirname(first_config)
    print(f'Using wp_path: {wp_path}')

if not wp_path:
    print('ERROR: Could not find WordPress path')
    ssh.close()
    exit(1)

# Step 2: Images already uploaded in /tmp - skip re-upload if already there
print('\n--- Checking /tmp for existing uploads ---')
stdin, stdout, stderr = ssh.exec_command('ls /tmp/BAYER-MUNCHEN-TERCERA_*.jpg 2>/dev/null')
stdout.channel.recv_exit_status()
existing = stdout.read().decode().strip()
print(f'Existing in /tmp: {existing}')

# Upload any missing images
sftp = ssh.open_sftp()
for fname, title in images:
    if fname not in existing:
        local_path = os.path.join(local_dir, fname)
        remote_path = f'/tmp/{fname}'
        print(f'Uploading {fname}...')
        sftp.put(local_path, remote_path)
        print(f'  -> /tmp/{fname} OK')
    else:
        print(f'  {fname} already in /tmp, skipping upload')
sftp.close()

# Step 3: Import with WP-CLI
media_ids = {}
for fname, title in images:
    cmd = f'wp media import /tmp/{fname} --title="{title}" --path={wp_path} --porcelain 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f'{fname} -> ID: {out} (exit={exit_status}) err={err[:150] if err else ""}')
    if out.isdigit():
        media_ids[fname] = int(out)
    else:
        media_ids[fname] = out

ssh.close()
print()
print('=== MEDIA IDS ===')
for k, v in media_ids.items():
    print(f'  {k}: {v}')
