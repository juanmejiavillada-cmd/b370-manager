"""Verificar y crear directorios remotos, luego subir imagenes"""
import paramiko, os
from dotenv import load_dotenv

load_dotenv()
SSH_HOST = os.getenv('SSH_HOST')
SSH_PORT = int(os.getenv('SSH_PORT', 65002))
SSH_USER = os.getenv('SSH_USER')
SSH_PASS = os.getenv('SSH_PASS')
REMOTE_DIR = '/home/u723505263/domains/b370sports.com/public_html/wp-content/uploads/b370/'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS, timeout=30)
print(f'Conectado como {SSH_USER}')

# Verificar home y estructura
for cmd in [
    'echo "HOME=$HOME"',
    'echo "USER=$(whoami)"',
    'ls ~/domains/b370sports.com/public_html/wp-content/uploads/ | head -20',
    f'mkdir -p {REMOTE_DIR}',
    f'ls -la {REMOTE_DIR}',
    'which wp || echo "wp not found"',
    'wp --info --path=/home/u723505263/domains/b370sports.com/public_html 2>&1 | head -5',
]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f'\n$ {cmd}')
    if out: print(out)
    if err: print('ERR:', err[:200])

ssh.close()
