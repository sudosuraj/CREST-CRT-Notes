# Business Logic Vulnerabilities

## Why It Matters

Business logic flaws are not parser bugs. They are workflow failures where the application trusts assumptions that a tester can break. These issues can lead to:

- free purchases
- duplicate redemptions
- unauthorized refunds
- negative balances
- tier or role abuse
- workflow bypass

The key skill is understanding the intended process first, then testing where the process can be manipulated.

## Recognition Cues

Look for flows involving:

- carts, pricing, discounts, and checkout
- loyalty points, wallets, and balances
- approval and refund workflows
- subscriptions and plan upgrades
- one-time actions such as coupon redemption

## Workflow

1. understand the normal happy path
2. identify the assumptions the workflow relies on
3. capture the legitimate requests
4. tamper with values, order, timing, and state
5. prove business impact, not just parameter acceptance

## Step 1: Map The Happy Path

Before modifying anything, understand:

- the normal step order
- which data the client sends
- which values the server recalculates
- which actions are meant to be one-time or role-limited

## Step 2: Identify Trust Boundaries

High-signal parameters include:

```text
price=
amount=
total=
cost=
quantity=
coupon=
balance=
credit=
status=
role=
plan=
```

The question is whether the server trusts the client too much.

## Common Test Areas

### Price Manipulation

Try:

```text
price=1
price=0
price=-1
price=0.01
```

If the server accepts client-supplied pricing, the finding is usually high impact.

### Quantity Abuse

Try:

```text
quantity=0
quantity=-1
quantity=999999
```

Check for:

- negative quantity logic
- integer edge cases
- free or credit-generating orders

### Discount And Coupon Abuse

Test:

- applying the same coupon twice
- stacking multiple coupons
- removing the coupon after the discounted total is set
- changing the coupon after calculation

### Workflow Bypass

If the flow is:

1. add item
2. review
3. confirm
4. pay

Try calling the later endpoints directly:

```text
POST /confirm
POST /complete
POST /approve
```

### State Manipulation

Look for:

```text
status=approved
status=completed
approved=true
isPremium=true
role=admin
```

If the client can directly control state or privilege markers, that is usually more than just a UI flaw.

### Race Conditions

Important for:

- coupon use
- limited inventory
- balance transfers
- one-time actions

Send multiple requests at once and check whether single-use assumptions break.

## Numeric Edge Cases

Useful values:

```text
0
-1
-9999
999999999
0.0001
null
```

You are looking for miscalculations, overflow, underflow, or incorrect validation branches.

## Where It Often Overlaps

Business logic issues often combine with:

- IDOR
- access control flaws
- race conditions
- weak server-side validation

## Pitfalls

- testing values without first understanding the intended workflow
- reporting parameter tampering without proving real business impact
- missing multi-step state changes because only one request was altered
- forgetting to test concurrency on single-use actions

## Reporting Notes

Capture:

- the normal workflow
- the assumption that was broken
- the modified request sequence
- the financial, access, or process impact
- whether the flaw was repeatable

## Fast Checklist

```text
1. Map the happy path
2. Identify trusted client values
3. Tamper with price, quantity, state, and sequence
4. Test replay and concurrency
5. Prove financial or process impact
6. Save the exact request chain
```
