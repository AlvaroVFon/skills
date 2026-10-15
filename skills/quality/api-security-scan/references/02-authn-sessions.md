# 02 — Authentication, Sessions, and Crypto (API2:2023 · A07, A04:2025)

## Definition

The API accepts a caller as authenticated when it should not: missing checks, forgeable tokens, weak credential flows.

## Signals

| Signal                      | Probe                                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------- |
| Route without auth          | Sensitive route registered before/outside the auth middleware, or guard missing on one handler           |
| JWT not verified            | `jwt.decode` instead of `jwt.verify`; `algorithms` not pinned (`none`, HS/RS confusion)                  |
| Weak JWT claims             | No `exp`, huge TTL, `aud`/`iss` unchecked, secret hardcoded or default (`secret`, `changeme`)            |
| Token transport             | Token in query string, logged, or in a non-`HttpOnly`/non-`Secure` cookie                                |
| Session fixation/revocation | Session id not rotated on login; logout or password change does not invalidate tokens                    |
| Password reset              | Predictable/long-lived reset tokens, token not single-use, not bound to the user                         |
| Brute force                 | Login/OTP/reset without rate limit or lockout (see `07`)                                                 |
| Credential storage (A04)    | Plain/MD5/SHA1/unsalted passwords instead of bcrypt/Argon2/scrypt (CWE-916, CWE-759)                     |
| Weak randomness (A04)       | Tokens, reset codes, session ids from `Math.random`/timestamps instead of `crypto.randomBytes` (CWE-338) |
| Secret comparison           | Tokens/API keys/HMACs compared with `===` instead of `timingSafeEqual` (CWE-208)                         |
| API keys                    | Key accepted from any header/query, not scoped, compared non-constant-time                               |

## Test to Confirm

Build the app in-process; call the route with no token, an expired token, a `none`-alg token, or a token signed with the default secret; assert 401. A 2xx response is the exploit.

## False-Positive Traps

- Auth applied by a router-level `use` or a global guard (`APP_GUARD`) higher up the chain.
- The route is public by design (document it in the inventory, not as a finding).
- Verification happens in a gateway present in the repo's infrastructure code.
