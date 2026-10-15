# 07 — Resource Consumption and Business Flows (API4, API6:2023 · A06:2025)

## Definition

A caller can exhaust resources or automate a business flow beyond its intended use.

## Signals

| Signal                          | Probe                                                                                              |
| ------------------------------- | -------------------------------------------------------------------------------------------------- |
| No rate limit                   | Login, OTP, reset, signup, search, expensive exports without per-user/IP limits                    |
| Unbounded pagination            | `limit` from query without max; missing default limit; `find()` without limit on large collections |
| Body/upload size                | `express.json()` without `limit` override where large bodies matter; uploads without size cap      |
| Expensive operations            | Regex/sort/aggregation on user input, N+1 fan-out, batch endpoints with unbounded array length     |
| GraphQL depth/complexity        | No depth/complexity limit, batching/aliases unrestricted                                           |
| Business flow abuse (API6; A06) | Coupons/referrals/trials reusable; no idempotency key on payments; replayable signed requests      |
| Race on balances/stock          | Check-then-write without atomic update or transaction (double spend)                               |
| Third-party cost                | SMS/email/LLM calls triggerable without limit (cost amplification)                                 |

## Test to Confirm

In-process: send N+1 requests and assert a 429; request `limit=100000` and assert it is capped; redeem the same coupon twice and assert the second is rejected; fire concurrent requests with `Promise.all` against the in-memory DB and assert balance invariants. Stub external providers and count calls.

## False-Positive Traps

- Rate limiting at the gateway present in the repo's infra code (otherwise Unconfirmed, not discarded).
- Pagination capped by a shared helper or schema validation.
- Idempotency enforced by a unique index.
