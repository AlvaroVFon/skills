# 03 — Pull Complexity Downwards

## Definition

The implementer of a module should absorb complexity rather than expose it to callers. Deciding **how to allocate complexity** is the hardest part of design. A module takes total responsibility: it resolves edge cases, derives values, and applies sane defaults so the common case is trivial.

Three focuses:

- **No exceptionitis**: do not raise exceptions for conditions the module can handle; do not force the caller to translate internal errors.
- **Over-configuration**: every configuration parameter is complexity pushed upward and multiplies the test matrix. Parameters should be rare; almost always there is a default or an auto-detectable value.
- **Total responsibility**: the module solves the whole problem; it does not leave special cases or derived data to the caller.

## Signals

| Signal                  | Test                                                             |
| ----------------------- | ---------------------------------------------------------------- |
| Over-configuration      | Could the parameter be a default or be auto-detected?            |
| Exceptionitis           | Does the module raise for cases it could handle?                 |
| Internal error taxonomy | Must the caller know or translate internal error types?          |
| Derived data            | Does the caller compute something the module can already derive? |
| Special cases outside   | Does the caller branch on the module's domain edge cases?        |
| Redundant state         | Does the caller pass back data the module already held?          |
| Missing defaults        | Does the common case require passing every value?                |

## Design Moves

1. **Absorb** edge cases internally (fallback, retry, normalization).
2. **Auto-detect or derive** instead of requiring parameters.
3. Provide **sane defaults**: parameters are optional overrides, never mandatory on the common path.
4. **Normalize errors** into domain-meaningful failures, not an internal taxonomy.
5. Decide genuinely variable policy **once, at a high point** — dependency injection or strategy at the composition root is the legitimate mechanism.

## The Limit: Do Not Over-Absorb

Absorbing too much is as harmful as absorbing too little. Real variability and real failures must surface. The rule:

> Absorb only the complexity that belongs to the module's responsibility. Decide genuinely variable policy once, at a high point. Unrecoverable failures must surface, but with domain meaning.

If a caller genuinely must decide, that is policy, and it belongs at a composition point — not hidden inside the module.

## Failure Contract

Always define **what can fail and how the caller sees it**. Normalizing errors must not hide real failures. The contract states, in domain terms, the failure modes a caller can observe and what it is expected to do about each.

## Edge Cases

- **DI / strategy**: the legitimate way to push variable policy upward a single time. Not a violation of "pull complexity downwards".
- **Infrastructure errors**: translate them at the boundary; the domain interface must not expose connection, HTTP, or ORM errors.
- **Retry/fallback**: absorbing a transient failure is correct; absorbing a permanent one hides a bug.
- **Test matrix**: each added parameter multiplies cases; prefer a default and remove the parameter.

## Mini-Checklist

- [ ] Every parameter justifies why it cannot be a default or auto-detected.
- [ ] The common case requires no parameters beyond sane defaults.
- [ ] Internal errors are normalized into domain-meaningful failures.
- [ ] Infrastructure exception types do not cross the boundary.
- [ ] The module absorbs the complexity of its own responsibility.
- [ ] Variable policy is decided once at a high point (DI/strategy).
- [ ] The failure contract is explicit.
