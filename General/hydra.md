## Hydra

### Basic Usage

**NOTE:** Capital `-L` allows specifying username list.
```
hydra -l <username> -P <password list> <target> <protocol> [options]
```

### Protocol Specific Usage

#### HTTP / HTTP-GET/POST

**NOTE:** The `login_failed_string` string used in example below is text that appears in the HTTP response when a login attempt **FAILS**.
```
hydra -l <username> -P <password list> <target> http-get /path
hydra -l admin -P /path/to/password_list.txt 127.0.0.1 http-post-form "/login.php:user=^USER^&pass=^PASS^:F=login_failed_string"
```
#### FTP
```
hydra -l admin -P /path/to/password_list.txt ftp://192.168.1.100
```

#### SSH
```
hydra -l root -P /path/to/password_list.txt ssh://192.168.1.100
```

#### Telnet
```
hydra -l <username> -P <password list> <target> telnet
hydra -l admin -P wordlist.txt telnet://<IP>
hydra -L users.txt -P passwords.txt telnet://<IP>
```

#### RDP
```
hydra -l <username> -P <password list> <target> rdp
```

#### SMTP
```
hydra -l user@target.com -P passwords.txt smtp://target.com:587
hydra -L users.txt -P passwords.txt smtp://target.com:587
```

#### POP3 
```
hydra -l user@target.com -P passwords.txt pop3://target.com
hydra -l user@target.com -P passwords.txt pop3s://target.com:995
hydra -L users.txt -P passwords.txt pop3://target.com
```

#### IMAP
```
hydra -l user@target.com -P passwords.txt imap://target.com
hydra -l user@target.com -P passwords.txt imaps://target.com:993
hydra -L users.txt -P passwords.txt imap://target.com
```

#### LDAP
```
hydra -L users.txt -P passwords.txt target.com ldap2 -s 389
```

#### MSSQL
```
hydra -L users.txt -P passwords.txt <IP> mssql
hydra -l sa -P /usr/share/wordlists/rockyou.txt target.com mssql
```

#### MySQL
```
hydra -L users.txt -P passwords.txt <IP> mysql
```