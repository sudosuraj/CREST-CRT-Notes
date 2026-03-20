# Open Redirect

## Why It Matters

Open redirect issues are often low-value by themselves, but they become important when chained into:

- phishing
- OAuth abuse
- password reset poisoning
- CSP or redirect-based trust bypass
- SSRF-style backend fetch behavior

The severity depends on where the redirect sits in the workflow.

## Recognition Cues

Look for parameters such as:

```text
url=
next=
redirect=
redirect_uri=
return=
continue=
target=
destination=
```

Typical examples:

```text
/login?next=/dashboard
/redirect?url=https://example.com
/oauth?redirect_uri=https://example.com
```

## Workflow

1. identify the redirect parameter or header-controlled location
2. test direct external URLs
3. try parser and validation bypasses
4. determine whether the issue is standalone or part of OAuth, reset, or trust logic
5. report the realistic chainable impact

## Step 1: Direct External Redirect Test

```text
https://target.com/redirect?url=https://evil.com
```

If the server returns:

```text
Location: https://evil.com
```

the issue is confirmed.

## Step 2: Common Bypass Forms

If plain external URLs are blocked, try:

```text
//evil.com
///evil.com
https://target.com@evil.com
https://target.com.evil.com
https:%2f%2fevil.com
https:%252f%252fevil.com
\\evil.com
https:\\evil.com
```

These test whether validation is based on naive string checks instead of real URL parsing.

## Step 3: Relative And Mixed-Slash Variants

Sometimes filters only block obvious full URLs:

```text
/\evil.com
/\/evil.com
https:/\evil.com
```

These are useful when the application tries to normalize paths incorrectly.

## Step 4: Special Chaining Contexts

### OAuth

High-value target:

```text
/oauth?redirect_uri=
```

If redirect validation is weak, authorization codes or tokens may be exposed to an attacker-controlled domain.

### Password Reset

If reset links or completion steps honor attacker-controlled redirect targets or host values, open redirect may contribute to account takeover workflows.

### SSRF-Like Fetch Behavior

If the backend follows or previews the redirect server-side, the issue may become SSRF rather than just a client redirect.

## Protocol Abuse

Test carefully when appropriate:

```text
javascript:alert(1)
data:text/html,<script>alert(1)</script>
```

These matter only if the redirect sink or downstream browser behavior makes them relevant.

## Pitfalls

- reporting every external redirect as high severity without chainable context
- missing OAuth and reset flows where the impact is much stronger
- confusing client-side navigation with server-side redirect handling
- stopping after `https://evil.com` without testing parser bypasses

## Reporting Notes

Capture:

- the vulnerable parameter or flow
- the redirect response
- whether validation was missing or bypassable
- the realistic impact chain, such as phishing or OAuth abuse

## Fast Checklist

```text
1. Find a redirect parameter
2. Test direct external URL
3. Try parser bypass variants
4. Check OAuth, reset, and trust-sensitive flows
5. Report the real chainable impact
```
