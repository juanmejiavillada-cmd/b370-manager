import paramiko
import re

wp_path = "/home/u122447978/domains/b370sports.com/public_html"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("195.35.15.241", port=65002, username="u122447978", password="Operacionesb370.")

# Query WP media for ESPANA-LOCAL images
cmd = f"wp post list --post_type=attachment --post_status=inherit --fields=ID,post_title,guid --search='Espana Local' --path={wp_path} 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode().strip()
print("WP Media search results:")
print(out)

ssh.close()
