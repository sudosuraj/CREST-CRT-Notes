## Hydra

### Why It Matters

Hydra is a remote authentication testing tool. Its value comes from disciplined use, not volume. Use it when you already have:

- a good username list
- a focused password list or spray candidate
- a clear target protocol
- lockout-aware scope

### Workflow

1. identify the target protocol and auth format
2. choose single-user, multi-user, or combo-file mode
3. keep the password set small and relevant
4. validate hits immediately in the native client

### Core Patterns

```bash
hydra -l <username> -P <password_list> <target> <protocol>
hydra -L users.txt -P passwords.txt <service>://<ip>
hydra -L users.txt -p Password123 <service>://<ip>
hydra -C userpass.txt <service>://<ip>
```

### Common Protocol Examples

```bash
hydra -l admin -P passwords.txt 127.0.0.1 http-post-form "/login.php:user=^USER^&pass=^PASS^:F=login_failed_string"
hydra -L users.txt -P passwords.txt ssh://<ip>
hydra -L users.txt -P passwords.txt ftp://<ip>
hydra -L users.txt -P passwords.txt telnet://<ip>
hydra -L users.txt -P passwords.txt smtp://target.com:587
hydra -L users.txt -P passwords.txt pop3://target.com
hydra -L users.txt -P passwords.txt imap://target.com
hydra -L users.txt -P passwords.txt target.com ldap2 -s 389
hydra -L users.txt -P passwords.txt <ip> mssql
hydra -L users.txt -P passwords.txt <ip> mysql
```

### Selection Logic

Use Hydra when:

- the protocol is directly supported
- you know the failure condition
- the target will tolerate the test volume

Do not use it blindly on unstable services or high-risk lockout targets.

### Pitfalls

- using huge generic wordlists without context
- spraying without understanding lockout
- trusting Hydra success without validating in the native client

### Reporting Notes

Hydra itself is usually not the report item. The report item is weak password policy, default credentials, or password reuse.

### Fast Checklist

```text
1. Pick the right protocol module
2. Use a tight user and password set
3. Stay lockout-aware
4. Validate any hit immediately
5. Report the credential weakness, not the tool
```
