import paramiko
import re

wp_path = "/home/u122447978/domains/b370sports.com/public_html"

images = [
    ("ESPANA-LOCAL_1.jpg", "Espana Local 1"),
    ("ESPANA-LOCAL_2.jpg", "Espana Local 2"),
    ("ESPANA-LOCAL_3.jpg", "Espana Local 3"),
    ("ESPANA-LOCAL_4.jpg", "Espana Local 4"),
    ("ESPANA-LOCAL_5.jpg", "Espana Local 5"),
    ("ESPANA-LOCAL_6.jpg", "Espana Local 6"),
    ("ESPANA-LOCAL_7.jpg", "Espana Local 7"),
    ("ESPANA-LOCAL_8.jpg", "Espana Local 8"),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("195.35.15.241", port=65002, username="u122447978", password="Operacionesb370.")

media_ids = {}

for fname, title in images:
    cmd = f"wp media import /tmp/{fname} --title='{title}' --path={wp_path} --porcelain 2>&1"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    # porcelain output: last line is just the attachment ID (after warnings)
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    # The attachment ID is the last line that is purely a number
    att_id = None
    for line in reversed(lines):
        if re.match(r"^\d+$", line):
            att_id = int(line)
            break
    media_ids[fname] = att_id
    print(f"File: {fname} | AttachmentID: {att_id}")

ssh.close()

print()
print("=== MEDIA IDs ===")
for k, v in media_ids.items():
    print(f"{k} -> {v}")
