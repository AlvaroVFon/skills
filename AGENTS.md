# AGENTS.md

Skills repository. Each skill is a directory under `skills/{name}/` containing a `SKILL.md` plus optional `assets/` and `references/`.

## Skills

| Skill            | Path                               | Purpose                                                              |
| ---------------- | ---------------------------------- | -------------------------------------------------------------------- |
| skill-creator    | `skills/skill-creator/SKILL.md`    | Create new LLM-first skills                                          |
| skill-improver   | `skills/skill-improver/SKILL.md`   | Audit and refactor existing skills                                   |
| code-review      | `skills/code-review/SKILL.md`      | Review PRs/diffs via `gh`; request changes, never merge              |
| create-pr        | `skills/create-pr/SKILL.md`        | Create standardized PRs with validated descriptions                  |
| create-commit    | `skills/create-commit/SKILL.md`    | Create conventional commits `type(scope): subject`                   |
| module-design    | `skills/module-design/SKILL.md`    | Design/analyze domain module boundaries and interfaces               |
| adr              | `skills/adr/SKILL.md`              | Write architecture/design decision records (MADR)                    |
| bug-scan         | `skills/bug-scan/SKILL.md`         | Scan repo/modules for latent bugs, prove each with a test            |
| mutation-test    | `skills/mutation-test/SKILL.md`    | Manual mutation testing of repo/modules; report survivors            |
| refactor         | `skills/refactor/SKILL.md`         | Behavior-preserving restructuring in small verified steps            |
| tdd              | `skills/tdd/SKILL.md`              | Implement doc-first and test-first (red-green-refactor)              |
| learning-profile | `skills/learning-profile/SKILL.md` | Build and update the learner's structured profile                    |
| mentor           | `skills/mentor/SKILL.md`           | Design/deliver profile-based sessions; depends on `learning-profile` |

## Skill Dependencies

- `mentor` depends on `learning-profile`: it MUST load `learning-profile` to create the profile when none exists, and again after every session to update the profile from the logged evidence. `mentor` never writes `profile.md` or the evidence log directly.

## Hard Rules

- `SKILL.md` is the normative runtime contract; follow `skills/skill-creator/references/skill-style-guide.md` when creating or updating skills.
- Keep the skill body 180–450 tokens (max 700). Move detail to `references/` and scripts/templates to `assets/`.
- `description` MUST be one quoted YAML-safe line, <=160 chars (max 250), triggers first, no `Keywords`.
- Frontmatter MUST include `name`, `description`, `license`, `metadata.author`, and `metadata.version`.
- References must point to local files.
- Skills with GitHub workflow rules (create-pr, code-review) MUST use the `gh` CLI and NEVER merge.

## Formatting

- Format Markdown (and other supported files) with `npm run fmt`; verify with `npm run fmt:check`.
- A husky pre-commit hook runs `lint-staged` → `oxfmt` on staged `*.md` files. Run `npm install` once to enable it.

## Testing

- `create-pr` validation: `python3 skills/create-pr/assets/validate_pr_description.py --body <file> [--title "<title>"]` → exit 0 with `OK`, or exit 1 with `ERROR:` lines.
- `create-commit` validation: `python3 skills/create-commit/assets/validate_commit_message.py --message "<subject>"` → exit 0 with `OK`, or exit 1 with `ERROR:` lines.
- Validate every skill against `skill-style-guide.md` after edits using `skill-improver`.
