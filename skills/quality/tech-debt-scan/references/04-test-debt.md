# 04 — Test Debt

Category `tests`. Measure test health, not test strength: use `mutation-test` to judge whether assertions catch regressions. Missing or weak tests mostly cost as `unknown-unknowns` (changes break silently).

| Signal                | How to measure                                                  | Debt when                                          | Symptom · cause                   |
| --------------------- | --------------------------------------------------------------- | -------------------------------------------------- | --------------------------------- |
| Untested hotspot      | Coverage report if available, else map tests to hotspot modules | High-churn module with no or minimal tests         | unknown-unknowns · obscurity      |
| Coverage gaps in core | Per-module coverage from the existing report                    | Critical flow (money, auth, persistence) uncovered | unknown-unknowns · obscurity      |
| Skipped tests         | `grep -rnE "\.skip\|xit\|@Disabled\|pytest.mark.skip"` + age    | Skipped without a reason or for > ~3 months        | unknown-unknowns · obscurity      |
| Flaky markers         | Retries, sleeps, `retry`/`flaky` annotations, CI rerun history  | Retries or fixed sleeps hide nondeterminism        | unknown-unknowns · obscurity      |
| Brittle tests         | Heavy mocking of internals, snapshot-everything, order coupling | Tests break on refactors that keep behavior        | change-amplification · dependency |
| Slow suite            | Run the suite once and time it, or read CI durations            | Feedback loop long enough to discourage running it | cognitive-load · obscurity        |
| Missing test layers   | Inventory unit/integration/e2e folders                          | Only one layer exists for a service-heavy codebase | unknown-unknowns · obscurity      |
| Test duplication      | Repeated setup blocks, copy-pasted fixtures                     | No shared builders/fixtures across many files      | change-amplification · dependency |

## Rules

- Do not install tools or change config to produce coverage; use an existing report or state `coverage not available` in `evidence.result`.
- Run the suite only when its command is known, safe, and needs no external services.

## Edge Cases

- **No tests at all**: one finding per High-interest module, not one per file.
- **Coverage gate in CI**: read its threshold and treat it as a fact, not as proof of quality.
