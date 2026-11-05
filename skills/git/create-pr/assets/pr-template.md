# PR Description Template

Use this exact structure for every PR body. Start with `AI_GENERATED`, then the required section: `Objective`. Optional sections: `Validation`, `Risks` (include them when relevant; one line in `Validation` is expected for most changes). Write in English.

```markdown
AI_GENERATED

## Objective

<One short paragraph describing what this PR does and why it is needed.>

## Validation

- <How it was tested/validated (unit tests run, manual steps, CI)>

## Risks

- <Optional: risks, breaking changes, performance impact, related PRs/dependencies>
```

## Examples

### Good

```markdown
AI_GENERATED

## Objective

Add rate limiting to the public API to prevent abuse of the signup endpoint.

## Validation

- `pytest tests/middleware -q` passes (24 tests).
- Manual: 5 rapid requests to POST /signup return 429 after the limit.

## Risks

- Limits are strict by default; ops may need to tune env vars during rollout.
```

### Bad — do not submit

```markdown
rate limiting added

- middleware now limits the api signups so they dont get bombed
- env vars
```

Problems: no `AI_GENERATED` first line, no `## Objective` paragraph, no `## Validation`, title filled in as the body.
