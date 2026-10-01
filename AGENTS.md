# AGENTS.md

Skills repository. Each skill is a directory under `skills/{name}/` containing a `SKILL.md` plus optional `assets/` and `references/`.

## Skills

| Skill          | Path                             | Purpose                                                 |
| -------------- | -------------------------------- | ------------------------------------------------------- |
| skill-creator  | `skills/skill-creator/SKILL.md`  | Create new LLM-first skills                             |
| skill-improver | `skills/skill-improver/SKILL.md` | Audit and refactor existing skills                      |
| code-review    | `skills/code-review/SKILL.md`    | Review PRs/diffs via `gh`; request changes, never merge |
| create-pr      | `skills/create-pr/SKILL.md`      | Create standardized PRs with validated descriptions     |
| create-commit  | `skills/create-commit/SKILL.md`  | Create conventional commits `type(scope): subject`      |
| module-design  | `skills/module-design/SKILL.md`  | Design/analyze domain module boundaries and interfaces  |
| adr            | `skills/adr/SKILL.md`            | Write architecture/design decision records (MADR)       |

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
