# Conventional Commits Reference

Every commit must follow the Conventional Commits format:

```
<type>(<scope>): <subject>
```

Example: `feat(api): add rate limiting middleware`

## Format

- `<type>` — one of the allowed types below.
- `<scope>` — short, descriptive name of the module/area changed (no spaces, <=40 chars). Required.
- `<subject>` — descriptive imperative phrase (lowercase, no trailing period, <=72 chars for the full line).

## Allowed Types

| Type     | When to use                                          | Example                                        |
| -------- | ---------------------------------------------------- | ---------------------------------------------- |
| feat     | New feature or user-visible behavior                 | `feat(auth): add token refresh endpoint`       |
| fix      | Bug fix                                              | `fix(parser): handle empty input`              |
| refactor | Code restructure with no behavior change             | `refactor(store): extract cursor pagination`   |
| perf     | Performance improvement                              | `perf(render): batch DOM updates`              |
| test     | Tests only                                           | `test(cart): cover quantity edge cases`        |
| docs     | Docs or comments only                                | `docs(api): document retry policy`             |
| chore    | Build, tooling, maintenance, dependencies            | `chore(deps): bump express to 5`               |
| ci       | CI/CD configuration                                  | `ci(release): add publish workflow`            |
| style    | Formatting, whitespace, no logic change              | `style(core): run prettier`                    |
| build    | Build system changes                                 | `build(docker): pin base image digest`         |

## Scope

Derive the scope from the changed paths — a clearly-named module, service, or
area (e.g. `auth`, `api`, `parser`, `store`). Keep it short and lowercase; no
spaces, punctuation, or path segments.

## Subject Rules

- Imperative mood: `add ...`, `fix ...`, `remove ...`, `handle ...`.
- Lowercase start: `feat(ui): add dark mode` — NOT `feat(ui): Add dark mode`.
- No trailing period.
- Full line <=72 chars, including `type(scope): `.
- One logical change per commit.

## Examples

### Good

- `feat(api): add rate limiting middleware`
- `fix(parser): handle empty input`
- `refactor(store): extract cursor pagination`
- `test(cart): cover quantity edge cases`
- `docs(api): document retry policy`

### Bad — do not submit

- `add stuff` — no type/scope, not in format.
- `FIX auth: Fixed login bug` — uppercase type, non-imperative, uppercase subject.
- `feat(auth/server/refresh-tokens): improve things` — scope too long with segments; subject vague.
- `feat: add rate limiting` — scope missing.
