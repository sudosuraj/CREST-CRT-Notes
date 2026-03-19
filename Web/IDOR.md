# Insecure Direct Object Reference (IDOR)

## Detection

### Identify IDOR candidates

### Search for parameters that reference objects:
```
?user_id=
?invoice=
?file=
?id=
```

Look for:
- Sequential IDs
- Predictable identifiers
- GUIDs that map to records

## Manual Testing
### HTTP GET tampering

1. Capture request with ID parameter (authenticated)
2. Change the object reference in the URL or API request
3. Send modified request
4. Check whether unauthorized data is returned

#### Example:
```
GET /profile?user_id=123
```
Try:
```
GET /profile?user_id=124
GET /profile?user_id=125
```


## Tools / Workflow

### Burp Suite (Intruder – Sniper)

1. Identify relevant parameter
2. Send to Intruder
3. Set payload position for object ID
4. Payloads:
   - Sequential numbers
   - Known valid IDs
   - Wordlist of IDs
5. Analyze responses (status codes, content length)
6. Look for successful unauthorized access samples

### Example Payload Setup (Burp)
```
Positions: id=§123§
Payload set:
   Numbers (start: 1, end: 10000, step: 1)
```

Filter responses:
- 200 OK with valid data = possible IDOR
- Differences in response size/content indicate differing access


## API Testing (JSON / REST)

Attack vectors:
```
GET /api/orders/123
```
Try:
```
GET /api/orders/124
```

Modify:
- Path parameters
- JSON body identifiers
- Authorization header values

---

## POST / PUT Manipulation

Example:
```
POST /updateInvoice
{
  "invoiceId": 1234,
  "fields": {...}
}
```

Try:
```
{
  "invoiceId": 1235,
  "fields": {...}
}
```

---

## Common IDOR Scenarios

- Horizontal access: user → other user’s data
- Vertical access: user → admin/resource escalation
- File access: download others' files
- Function access: access restricted actions via modified IDs

---

## Indicator Patterns

Susceptible when:
- Business logic relies only on user ID in request
- No server-side authorization check
- ID pattern predictable
- HTTP status 200 for unauthorized IDs
- Content returned matches another user’s data

---

## Response Validation Tips

Check:
- Status codes (200 OK for modified ID)
- Body content differences
- JSON fields belong to other users
- Length of response (longer/shorter than expected)

---

## Bypasses

- Sequential OR brute-forced IDs
- Encoded IDs: Base64 / URL encoding
  - Decode identifiers
  - Modify and re-encode
- Cookies / JWT claims manipulation (object ID in token)

---

## Evidence Collection

Record:
- Original request & response
- Modified request with ID change
- Unauthorized access proof
- Screenshot of request/response
- Relevant headers

---

## Mitigation (Report Wording)

- Always enforce **server-side access control** for object references  
- Verify that the authenticated user is authorized for the requested object  
- Avoid exposing internal IDs directly
- Use **indirect references** (opaque, unpredictable tokens)  
- Apply **deny-by-default** access checks  
- Check permissions on each request (not just authentication) :contentReference[oaicite:6]{index=6}

---

## Quick Copy/Paste Commands / Snippets

### Burp Intruder setup
```
Send to Intruder → Sniper
Position: id=§123§
Payloads: Numbers (start 1, end 5000)
```

### Encode / Decode IDs
```
echo -n "123" | base64
echo "MTIz" | base64 -d
```