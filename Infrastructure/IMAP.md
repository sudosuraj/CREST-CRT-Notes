# IMAP

## Why It Matters

IMAP mailbox access can reveal:

- password reset emails
- sensitive attachments
- operational communications
- internal usernames and systems

Compared with POP3, IMAP is often better for structured mailbox exploration because folders and search are richer.

## Workflow

1. detect IMAP or IMAPS
2. validate credentials
3. enumerate mailboxes
4. search for high-value content
5. translate mail access into account takeover or intelligence

## Detection

```bash
nmap -p 143,993 -sV target.com
nc target.com 143
telnet target.com 143
```

## Step 1: Connect

### IMAP

```text
a1 LOGIN username password
a2 LIST "" "*"
a3 SELECT INBOX
a4 FETCH 1 BODY[]
a5 LOGOUT
```

### IMAPS

```bash
openssl s_client -connect target.com:993 -crlf -quiet
```

### cURL

```bash
curl -u username:password imap://target.com/
curl -u username:password imap://target.com/INBOX -X "FETCH 1 BODY[]"
curl -u username:password imaps://target.com/ --insecure
```

## Step 2: Enumerate Mailboxes

Useful actions:

- list folders
- select `INBOX`
- search for reset and password content
- retrieve only the messages that prove impact

## Step 3: Search For Value

Typical high-value searches:

- password reset
- VPN or MFA setup
- credentials
- confidential attachments
- administrative communications

## Step 4: Credential Testing

If needed and in scope:

```bash
hydra -l user@target.com -P passwords.txt imap://target.com
hydra -l user@target.com -P passwords.txt imaps://target.com:993
hydra -L users.txt -P passwords.txt imap://target.com
```

## Pitfalls

- brute forcing before trying reused credentials
- downloading entire mailboxes without triage
- reporting mailbox access without showing why the content matters

## Reporting Notes

Capture:

- the mailbox accessed
- the credential source
- the folders or messages reviewed
- the specific sensitive content obtained

## Fast Checklist

```text
1. Detect IMAP/IMAPS
2. Validate credentials
3. List mailboxes and select INBOX
4. Search for resets, secrets, and sensitive content
5. Save only the messages needed to prove impact
```
