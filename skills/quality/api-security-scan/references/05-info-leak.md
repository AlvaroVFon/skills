# 05 — Information Leakage (API3, API8:2023 · A01, A09, A10:2025)

## Definition

The API reveals more than the caller needs: **internal implementation details** that help an attacker map and exploit the system, or **data** the caller is not entitled to see.

## Internal Implementation Details

| Signal                    | Probe                                                                                                                                          |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Stack traces in responses | Error handler returns `err.stack`/`err.message`; Express default handler active when `NODE_ENV` ≠ `production`                                 |
| Raw driver/ORM errors     | Mongo `E11000 duplicate key … index: email_1`, `CastError`, SQL errors with table/column names sent to client                                  |
| Query echo                | Response or error includes the filter/query/SQL built server-side                                                                              |
| Stack fingerprinting      | `X-Powered-By`, `Server`, framework/library version headers or `/version` route without auth                                                   |
| Internal topology         | Internal hostnames, IPs, file paths, bucket names, queue names in bodies, headers, or errors                                                   |
| Exposed tooling           | `/debug`, `/metrics`, `/actuator`, `/swagger`, `/graphql` introspection, `/health` with dependency details, unauthenticated or enabled in prod |
| Source maps / env         | `.map` files or `.env`/config served statically                                                                                                |
| Distinguishable responses | Login/reset/signup say "user not found" vs "wrong password"; 403 vs 404 on someone else's id (enumeration)                                     |
| Timing side channel       | Early return when the user does not exist vs hash compare when it does                                                                         |

## Improper Data Exposure

| Signal                       | Probe                                                                                                       |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Full object returned         | `res.json(user)` of a Mongoose doc/entity: `passwordHash`, `resetToken`, `mfaSecret`, `__v`, internal flags |
| No serializer / projection   | Missing `select('-password')`, `toJSON` transform, DTO/`ClassSerializerInterceptor`, `@Exclude`             |
| Over-wide `populate` / joins | Related documents populated in full (author email, phone, address of other users)                           |
| Lists and search             | Collection endpoints return other users' PII or fields the detail endpoint hides                            |
| Data in errors               | Validation error echoes the whole input (passwords, card numbers) or another user's record                  |
| Sensitive data in URLs       | Tokens, emails, ids of other users in query strings (logged by proxies, Referer)                            |
| Logs (A09)                   | Logger writes `req.body`, `req.headers.authorization`, tokens, passwords, PII                               |
| Caching                      | Private responses without `Cache-Control: no-store`; shared cache keys missing user                         |
| Enumerable ids               | Sequential/incremental ids on user-facing resources combined with weak authz (`03`)                         |

## CWE Hints

CWE-200 (exposure), CWE-201 (sent data), CWE-209 / CWE-550 (error message), CWE-215 (debug code), CWE-213 (intended-but-sensitive data), CWE-203 (observable discrepancy), CWE-208 (timing), CWE-532 (log), CWE-598 (query string), CWE-497 (system info).

## Test to Confirm

In-process, trigger the path (force an error with a malformed id or duplicate key, call the list endpoint as user A, hit the debug route anonymously) and assert the leaked field/header/string is **absent**. The test failing because it is present is the exploit. For logs, capture the logger (spy/stub transport) and assert on the written line. Redact real values in evidence; synthetic fixtures make this trivial.

## Severity Guidance

- Credentials, tokens, secrets, or other users' PII → **High** (Critical if unauthenticated and bulk).
- Own-user sensitive internals (hash, MFA secret) → **Medium–High**.
- Enumeration of users/emails → **Medium**.
- Versions, stack traces, `X-Powered-By` alone → **Low** unless they chain with a known issue.

## False-Positive Traps

- A global `toJSON`/serializer strips the field before the response (check schema options and interceptors).
- Detailed errors only when `NODE_ENV=development` and production config sets it — verify the prod config path.
- The field is intentionally public (username, avatar); document, do not report.
