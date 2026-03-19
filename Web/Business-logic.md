# Business Logic Vulnerabilities

Business Logic flaws occur when an application’s workflow or rules can be manipulated in unintended ways to gain financial, access, or data advantage.

These are NOT technical injection bugs — they exploit flawed assumptions in application design.

# 1. Quick Testing Checklist 

1. Understand normal workflow (happy path)
2. Identify assumptions:
   - Price
   - Quantity
   - Role
   - Status
   - Step order
3. Capture legitimate request
4. Modify:
   - Values
   - Order of requests
   - Sequence
   - State
   - Quantity
   - Price
5. Look for:
   - Free items
   - Duplicate discounts
   - Skipped validation
   - Reused tokens
   - State manipulation
   - Negative balances

# 2. Common Business Logic Categories

## A. Price Manipulation

Look for:

```
price=
amount=
total=
cost=
```

Test:

```
price=1
price=0
price=-1
price=0.01
price=999999
```

If client sends price → always try modifying.

---

## B. Quantity Abuse

```
quantity=1000
quantity=0
quantity=-1
quantity=999999
```

Test:

- Negative quantities
- Zero quantity
- Large quantity overflow

---

## C. Discount / Coupon Abuse

Test:

```
coupon=DISCOUNT50
coupon=DISCOUNT60
coupon=DISCOUNT90
```

Try:
- Applying same coupon multiple times
- Removing coupon after discount applied
- Changing coupon after total calculated
- Stacking multiple coupons

## D. Step Skipping (Workflow Bypass)

If flow is:

1. Add item
2. Review
3. Confirm
4. Pay

Try directly calling:

```
POST /confirm
POST /complete
POST /approve
```

Without completing earlier steps.

## E. Parameter Tampering

Look for hidden params:

```
isPremium=true
isVerified=true
isAdmin=true
approved=true
status=approved
role=admin
```

Try flipping values.

## F. Role / Tier Upgrade Abuse

Try modifying:

```
accountType=premium
plan=enterprise
membership=gold
```

## G. Multi-Step Token Reuse

If a token is issued in step 1:

- Reuse token
- Replay token
- Use token with modified data
- Use expired token

## H. Race Conditions

Used when:
- Limited inventory
- Balance transfers
- Coupon use
- One-time actions

### Burp Turbo Intruder / Repeater trick:

Send 10–50 identical requests simultaneously.

Goal:
- Double-spend
- Bypass single-use restriction
- Redeem coupon multiple times

## I. Balance Manipulation

Look for:

```
balance=
credit=
wallet=
points=
```

Test:

- Negative transfers
- Self-transfer
- Large transfer
- Decimal abuse


## J. State Manipulation

Look for:

```
status=pending
status=approved
status=completed
```

Try:

```
status=approved
```

Even if app normally sets it.


# 3. Numeric Edge Case Testing

Test edge values:

```
0
-1
-9999
999999999
0.0001
NaN
null
```

# 4. ID Sequencing Abuse

If order IDs are sequential:

```
orderId=1001 → 1002 → 1003
```

Try:
- Accessing other orders
- Modifying others' orders
- Cancelling others' orders

(Combines with IDOR)

# 5. Timing-Based Logic Flaws

If app enforces:
- “1 request per day”
- “1 redemption per account”

Try:
- Multiple requests in parallel
- Rapid submission
- Using two sessions simultaneously

# 6. Refund / Return Abuse

Test:

- Refund without payment
- Refund twice
- Partial refund → full refund
- Refund negative value

# 7. Cart Manipulation Flow

1. Add expensive item
2. Intercept request
3. Modify:

```
price=1
total=1
```

4. Forward

If server trusts client total → critical flaw.

---

# 8. Burp Workflow Strategy

1. Record full purchase flow
2. Repeater:
   - Change price
   - Change quantity
   - Change coupon
   - Remove required param
3. Compare responses
4. Test multi-send
5. Observe:
   - Order confirmation
   - Payment bypass
   - Status changes

# 9. Quick Copy-Paste Paylaod List

```
price=0
price=1
price=-1
price=0.01

quantity=0
quantity=-1
quantity=9999

coupon=DISCOUNT50
coupon=FREE
coupon=

isAdmin=true
isPremium=true
role=admin
status=approved
approved=true

balance=999999
balance=-100

total=1
amount=1
cost=0
```