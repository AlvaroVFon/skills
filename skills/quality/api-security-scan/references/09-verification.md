# 09 — Verification

## Definition

A finding is only reported with a verdict earned by evidence. The default evidence is an **exploit test**: an in-process HTTP test that succeeds in the attack on the current code (the assertion of the secure behavior fails).

## Protocol

1. State the prediction: "As `{identity}`, `{METHOD} {path}` with `{payload}` must be rejected/filtered, but returns `{status}` with `{evidence}`".
2. Use the repo's framework and in-process harness (supertest `request(app)`, Nest `Test.createTestingModule` + `app.getHttpServer()`, Fastify `inject`, FastAPI `TestClient`).
3. Write the test in a temporary file next to the repo's tests named `*.security-scan.{finding-id}.*`. Never edit existing tests or production code.
4. Use synthetic fixtures (two users, two tenants, one admin) and the repo's in-memory DB or mocks. Stub every outbound HTTP call.
5. Run only that file; capture status, headers, and the relevant body fragment.
6. Delete every temporary test; `git status` must show nothing besides the report.

## Network Boundary (Hard)

Never call a running server, `localhost` port, staging, production, or third-party host. If the bug only shows against real infrastructure, it is **Unconfirmed** with manual steps for a local instance the user controls.

## Parallel Verification

1. List every finding with `file:line`, endpoint, and prediction.
2. Dispatch one write-capable subagent per finding in a single message using `assets/verify-exploit-subagent.md`; at most 4 concurrent, queue the rest.
3. Serialize findings sharing infrastructure (in-memory DB singleton, ports, global app state).
4. Collect facts, assign verdicts, confirm no temp files remain.
5. No write-capable subagent: run the protocol sequentially yourself.

## Verdicts

| Result                                         | Verdict     | Report                                              |
| ---------------------------------------------- | ----------- | --------------------------------------------------- |
| Attack succeeds as predicted                   | Confirmed   | Exploit test and its output (redacted)              |
| Fails for another reason (setup, import, stub) | Retry once  | Fix the test, not the code; else Unconfirmed        |
| Attack rejected / field absent                 | Discarded   | Counted in the summary, not listed                  |
| Cannot be run (gateway, infra, real provider)  | Unconfirmed | Test sketch plus manual steps                       |
| Static proof only (hardcoded secret, config)   | Confirmed   | Evidence type `manual`, `file:line`, redacted value |

## Redaction

Never paste real secrets, tokens, or PII into tests, outputs, or the report. Keep the first 4 chars then `…`. `validate_report.py` warns (W15) on JWT/private-key/API-key patterns.

## Manual Verification Steps

For Unconfirmed: numbered steps against a local instance — preconditions (users/roles/data), exact request (`curl` with placeholders for tokens), expected vs observed, and what to watch (status, header, log line).
