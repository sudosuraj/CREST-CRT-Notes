# Cross-Site Request Forgery

## 1. Idenfity a CSRF Canditate

- Is there a state-changing action?
    - Change email/password
    - Update Profile
    - Transfer Funds
    - Modify Permissions

- Is the user authenticated via cookies/browser credentials?

## 2. Initial surface checks (fast wins)

- Does every form / request include a CSRF token?
- Does the action accept GET instead of POST?
- Can parameters be sent in the URL instead of body?

If no token or `GET` allowed -> CSRF is likely.

## 3. Token presence & enforcement

- Submit request without token
- Submit with token parameter present but empty (`csrf=`)
- Submit with random token

If any succeed -> CSRF.

## 4. Token binding & reuse

- Token binding & reuse
- Use a token from a different session / user
- Use a token of the same length / format

If accepted -> token not session-bound -> CSRF.


## 5. Token quality checks

- Token static across requests?
- Token predictable?
- Token equals known value (user ID, email, timestamp)?


If yes → CSRF.

## 6. Cookie relationships

- Is the CSRF token tied to:
    - the session cookie? (good)
    - a different cookie (weak)
- Can you set / influence that cookie?

If yes -> possible bypass.

## 7. SameSite & method abuse

- Session cookie has SameSite?
    - None / missing -> Weak
    - Lax - GET-based CSRF possible
- Can request be submitted as:
    - GET
    - top-level navigation
    - image / redirect


## 8. HTTP Method Overrides

- `X-Http-Method-Override: GET`
- `_method=GET` or `_method=POST`

If server accepts override -> bypass is possible.

## 9. Referer / Origin validation

- Is Referer checked? 
- Does request succeed if:
    - Referer missing?
    - Referer manipulated?

If yes -> bypassable CSRF.

## 10. Bonus (only if relevant)
- Can token be stolen via XSS?
- Are there on-site gadgets (redirects, DOM nav)? 
- Are there sibling domains under same site?


