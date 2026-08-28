# Code Review Checklist

Scan each changed file for the categories below. Mark findings with `[Blocking]`, `[Should]`, or `[Nit]` per the severity rules in `SKILL.md`. Only report issues introduced by or directly affected by the diff.

## Correctness

- [ ] Logic matches the PR's stated intent.
- [ ] Edge cases handled: empty inputs, null/undefined, zero, off-by-one, duplicates.
- [ ] Data flow correct across the change: no dropped or misrouted values.
- [ ] Async/concurrency issues: races, stale closures, unawaited promises, lost updates.
- [ ] Types and contracts respected: no silent casts, no bypassing validation.

## Error Handling

- [ ] Failures are caught and propagated, not swallowed.
- [ ] Error messages are actionable; errors include context.
- [ ] Partial failures cleaned up (resources, transactions, side effects).
- [ ] No sensitive data leaked in logs or error responses.

## Security

- [ ] User input validated and sanitized (injection, path traversal, XSS). Escalates to Blocking.
- [ ] No secrets, tokens, or credentials added to the diff or logs. Blocking.
- [ ] AuthZ checked on new endpoints/handlers; no missing permission gate. Blocking.
- [ ] Dependencies: no new risky or unmaintained package added without justification.

## Performance

- [ ] No accidental O(n²) patterns, N+1 queries, or work in hot loops.
- [ ] Large objects not copied needlessly; no redundant re-renders/requests.
- [ ] Resources bounded: no unbounded caches, retries, or recursion.

## Tests

- [ ] New behavior covered by tests that exercise both happy path and failure path.
- [ ] Tests assert real behavior, not implementation detail.
- [ ] No test skipped/disabled to green-light this change.

## Maintainability

- [ ] Names describe responsibility and domain, not mechanism.
- [ ] No copy-paste duplication introduced; reuse existing helpers where present.
- [ ] Dead code, debug output, and commented-out code removed.
- [ ] Complexity of new functions is reasonable and readable.

## Consistency

- [ ] Change is consistent with the surrounding codebase conventions (naming, error style, module layout).
- [ ] Docs/contracts adjusted if public API or behavior changed.
- [ ] The change as a whole is coherent and not a mix of unrelated concerns.