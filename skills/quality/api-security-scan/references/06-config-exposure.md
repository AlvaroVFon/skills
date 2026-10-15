# 06 — Security Configuration and Integrity (API8, API9, API10:2023 · A02, A04, A08, A09:2025)

## Definition

The API's defaults, transport, secrets, and integrations weaken every endpoint at once.

## Signals

| Signal                       | Probe                                                                                                     |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| CORS                         | `origin: '*'` or reflected `Origin` with `credentials: true`; regex allowlists that match `evil-site.com` |
| Security headers             | No `helmet` or equivalent: HSTS, `X-Content-Type-Options`, `frame-ancestors`, CSP on HTML responses       |
| Cookies                      | Session cookies without `HttpOnly`, `Secure`, `SameSite`; CSRF protection missing on cookie auth          |
| Hardcoded secrets (A04)      | Keys, passwords, JWT secrets, connection strings in source or committed config (CWE-321, CWE-798)         |
| Transport (A04)              | HTTP allowed, no HSTS, TLS verification off in outbound clients (`rejectUnauthorized: false`) (CWE-319)   |
| Integrity (A08)              | Webhooks/callbacks without signature check; client-sent prices/roles trusted without server verification  |
| Security event logging (A09) | Failed logins, authz denials, high-value actions not logged (CWE-778, CWE-223); report as Low             |
| Insecure defaults            | Debug flags on, `trust proxy` misconfigured (spoofable IP for rate limits), TLS verification disabled     |
| HTTP methods                 | `TRACE`/unexpected methods enabled; `app.all` handlers                                                    |
| Inventory (API9)             | Old versions (`/v1`) still mounted without the fixes of `/v2`; undocumented/internal routes exposed       |
| Unsafe consumption (API10)   | Third-party responses trusted without validation; redirects followed                                      |

## Test to Confirm

In-process: send a preflight with `Origin: https://evil.example` and assert it is not reflected with credentials; assert headers/cookie flags on a real response; call the legacy route and show the missing control; post a webhook with no/invalid signature and assert 401. Hardcoded secrets are proven by `file:line` alone (evidence type `manual`, value redacted).

## False-Positive Traps

- Headers/CORS set by a reverse proxy config that is in the repo (check before reporting).
- Secrets in test fixtures that are clearly fake and unused outside tests.
- Wildcard CORS on a truly public, cookie-less, read-only API.
