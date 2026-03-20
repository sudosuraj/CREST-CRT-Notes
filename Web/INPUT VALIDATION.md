# 1. INPUT VALIDATION - COMPLETE GUIDE <a name="input-validation"></a>

## 1.1 THEORY & IMPORTANCE

### Why Input Validation?

**Input validation is the first line of defense against:**
- SQL Injection
- XSS
- Command Injection
- Path Traversal
- LDAP Injection
- XML Injection
- Buffer Overflows
- Business Logic Flaws

**Defense in Depth:**
Input validation should be ONE layer in a multi-layered security approach:
1. Input Validation
2. Output Encoding
3. Parameterized Queries
4. Least Privilege
5. WAF (Web Application Firewall)

---

## 1.2 VALIDATION STRATEGIES

### 1.2.1 Allowlist (Whitelist) - RECOMMENDED

**Definition:** Only explicitly allowed input is accepted.

**Advantages:**
- Most secure approach
- Explicit definition of valid input
- Easier to maintain

**Disadvantages:**
- Requires knowing all valid inputs
- May be too restrictive for some use cases
- Can break legitimate functionality if not designed properly

**Examples:**

```php
// PHP - Allowlist for user role
$allowed_roles = ['user', 'admin', 'moderator'];
$user_role = $_POST['role'];

if (in_array($user_role, $allowed_roles, true)) {
    // Process valid role
} else {
    // Reject invalid input
    die('Invalid role');
}

// Allowlist for file extensions
$allowed_extensions = ['jpg', 'jpeg', 'png', 'gif'];
$file_extension = strtolower(pathinfo($_FILES['upload']['name'], PATHINFO_EXTENSION));

if (in_array($file_extension, $allowed_extensions, true)) {
    // Process file upload
} else {
    die('Invalid file type');
}

// Allowlist for numeric ID
$id = $_GET['id'];
if (ctype_digit($id) && $id > 0 && $id < 1000000) {
    // Valid ID
} else {
    die('Invalid ID');
}

// Allowlist for specific characters (alphanumeric)
$username = $_POST['username'];
if (preg_match('/^[a-zA-Z0-9_]{3,20}$/', $username)) {
    // Valid username
} else {
    die('Invalid username');
}
```

```javascript
// JavaScript - Allowlist for country codes
const allowedCountries = ['US', 'UK', 'CA', 'AU', 'DE', 'FR'];
const country = req.body.country;

if (allowedCountries.includes(country)) {
    // Process
} else {
    return res.status(400).send('Invalid country');
}

// Allowlist using regex
const email = req.body.email;
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

if (emailRegex.test(email)) {
    // Valid email format
} else {
    return res.status(400).send('Invalid email');
}
```

```python
# Python - Allowlist for actions
ALLOWED_ACTIONS = ['view', 'edit', 'delete']
action = request.form.get('action')

if action in ALLOWED_ACTIONS:
    # Process action
else:
    return 'Invalid action', 400

# Allowlist for date format
import re
date = request.form.get('date')
if re.match(r'^\d{4}-\d{2}-\d{2}$', date):
    # Valid date format (YYYY-MM-DD)
else:
    return 'Invalid date format', 400
```

### 1.2.2 Denylist (Blacklist) - NOT RECOMMENDED

**Definition:** Known bad input is rejected, everything else is allowed.

**Advantages:**
- Less restrictive
- Allows more flexibility

**Disadvantages:**
- Easy to bypass
- Requires knowing all possible attack vectors
- Incomplete by nature
- Can be circumvented with encoding, case changes, etc.

**Examples (and why they fail):**

```php
// PHP - WEAK denylist
$input = $_GET['search'];

// Block common XSS strings
$bad_strings = ['<script>', 'javascript:', 'onerror='];

foreach ($bad_strings as $bad) {
    if (stripos($input, $bad) !== false) {
        die('Invalid input');
    }
}

// BYPASS:
// <Script> (case variation)
// <scr<script>ipt> (nested tags)
// <img src=x onerror=alert(1)> (not in denylist)
// JaVaScRiPt: (case variation)
// javas	cript: (tab character)
```

```python
# Python - WEAK denylist for SQL Injection
query = request.form.get('query')

# Block SQL keywords
blocked = ['SELECT', 'DROP', 'DELETE', 'INSERT', 'UPDATE']

for keyword in blocked:
    if keyword.upper() in query.upper():
        return 'Invalid input', 400

# BYPASS:
# SeLeCt (case variation)
# SEL/*comment*/ECT (comment injection)
# UNION SELECT (UNION not in list)
# ' OR '1'='1 (logic-based, no keywords)
```

**Why Denylists Fail:**
- Encoding bypasses (URL, HTML, Unicode, etc.)
- Case variations
- Comment injection
- Nested payloads
- Alternative syntax
- Incomplete list of bad patterns

### 1.2.3 Data Sanitization

**Definition:** Transforming input to make it safe by removing or encoding dangerous characters.

**Approaches:**
1. **Encoding:** Convert special characters to safe representation
2. **Escaping:** Add escape characters before special characters
3. **Removing:** Delete dangerous characters entirely

**Examples:**

```php
// PHP - HTML encoding (for display)
$user_input = $_POST['comment'];
$safe_output = htmlspecialchars($user_input, ENT_QUOTES, 'UTF-8');
echo $safe_output; // <script> becomes &lt;script&gt;

// URL encoding
$url_param = $_GET['redirect'];
$safe_url = urlencode($url_param);

// SQL escaping (still use parameterized queries!)
$search = $_POST['search'];
$safe_search = mysqli_real_escape_string($conn, $search);

// Remove all HTML tags
$clean_text = strip_tags($user_input);

// Allow only specific HTML tags
$clean_html = strip_tags($user_input, '<p><br><strong><em>');

// Using HTMLPurifier (library for advanced sanitization)
require_once 'HTMLPurifier.auto.php';
$config = HTMLPurifier_Config::createDefault();
$purifier = new HTMLPurifier($config);
$clean_html = $purifier->purify($dirty_html);
```

```javascript
// JavaScript - DOMPurify (sanitization library)
import DOMPurify from 'dompurify';

const dirty = req.body.content;
const clean = DOMPurify.sanitize(dirty);

// Manual sanitization (not recommended, use library)
function sanitizeHTML(str) {
    const temp = document.createElement('div');
    temp.textContent = str;
    return temp.innerHTML;
}

// Remove script tags (weak, use DOMPurify instead)
function stripScripts(str) {
    return str.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
}
```

```python
# Python - bleach (sanitization library)
import bleach

dirty_html = request.form.get('content')

# Allow only specific tags and attributes
clean_html = bleach.clean(
    dirty_html,
    tags=['p', 'br', 'strong', 'em', 'a'],
    attributes={'a': ['href', 'title']},
    strip=True
)

# HTML escaping
import html
user_input = request.form.get('comment')
safe_output = html.escape(user_input)

# URL encoding
from urllib.parse import quote
url_param = request.args.get('redirect')
safe_url = quote(url_param)
```

**Sanitization Best Practices:**
- Sanitize at the last moment (output encoding)
- Use well-tested libraries (DOMPurify, HTMLPurifier, bleach)
- Context-aware sanitization (HTML vs URL vs JavaScript)
- Don't rely on sanitization alone - combine with validation

---

## 1.3 CLIENT-SIDE vs SERVER-SIDE VALIDATION

### 1.3.1 Client-Side Validation

**Purpose:**
- Improve user experience
- Provide immediate feedback
- Reduce server load

**Implementation:**

```html
<!-- HTML5 validation -->
<form>
    <input type="email" required>
    <input type="number" min="1" max="100" required>
    <input type="text" pattern="[A-Za-z]{3,20}" required>
    <input type="submit">
</form>

<!-- JavaScript validation -->
<script>
function validateForm() {
    var email = document.getElementById('email').value;
    var regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!regex.test(email)) {
        alert('Invalid email');
        return false;
    }
    return true;
}
</script>
<form onsubmit="return validateForm()">
    <input type="text" id="email">
    <input type="submit">
</form>
```

**Why Client-Side Validation is NOT Secure:**

```bash
# Easy to bypass with:

# 1. Browser Developer Tools
# Remove 'required' attribute
# Change input type
# Disable JavaScript

# 1. Proxy tools (Burp Suite)
# Intercept request
# Modify parameters
# Forward to server

# 3. Direct API calls
curl -X POST http://site.com/api/user \
  -d '{"email":"not-an-email","age":-5}'

# 4. Custom script
import requests
requests.post('http://site.com/api/user', 
    json={'email': '<script>alert(1)</script>', 'age': 999})
```

**Demonstration:**

```html
<!-- Client-side validation only (VULNERABLE) -->
<form action="/register" method="POST" onsubmit="return validate()">
    <input type="text" id="username" required pattern="[a-zA-Z0-9]{3,20}">
    <input type="password" id="password" required minlength="8">
    <input type="submit">
</form>

<script>
function validate() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    
    if (username.length < 3) {
        alert('Username too short');
        return false;
    }
    if (password.length < 8) {
        alert('Password too short');
        return false;
    }
    return true;
}
</script>

<!-- Bypass with Burp Suite: -->
<!-- 1. Intercept POST request -->
<!-- 2. Change username to: <script>alert(1)</script> -->
<!-- 3. Change password to: 123 -->
<!-- 4. Forward - validation bypassed! -->
```

### 1.3.2 Server-Side Validation (ESSENTIAL)

**Why Server-Side Validation is Critical:**
- Cannot be bypassed by client
- Centralized validation logic
- Protection against all clients (web, mobile, API)
- Mandatory security control

**Implementation:**

```php
// PHP - Server-side validation
<?php
// Never trust client input

$username = $_POST['username'];
$password = $_POST['password'];
$email = $_POST['email'];

// Validate username
if (!preg_match('/^[a-zA-Z0-9_]{3,20}$/', $username)) {
    die('Invalid username format');
}

// Validate password
if (strlen($password) < 8) {
    die('Password too short');
}
if (!preg_match('/[A-Z]/', $password) || 
    !preg_match('/[a-z]/', $password) || 
    !preg_match('/[0-9]/', $password)) {
    die('Password must contain uppercase, lowercase, and digit');
}

// Validate email
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    die('Invalid email format');
}

// Additional validation
if (strlen($username) > 20 || strlen($password) > 100) {
    die('Input too long');
}

// All validation passed, proceed with registration
?>
```

```javascript
// Node.js/Express - Server-side validation
const express = require('express');
const app = express();

app.post('/register', (req, res) => {
    const {username, password, email} = req.body;
    
    // Validate username
    if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
        return res.status(400).send('Invalid username');
    }
    
    // Validate password
    if (password.length < 8) {
        return res.status(400).send('Password too short');
    }
    if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
        return res.status(400).send('Password complexity insufficient');
    }
    
    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return res.status(400).send('Invalid email');
    }
    
    // Length checks
    if (username.length > 20 || password.length > 100 || email.length > 100) {
        return res.status(400).send('Input too long');
    }
    
    // Proceed with registration
    res.send('Registration successful');
});
```

```python
# Python/Flask - Server-side validation
from flask import Flask, request
import re

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    
    # Validate username
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return 'Invalid username', 400
    
    # Validate password
    if len(password) < 8:
        return 'Password too short', 400
    if not (re.search(r'[A-Z]', password) and 
            re.search(r'[a-z]', password) and 
            re.search(r'[0-9]', password)):
        return 'Password complexity insufficient', 400
    
    # Validate email
    email_regex = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    if not re.match(email_regex, email):
        return 'Invalid email', 400
    
    # Length checks
    if len(username) > 20 or len(password) > 100 or len(email) > 100:
        return 'Input too long', 400
    
    # Proceed with registration
    return 'Registration successful', 200
```

### 1.3.3 Defense in Depth Approach

**Best Practice: BOTH Client and Server-Side**

```html
<!-- Client-side for UX -->
<form action="/register" method="POST" onsubmit="return clientValidate()">
    <input type="text" id="username" required pattern="[a-zA-Z0-9_]{3,20}">
    <input type="email" id="email" required>
    <input type="password" id="password" required minlength="8">
    <input type="submit">
</form>

<script>
function clientValidate() {
    // Client-side validation for immediate feedback
    var username = document.getElementById('username').value;
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
    
    if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
        alert('Username must be 3-20 alphanumeric characters');
        return false;
    }
    
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Invalid email format');
        return false;
    }
    
    if (password.length < 8) {
        alert('Password must be at least 8 characters');
        return false;
    }
    
    return true;
}
</script>
```

```php
<!-- Server-side for security (SAME validation logic) -->
<?php
$username = $_POST['username'];
$email = $_POST['email'];
$password = $_POST['password'];

// ALWAYS validate on server, even if client validated
if (!preg_match('/^[a-zA-Z0-9_]{3,20}$/', $username)) {
    http_response_code(400);
    die(json_encode(['error' => 'Invalid username']));
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    die(json_encode(['error' => 'Invalid email']));
}

if (strlen($password) < 8) {
    http_response_code(400);
    die(json_encode(['error' => 'Password too short']));
}

// Proceed with registration
?>
```

---

## 1.4 VALIDATION EXAMPLES BY INPUT TYPE

### 1.4.1 Email Validation

```php
// PHP
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    die('Invalid email');
}

// Additional checks
if (strlen($email) > 254) { // RFC 5321
    die('Email too long');
}

// Check domain exists (optional)
list($user, $domain) = explode('@', $email);
if (!checkdnsrr($domain, 'MX')) {
    die('Invalid email domain');
}
```

```javascript
// JavaScript
const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

if (!emailRegex.test(email)) {
    return 'Invalid email';
}

if (email.length > 254) {
    return 'Email too long';
}
```

### 1.4.2 URL Validation

```php
// PHP
$url = $_GET['redirect'];

if (!filter_var($url, FILTER_VALIDATE_URL)) {
    die('Invalid URL');
}

// Additional checks - only allow specific domains (allowlist)
$parsed = parse_url($url);
$allowed_hosts = ['example.com', 'www.example.com', 'api.example.com'];

if (!in_array($parsed['host'], $allowed_hosts)) {
    die('URL not in allowed domains');
}

// Ensure HTTPS
if ($parsed['scheme'] !== 'https') {
    die('Only HTTPS URLs allowed');
}
```

```javascript
// JavaScript/Node.js
const url = require('url');

function validateURL(urlString) {
    try {
        const parsed = new URL(urlString);
        
        // Check scheme
        if (parsed.protocol !== 'https:') {
            return 'Only HTTPS allowed';
        }
        
        // Check allowed hosts
        const allowedHosts = ['example.com', 'www.example.com'];
        if (!allowedHosts.includes(parsed.hostname)) {
            return 'Domain not allowed';
        }
        
        return 'Valid';
    } catch (e) {
        return 'Invalid URL';
    }
}
```

### 1.4.3 Numeric Validation

```php
// PHP - Integer validation
$id = $_GET['id'];

if (!ctype_digit($id)) {
    die('ID must be numeric');
}

$id = (int)$id;

if ($id < 1 || $id > 1000000) {
    die('ID out of range');
}

// Float validation
$price = $_POST['price'];

if (!is_numeric($price)) {
    die('Price must be numeric');
}

$price = (float)$price;

if ($price < 0 || $price > 999999.99) {
    die('Invalid price');
}
```

```python
# Python
id_str = request.args.get('id')

try:
    id_num = int(id_str)
    if id_num < 1 or id_num > 1000000:
        return 'ID out of range', 400
except ValueError:
    return 'ID must be numeric', 400
```

### 1.4.4 Date Validation

```php
// PHP
$date = $_POST['date'];

// Validate format
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
    die('Invalid date format (YYYY-MM-DD)');
}

// Validate it's a real date
$parts = explode('-', $date);
if (!checkdate($parts[1], $parts[2], $parts[0])) {
    die('Invalid date');
}

// Using DateTime
try {
    $dt = new DateTime($date);
    
    // Additional checks
    $now = new DateTime();
    if ($dt > $now) {
        die('Date cannot be in the future');
    }
} catch (Exception $e) {
    die('Invalid date');
}
```

```javascript
// JavaScript
const dateRegex = /^\d{4}-\d{2}-\d{2}$/;

if (!dateRegex.test(dateStr)) {
    return 'Invalid date format';
}

const date = new Date(dateStr);

if (isNaN(date.getTime())) {
    return 'Invalid date';
}

// Check not in future
if (date > new Date()) {
    return 'Date cannot be in future';
}
```

### 1.4.5 Phone Number Validation

```php
// PHP - International phone number
$phone = $_POST['phone'];

// Remove all non-digits
$phone_clean = preg_replace('/[^0-9]/', '', $phone);

// Validate length (10-15 digits)
if (strlen($phone_clean) < 10 || strlen($phone_clean) > 15) {
    die('Invalid phone number');
}

// Validate format (optional)
if (!preg_match('/^\+?[1-9]\d{1,14}$/', $phone)) {
    die('Invalid phone format');
}
```

```python
# Python - using phonenumbers library
import phonenumbers

try:
    phone_obj = phonenumbers.parse(phone, "US")
    if not phonenumbers.is_valid_number(phone_obj):
        return 'Invalid phone number', 400
except phonenumbers.NumberParseException:
    return 'Invalid phone format', 400
```

---

## 1.5 CONTEXT-SPECIFIC VALIDATION

### 1.5.1 File Upload Validation

```php
// PHP - File upload validation
$file = $_FILES['upload'];

// Check file was uploaded
if ($file['error'] !== UPLOAD_ERR_OK) {
    die('Upload error');
}

// Validate file size (5MB max)
if ($file['size'] > 5 * 1024 * 1024) {
    die('File too large');
}

// Validate file extension (allowlist)
$allowed_ext = ['jpg', 'jpeg', 'png', 'gif', 'pdf'];
$ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));

if (!in_array($ext, $allowed_ext)) {
    die('Invalid file type');
}

// Validate MIME type (check actual file content)
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime = finfo_file($finfo, $file['tmp_name']);
finfo_close($finfo);

$allowed_mime = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf'
];

if (!in_array($mime, $allowed_mime)) {
    die('Invalid file content');
}

// Validate it's actually an image (for images)
if (in_array($mime, ['image/jpeg', 'image/png', 'image/gif'])) {
    $img = getimagesize($file['tmp_name']);
    if ($img === false) {
        die('File is not a valid image');
    }
}

// Generate safe filename
$safe_name = bin2hex(random_bytes(16)) . '.' . $ext;
```

### 1.5.2 SQL Query Parameter Validation

```php
// PHP - Even with prepared statements, validate input

// Validate table name (cannot be parameterized)
$table = $_GET['table'];
$allowed_tables = ['users', 'products', 'orders'];

if (!in_array($table, $allowed_tables)) {
    die('Invalid table');
}

// Validate column name (cannot be parameterized)
$column = $_GET['sort'];
$allowed_columns = ['id', 'name', 'created_at', 'price'];

if (!in_array($column, $allowed_columns)) {
    die('Invalid column');
}

// Validate order direction
$order = $_GET['order'];
if ($order !== 'ASC' && $order !== 'DESC') {
    $order = 'ASC'; // Default
}

// Build query safely
$stmt = $pdo->prepare("SELECT * FROM $table ORDER BY $column $order");
$stmt->execute();
```

### 1.5.3 JSON Input Validation

```javascript
// Node.js/Express - JSON validation
app.post('/api/user', express.json(), (req, res) => {
    // Validate JSON structure
    if (typeof req.body !== 'object' || req.body === null) {
        return res.status(400).send('Invalid JSON');
    }
    
    // Validate required fields
    const required = ['username', 'email', 'password'];
    for (const field of required) {
        if (!(field in req.body)) {
            return res.status(400).send(`Missing field: ${field}`);
        }
    }
    
    // Validate data types
    if (typeof req.body.username !== 'string') {
        return res.status(400).send('Username must be string');
    }
    
    // Validate no extra fields (prevent mass assignment)
    const allowed_fields = ['username', 'email', 'password', 'age'];
    for (const key in req.body) {
        if (!allowed_fields.includes(key)) {
            return res.status(400).send(`Unexpected field: ${key}`);
        }
    }
    
    // Validate individual fields
    // ... (username, email, password validation as shown earlier)
});
```

---
