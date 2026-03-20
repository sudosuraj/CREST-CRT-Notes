# POP3

## Why It Matters

POP3 is useful when valid mailbox credentials give access to:

- password reset emails
- internal communications
- sensitive attachments
- account takeover paths through mail content

POP3 is less about service exploitation and more about what mail access unlocks.

## Workflow

1. detect POP3 or POP3S
2. validate credentials
3. enumerate mailbox size and messages
4. read high-value mail content
5. turn emails into credentials, reset paths, or internal intelligence

## Detection

```bash
nmap -p 110,995 -sV target.com
nc target.com 110
telnet target.com 110
```

## Step 1: Connect

### POP3

```text
USER username
PASS password
LIST
RETR 1
QUIT
```

### POP3S

```bash
openssl s_client -connect target.com:995 -crlf -quiet
```

### cURL

```bash
curl -u username:password pop3://target.com/
curl -u username:password pop3://target.com/1
curl -u username:password pop3s://target.com/ --insecure
```

## Step 2: Credential Testing

If needed and in scope:

```bash
hydra -l user@target.com -P passwords.txt pop3://target.com
hydra -l user@target.com -P passwords.txt pop3s://target.com:995
hydra -L users.txt -P passwords.txt pop3://target.com
```

## Step 3: Message Triage

After access:

- check message count
- pull recent or reset-related emails
- search downloaded mail for credentials and URLs

## High-Value Mail Content

Look for:

- password reset links
- welcome emails with temporary passwords
- VPN or MFA instructions
- shared secrets or attachments

## Pitfalls

- brute forcing before trying reused mail creds
- downloading everything without prioritizing high-value messages
- forgetting that POP3 is usually one mailbox, not full enterprise mail admin access

## Reporting Notes

Capture:

- the mailbox accessed
- the credential source
- the sensitive content obtained
- the downstream impact, such as reset or credential discovery

## Fast Checklist

```text
1. Detect POP3/POP3S
2. Validate credentials
3. List and retrieve messages
4. Search for reset, credential, and secret content
5. Save only the mail needed to prove impact
```
