# Broken Access Control

## Quick Testing Flow

1. **Map features per role** (Anon / User / Admin / Other roles)
2. **Get 2 accounts** (A and B) + note each user’s object IDs
3. **Capture a “good” request** for A (view/edit/delete/export/download)
4. Replay as:
   - **No auth** (remove cookies/token)
   - **Account B auth** (swap session)
   - **Same auth, changed object** (change IDs/UUIDs)
5. Try bypasses:
   - URL/endpoint guessing, method changes, param tampering, role headers/claims
6. Confirm impact:
   - **Read** other user data
   - **Modify** other user data
   - **Perform admin-only actions**
7. Capture evidence: request → response → impact


## Core Types You Must Test

### A. Horizontal privilege escalation (IDOR/BOLA)
User A accesses User B’s objects by changing identifiers.

Examples:
- `/api/users/123` → `/api/users/124`
- `/invoice?id=1001` → `1002`
- `/files/uuid` → another UUID

### B. Vertical privilege escalation
Normal user accesses admin-only functions (admin pages/endpoints, dangerous actions). 

### C. Function-level access control (BFLA)
User can invoke restricted actions even if UI hides them (buttons removed ≠ auth). 

### D. Unauthenticated access
Sensitive routes/actions exposed without login (missing checks).

### E. Parameter-based access control
Authorization enforced by **client-controlled params** (role=admin, isAdmin=true). 

## High-Signal Targets

### Web
- Admin panels, config pages, user management
- “Export”, “Download”, “Generate report”, “Billing”, “Refund”, “Invite”
- Hidden endpoints behind buttons/tabs
- Direct object fetch endpoints: `/download`, `/view`, `/print`

### API
- `/api/v1/users/{id}`
- `/api/orders/{id}`
- `/api/projects/{id}/reports/{rid}`
- bulk endpoints: `/search`, `/export`, `/list`
- GraphQL: `node(id:)`, `viewer`, direct object queries


## Practical Test Patterns

### A. Swap sessions (Account A → Account B)
- Login as A, capture request
- Replace Cookie/Authorization with B’s token
- Same object ID: should **deny**
- Then change object ID to B’s: should **allow** for B only

### B. Remove auth (Unauthenticated check)
- Remove `Cookie:` header
- Remove `Authorization:` header
- Remove CSRF token (if present) and see if still works

### C. Object ID fuzz (numbers + UUIDs + base64)
Test common formats:

**Numeric**
- `id=1` → `2`, `3`, `0`, `-1`, `99999`

**UUID**
- Replace with another known UUID (from B)
- Try uppercase/lowercase changes (sometimes naïve checks)

**Encoded**
- Base64 decode/encode if values look like it
- URL decode if values contain `%2f`, `%3d`

## Bypass Techniques (the stuff that actually wins exams)

### A. Forced browsing / endpoint guessing
Try direct access to “admin” routes:
- `/admin`
- `/admin/users`
- `/manage`
- `/settings`
- `/config`
- `/internal`
- `/debug`

Use a wordlist if needed:
- Common admin paths + your app’s nouns (users, invoices, reports)

### B. HTTP method tampering
If UI uses POST, try GET/PUT/PATCH/DELETE and vice versa.

Examples:
- `POST /api/users/123/delete` → `DELETE /api/users/123`
- `GET /download?id=100` → `POST /download` with body id=100

### C. Parameter tampering
Look for any “authz-like” params and flip them:

```
role=admin
isAdmin=true
admin=1
access=full
privileged=true
userType=staff
accountId=...
tenantId=...
orgId=...
projectId=...
```

Also try removing these params entirely (sometimes “missing” = default allow).

### D. Header-based access control bypass
Some apps trust headers (badly). Try adding:

```
X-Forwarded-For: 127.0.0.1
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Forwarded-Host: localhost
X-Host: localhost
```

(Only matters if the app is known to use them; still quick to test.)

### E. Multi-step / workflow bypass
If action is meant to require step 1 → step 2:
- Directly call step 2 endpoint with crafted params
- Replay “confirm” endpoints without completing prior steps

### F. Client-side “disabled” features
If a feature is disabled in UI (hidden button / greyed out):
- Find the endpoint in history and call it anyway

### G. Tenant boundary checks (multi-tenant)
Classic failure: `tenantId` not enforced server-side.
- Keep same session, change `tenantId/orgId/accountId`

## 6. Burp Workflow

1. Proxy → browse as Account A
2. **Logger/HTTP history**: mark key requests (view/edit/export/delete)
3. Send to Repeater:
   - Variant 1: no auth
   - Variant 2: Account B auth
   - Variant 3: change object IDs
4. Compare:
   - status codes (200 vs 403/401)
   - response length
   - sensitive fields present (email, address, tokens, card metadata)
5. If API: use Burp’s “Copy as cURL” for reproducible evidence

PortSwigger’s access control guidance aligns with replaying requests and systematically varying roles/IDs.

## 7. Evidence Checklist

Capture:
- The “legit” request as A (works)
- The unauthorized request:
  - as B, or unauthenticated, or with modified object ID
- The response showing:
  - data disclosure OR successful modification OR restricted action performed
- Clear impact statement (what attacker gains)