# 01 — Scan Modes

## Definition

- **Global**: cover the whole API by attack surface, not uniformly.
- **Targeted**: cover only the selected routes/paths/modules and the middleware and services they reach.

Coverage must always be declared: what was reviewed, in what depth, and what was skipped.

## Choosing the Scan Type (Mandatory)

Ask with the option selector (question tool) before any work, every run — never infer from the prompt:

1. **Mode**: `Global` (whole API) or `Targeted` (named routes/paths/modules). If `Targeted`, request them in the same round.
2. **Categories** (multi-select): `authn` (`02`), `authz` (`03`), `injection` (`04`), `info-leak` (`05`), `config-exposure` (`06`), `resource-business` (`07`), `error-handling` (`08`), or `all`. Load only the chosen references.
3. **Output format**: `chat` (concise summary) or `markdown` (full rendered report) — never both. The JSON report is written either way.

If the question tool is unavailable, ask in chat and wait for the answer.

## Reconnaissance — Endpoint Inventory

The exploration subagent returns facts, not verdicts:

- Every route: method, path, handler `file:line`, middleware chain (auth, role, validation, rate limit), input sources (params, query, body, headers, files), data touched (model/table, owner field).
- Global middleware: error handler, CORS, body parser limits, security headers, logger, serializer.
- Outbound calls (HTTP clients, webhooks, URL fetchers) and secret/config loading.
- Test framework, in-process HTTP harness (supertest, test client), auth fixtures, and the command to run one test file.

Frameworks: Express/Fastify (`app.get`, `router.use`), NestJS (`@Controller`, `@Get`, guards, pipes, interceptors), Koa, Next.js API routes; non-Node equivalents (FastAPI, Django, Spring) follow the same inventory.

## Global — Risk Ranking

| Signal                                                      | Risk   |
| ----------------------------------------------------------- | ------ |
| Unauthenticated routes, login/reset/signup, webhooks        | High   |
| Routes taking an object id (`/:id`) or owner-scoped data    | High   |
| Admin/role-gated routes, money, balances, coupons           | High   |
| Write routes with body → storage, file upload, URL fetch    | High   |
| Authenticated reads returning user or PII data              | Medium |
| Global middleware (error handler, CORS, logger, serializer) | Medium |
| Static, health, purely public catalogue reads               | Low    |

Deepen High first, then Medium while budget remains. Low is listed as **not reviewed** unless trivially covered. The previous report moves unreviewed and changed routes up (`references/11-baseline-history.md`).

## Targeted — Flow Tracing

1. Resolve each target to its routes and the full middleware chain (global + router + route).
2. Trace down to storage and outbound calls; trace up to who can call it (auth state, roles).
3. Stop at the service boundary; note crossings as out of scope.

## Edge Cases

- **Gateway/proxy does auth or rate limiting**: if it is not in the repo, mark the control **unverified** and the finding Unconfirmed; never assume it exists.
- **Monorepo**: one service per module; rank services first.
- **No HTTP test harness**: every finding becomes Unconfirmed with manual steps; say so.
- **Generated clients, vendored code, OpenAPI specs only**: use specs to find routes, but findings need code.
