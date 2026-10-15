# 10 — Severity

Rate **impact × exploitability**. Start from impact, then move one level down if exploitation needs a privileged account or user interaction, and one level up if it is unauthenticated and scriptable at scale.

| Severity | Impact                                                                                     | Typical examples                                                        |
| -------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| Critical | Full account/tenant takeover, auth bypass, RCE, bulk data of all users, money movement     | JWT `none` accepted, NoSQL login bypass, unauthenticated BOLA on PII    |
| High     | Read/modify other users' data, privilege escalation, credential or token leak              | BOLA with any account, mass assignment of `role`, tokens in logs        |
| Medium   | Limited data exposure, enumeration, abuse without direct loss, missing rate limit on login | User enumeration, unbounded pagination, CORS misconfig needing a victim |
| Low      | Fingerprinting and hardening gaps with no demonstrated chain                               | `X-Powered-By`, missing HSTS, verbose 500 without data                  |

## Classification

Every finding carries two OWASP tags plus an optional CWE:

- `owasp_api` — **OWASP API Security Top 10 (2023)**, the current API-specific edition (no newer API edition exists).
- `owasp_top10` — **OWASP Top 10:2025**, the current general web application list.

Set each to the best match or `null` when none fits; at least one should be set (W16 otherwise). Add `cwe` when it is clear.

### OWASP API Security Top 10 (2023)

| Id         | Name                                            | Reference  |
| ---------- | ----------------------------------------------- | ---------- |
| API1:2023  | Broken Object Level Authorization               | `03`       |
| API2:2023  | Broken Authentication                           | `02`       |
| API3:2023  | Broken Object Property Level Authorization      | `03`, `05` |
| API4:2023  | Unrestricted Resource Consumption               | `07`       |
| API5:2023  | Broken Function Level Authorization             | `03`       |
| API6:2023  | Unrestricted Access to Sensitive Business Flows | `07`       |
| API7:2023  | Server Side Request Forgery                     | `04`       |
| API8:2023  | Security Misconfiguration                       | `05`, `06` |
| API9:2023  | Improper Inventory Management                   | `06`       |
| API10:2023 | Unsafe Consumption of APIs                      | `06`       |

### OWASP Top 10:2025

| Id       | Name                                   | Reference                        | Typical API pairing    |
| -------- | -------------------------------------- | -------------------------------- | ---------------------- |
| A01:2025 | Broken Access Control (includes SSRF)  | `03`, `04` (SSRF), `05`          | API1, API3, API5, API7 |
| A02:2025 | Security Misconfiguration              | `06`                             | API8, API9             |
| A03:2025 | Software Supply Chain Failures         | out of scope                     | —                      |
| A04:2025 | Cryptographic Failures                 | `02`, `06`                       | API2, API8             |
| A05:2025 | Injection                              | `04`                             | API8, API10            |
| A06:2025 | Insecure Design                        | `07`                             | API4, API6             |
| A07:2025 | Authentication Failures                | `02`                             | API2                   |
| A08:2025 | Software or Data Integrity Failures    | `04` (deserialization), `06`     | API10                  |
| A09:2025 | Security Logging and Alerting Failures | `04` (log injection), `05`, `06` | —                      |
| A10:2025 | Mishandling of Exceptional Conditions  | `08`, `05` (error leaks)         | API8                   |

A03:2025 (dependencies, build pipeline) is out of scope: say so in `not_reviewed` when relevant.
