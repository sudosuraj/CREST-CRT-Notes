# LDAP Injection

## Why It Matters

LDAP injection occurs when user input is inserted into an LDAP query without proper escaping. Depending on the context, this can lead to:

- login bypass
- broader directory search results
- disclosure of user or group data
- privilege logic bypass based on LDAP matches

## Recognition Cues

Look for:

- LDAP-backed login forms
- directory search features
- user lookup and auto-complete
- filters containing usernames, emails, or group names

Strong hints:

- the application is integrated with Active Directory or LDAP
- authentication or search behavior changes unexpectedly with special characters

## Workflow

1. identify where user input likely reaches an LDAP filter
2. determine whether the feature is authentication or search
3. test filter-breaking characters and wildcards
4. check whether results broaden or auth decisions change
5. prove impact with the smallest working payload

## Search Context Testing

Wildcards are the quickest probe:

```text
*
```

If a search field suddenly returns many results, escaping may be weak.

## Authentication Context Testing

Classic filter-manipulation probes:

```text
*)(uid=*))(|(uid=*
admin)(cn=*))%00
```

These matter only if the application directly concatenates input into an LDAP filter.

## What You Are Looking For

Signs of success:

- login accepted unexpectedly
- search returns all users
- filters behave differently with `*`, `)`, or injected clauses
- role or group checks are bypassed

## Common Risk Areas

- username search boxes
- login forms
- admin user lookup features
- group membership checks

## Pitfalls

- assuming every LDAP-backed app is injectable
- using login payloads against a search context without understanding the filter
- reporting special-character handling without proving altered server behavior

## Reporting Notes

Capture:

- the vulnerable input point
- whether the injection affected auth or search
- the payload class that worked
- the resulting data exposure or auth bypass

## Fast Checklist

```text
1. Identify LDAP-backed search or auth input
2. Test wildcard and filter-breaking characters
3. Compare normal vs injected behavior
4. Prove auth bypass or broadened result set
5. Save the request and changed response
```
