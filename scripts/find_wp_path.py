import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("195.35.15.241", port=65002, username="u122447978", password="Operacionesb370.")

# Find wp-config.php location
stdin, stdout, stderr = ssh.exec_command("find /home/u122447978 -name 'wp-config.php' 2>/dev/null | head -5")
out = stdout.read().decode().strip()
print("wp-config.php locations:")
print(out)

# Also check home dir structure
stdin, stdout, stderr = ssh.exec_command("ls /home/u122447978/")
out2 = stdout.read().decode().strip()
print("\nHome dir:")
print(out2)

# Check domains
stdin, stdout, stderr = ssh.exec_command("ls /home/u122447978/domains/ 2>/dev/null")
out3 = stdout.read().decode().strip()
print("\nDomains:")
print(out3)

ssh.close()
