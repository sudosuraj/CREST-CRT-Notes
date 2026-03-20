# Insecure Direct Object Reference (IDOR)

## Why It Matters

IDOR is one of the most direct ways to prove broken authorization. The application exposes an object reference, and the server does not properly verify that the requester should access it.

Typical impacts:

- reading another user's data
- modifying another user's objects
- downloading other users' files
- deleting or approving records you do not own

## Recognition Cues

Look for:

- `id=`
- `user_id=`
- `invoice=`
- `file=`
- object IDs in JSON bodies
- path parameters such as `/orders/123`

High-signal signs:

- sequential IDs
- predictable UUID disclosure
- identifiers returned by list APIs and reused in direct fetch APIs

## Workflow

1. find an object reference
2. capture a legitimate request
3. modify the identifier
4. compare the response as the same user and another user
5. determine whether the impact is read, write, delete, or admin action

## Step 1: Identify Candidates

Examples:

```text
GET /profile?user_id=123
GET /api/orders/123
POST /updateInvoice {"invoiceId":1234}
```

Good targets:

- profiles
- invoices
- orders
- files
- reports
- support tickets

## Step 2: Manual Tampering

Change the reference:

```text
123 -> 124
1001 -> 1002
```

Then compare:

- status code
- response length
- returned user-specific fields

## Step 3: Multi-User Validation

If possible, use two accounts:

- user A owns object A
- user B owns object B

Test:

- user A requesting object B
- user B requesting object A

This gives cleaner evidence than random enumeration.

## API Patterns

IDOR often appears in:

- REST path parameters
- JSON body fields
- GraphQL object lookups
- download endpoints
- bulk export actions

Do not limit testing to query-string parameters.

## Encoded And Indirect References

If identifiers appear encoded:

- base64 decode
- URL decode
- re-encode after modification

Opaque references do not fix authorization if the server still fails to enforce ownership.

## Automation

Use Burp or similar tooling when the space is large, but validate manually first.

Typical automation target:

- a single numeric or UUID parameter
- response differences that indicate success

## Where It Overlaps

IDOR is often one instance of a larger access control problem, especially in:

- multi-tenant apps
- download features
- business workflows
- admin actions

## Pitfalls

- treating sequential IDs alone as a vulnerability
- stopping after a 200 response without confirming the data belongs to another user
- missing write or delete operations because only `GET` requests were tested
- ignoring identifiers in JSON, headers, or hidden fields

## Reporting Notes

Capture:

- the vulnerable object reference
- the legitimate request
- the unauthorized modified request
- whose data or object was accessed
- whether the impact was read, write, delete, or workflow action

## Fast Checklist

```text
1. Find object references
2. Capture a valid request
3. Modify the ID
4. Compare response and ownership
5. Test read and write paths
6. Save the authorized and unauthorized pair
```
