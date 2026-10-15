# 04 — Injection and Unsafe Input (API7, API8:2023 · A05, A01, A08:2025)

## Definition

Request data reaches an interpreter, file system, outbound request, or object graph without being constrained.

## Signals

| Signal                       | Probe                                                                                                       |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| NoSQL operator injection     | `find({ email: req.body.email })` where the value can be `{ "$ne": null }`; `$where`, `$regex` from user    |
| SQL injection                | String-concatenated SQL, `raw()`/`query()` with template literals, ORDER BY/column names from input         |
| Command injection            | `exec`/`spawn` with `shell: true` and user data                                                             |
| Path traversal               | `path.join(base, req.params.file)` without resolve-and-prefix check; `res.sendFile` with user paths         |
| SSRF (API7; A01:2025)        | Server fetches a user URL (webhooks, avatars, previews) without allowlist; redirects followed; internal IPs |
| Prototype pollution          | Deep merge/`lodash.merge`/`set` of user objects; `__proto__`/`constructor` keys accepted                    |
| ReDoS                        | User input against nested-quantifier regexes, or user-supplied regex                                        |
| Unsafe deserialization (A08) | `eval`, `new Function`, `vm`, YAML/XML parsers with unsafe options (XXE)                                    |
| Log injection (A09)          | User input written to logs unencoded (CRLF, forged entries) (CWE-117)                                       |
| File upload                  | No size/type limits, content-type trusted, files served from upload dir with original name                  |
| Template / header            | User data in server templates (SSTI) or in response headers (CRLF, open redirect via `Location`)            |

## Test to Confirm

Send the hostile payload in-process and assert on the effect: extra records returned, file outside base read, stubbed HTTP client called with an internal URL, polluted `({}).polluted`, regex time over a threshold. Never execute payloads that touch the real host (no `rm`, no real network).

## False-Positive Traps

- Schema validation (Joi/Zod/class-validator) casts the input to a primitive before the query.
- `mongoose.set('sanitizeFilter', true)` or `express-mongo-sanitize` in the chain.
- Parameterized queries / query builder escaping identifiers.
