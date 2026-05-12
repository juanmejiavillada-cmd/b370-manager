import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('195.35.15.241', port=65002, username='u122447978', password='Operacionesb370.', timeout=30)

wp_path = '/home/u122447978/domains/b370sports.com/public_html'

images = [
    ('MAN-UNITED-LOCAL_1.jpg', 'Manchester United Local 1'),
    ('MAN-UNITED-LOCAL_2.jpg', 'Manchester United Local 2'),
    ('MAN-UNITED-LOCAL_3.jpg', 'Manchester United Local 3'),
    ('MAN-UNITED-LOCAL_4.jpg', 'Manchester United Local 4'),
    ('MAN-UNITED-LOCAL_5.jpg', 'Manchester United Local 5'),
    ('MAN-UNITED-LOCAL_6.jpg', 'Manchester United Local 6'),
]

media_ids = {}
for img_file, img_title in images:
    cmd = f'wp media import /tmp/{img_file} --title="{img_title}" --path={wp_path} --porcelain 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f'{img_file}: ID={out}', flush=True)
    if err:
        print(f'  STDERR: {err}', flush=True)
    media_ids[img_file] = out

ssh.close()
print('DONE')
print('media_ids =', media_ids)
