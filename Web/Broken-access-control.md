# Broken Access Control

## Why It Matters

Broken access control is one of the most common and most important web finding classes. The issue is not that a user is authenticated. The issue is that the server fails to enforce who should be allowed to do what.

Typical impacts:

- reading another user's data
- modifying another user's data
- accessing admin-only functions
- crossing tenant boundaries
- performing actions without authentication

## Recognition Cues

Look for:

- object IDs in URLs, bodies, or API paths
- admin endpoints hidden only by the UI
- export, refund, download, billing, or user-management functions
- multi-tenant identifiers such as `orgId`, `tenantId`, or `accountId`

## Workflow

1. map features by role
2. obtain at least two test users if possible
3. capture a legitimate request
4. replay it as another user, unauthenticated, and with modified identifiers
5. check for function-level and role-level bypasses

## Core Test Types

### Horizontal Access Control

User A should not read or modify User B's data.

Examples:

```text
/api/users/123
/invoice?id=1001
/files/<uuid>
```

### Vertical Access Control

A normal user should not reach admin functions or restricted actions.

Common targets:

- `/admin`
- `/manage`
- `/settings`
- `/config`
- internal-only APIs

### Function-Level Access Control

If the UI hides a feature but the endpoint still works, the server-side control is weak.

### Unauthenticated Access

Remove cookies or authorization headers and re-test sensitive requests.

## Practical Test Patterns

### Session Swap

1. capture a request as user A
2. replay with user B's session
3. keep the same object ID
4. then modify the object ID again

This distinguishes between:

- ownership checks
- role checks
- complete lack of checks

### Identifier Tampering

Test:

- sequential numeric IDs
- known UUIDs
- encoded or base64-style identifiers

### Method And Endpoint Tampering

Try:

- `GET` vs `POST`
- `DELETE` vs a hidden action endpoint
- direct access to admin routes

### Parameter Tampering

Look for:

```text
role=admin
isAdmin=true
access=full
tenantId=
orgId=
projectId=
```

### Header Abuse

Some apps trust proxy-style headers incorrectly:

```text
X-Forwarded-For: 127.0.0.1
X-Original-URL: /admin
X-Rewrite-URL: /admin
```

These are fast checks, not guaranteed wins.

## High-Signal Targets

### Web

- admin pages
- billing or refund features
- report export
- download endpoints
- hidden tabs and workflows

### APIs

- `/api/v1/users/{id}`
- `/api/orders/{id}`
- `/api/projects/{id}`
- GraphQL object and node lookups

## Where It Overlaps

Access control failures often overlap with:

- IDOR
- business logic flaws
- CSRF on privileged actions
- multi-tenant isolation failures

## Pitfalls

- relying on UI role changes instead of replaying raw requests
- treating authentication as authorization
- stopping after a read-only access violation and missing write impact
- missing tenant boundary issues because IDs looked non-sequential

## Reporting Notes

Capture:

- the intended role or ownership boundary
- the legitimate request
- the unauthorized variant
- whether the impact was read, write, delete, or admin action
- whether the issue affected one object, many objects, or tenant-wide access

## Fast Checklist

```text
1. Map features by role
2. Capture a valid request
3. Replay as another user and without auth
4. Tamper with IDs, methods, and admin paths
5. Prove read, write, or admin impact
6. Save both the allowed and unauthorized request pair
```
