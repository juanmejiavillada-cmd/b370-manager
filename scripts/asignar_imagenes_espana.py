import paramiko

wp_path = "/home/u122447978/domains/b370sports.com/public_html"
product_id = 3170
thumbnail_id = 3162
gallery_ids = [3163, 3164, 3165, 3166, 3167, 3168, 3169]
gallery_str = ",".join(str(i) for i in gallery_ids)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("195.35.15.241", port=65002, username="u122447978", password="Operacionesb370.")

# Set thumbnail
cmd1 = f"wp post meta update {product_id} _thumbnail_id {thumbnail_id} --path={wp_path} 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd1)
out1 = stdout.read().decode().strip()
# Get only last meaningful line
lines1 = [l for l in out1.splitlines() if not l.startswith("Warning:")]
print("_thumbnail_id:", "\n".join(lines1) if lines1 else out1)

# Set gallery
cmd2 = f"wp post meta update {product_id} _product_image_gallery '{gallery_str}' --path={wp_path} 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd2)
out2 = stdout.read().decode().strip()
lines2 = [l for l in out2.splitlines() if not l.startswith("Warning:")]
print("_product_image_gallery:", "\n".join(lines2) if lines2 else out2)

# Verify
cmd3 = f"wp post meta get {product_id} _thumbnail_id --path={wp_path} 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd3)
out3 = stdout.read().decode().strip()
lines3 = [l for l in out3.splitlines() if not l.startswith("Warning:")]
print("Verify _thumbnail_id:", "\n".join(lines3))

ssh.close()
print("Imagenes asignadas OK")
