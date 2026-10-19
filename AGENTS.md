# AGENTS.md

Skills repository. Each skill is a directory under `skills/{category}/{name}/` containing a `SKILL.md` plus optional `assets/` and `references/`. Categories: `authoring/`, `design/`, `implementation/`, `quality/`, `git/`, `maintenance/`, `learning/`.

## Skills

### authoring

| Skill          | Path                                       | Purpose                            |
| -------------- | ------------------------------------------ | ---------------------------------- |
| skill-creator  | `skills/authoring/skill-creator/SKILL.md`  | Create new LLM-first skills        |
| skill-improver | `skills/authoring/skill-improver/SKILL.md` | Audit and refactor existing skills |

### design

| Skill         | Path                                   | Purpose                                                |
| ------------- | -------------------------------------- | ------------------------------------------------------ |
| module-design | `skills/design/module-design/SKILL.md` | Design/analyze domain module boundaries and interfaces |
| adr           | `skills/design/adr/SKILL.md`           | Write architecture/design decision records (MADR)      |

### implementation

| Skill    | Path                                      | Purpose                                                   |
| -------- | ----------------------------------------- | --------------------------------------------------------- |
| tdd      | `skills/implementation/tdd/SKILL.md`      | Implement doc-first and test-first (red-green-refactor)   |
| refactor | `skills/implementation/refactor/SKILL.md` | Behavior-preserving restructuring in small verified steps |

### quality

| Skill             | Path                                        | Purpose                                                      |
| ----------------- | ------------------------------------------- | ------------------------------------------------------------ |
| code-review       | `skills/quality/code-review/SKILL.md`       | Review PRs/diffs via `gh`; request changes, never merge      |
| bug-scan          | `skills/quality/bug-scan/SKILL.md`          | Scan repo/modules for latent bugs, prove each with a test    |
| mutation-test     | `skills/quality/mutation-test/SKILL.md`     | Manual mutation testing of repo/modules; report survivors    |
| api-security-scan | `skills/quality/api-security-scan/SKILL.md` | Scan HTTP APIs for vulnerabilities, prove with exploit tests |
| tech-debt-scan    | `skills/quality/tech-debt-scan/SKILL.md`    | Scan repo/modules for technical debt, rank by priority score |

### git

| Skill         | Path                                | Purpose                                             |
| ------------- | ----------------------------------- | --------------------------------------------------- |
| create-pr     | `skills/git/create-pr/SKILL.md`     | Create standardized PRs with validated descriptions |
| create-commit | `skills/git/create-commit/SKILL.md` | Create conventional commits `type(scope): subject`  |

### maintenance

| Skill               | Path                                              | Purpose                                                       |
| ------------------- | ------------------------------------------------- | ------------------------------------------------------------- |
| update-dependencies | `skills/maintenance/update-dependencies/SKILL.md` | Update deps by mode with vulnerability/breaking-change checks |

### learning

| Skill            | Path                                        | Purpose                                                              |
| ---------------- | ------------------------------------------- | -------------------------------------------------------------------- |
| learning-profile | `skills/learning/learning-profile/SKILL.md` | Build and update the learner's structured profile                    |
| mentor           | `skills/learning/mentor/SKILL.md`           | Design/deliver profile-based sessions; depends on `learning-profile` |

## Skill Dependencies

- `mentor` depends on `learning-profile`: it MUST load `learning-profile` to create the profile when none exists, and again after every session to update the profile from the logged evidence. `mentor` never writes `profile.md` or the evidence log directly.

## Hard Rules

- `SKILL.md` is the normative runtime contract; follow `skills/authoring/skill-creator/references/skill-style-guide.md` when creating or updating skills.
- Keep the skill body 180–450 tokens (max 700). Move detail to `references/` and scripts/templates to `assets/`.
- `description` MUST be one quoted YAML-safe line, <=160 chars (max 250), triggers first, no `Keywords`.
- Frontmatter MUST include `name`, `description`, `license`, `metadata.author`, and `metadata.version`.
- References must point to local files.
- Skills with GitHub workflow rules (create-pr, code-review) MUST use the `gh` CLI and NEVER merge.
- Skills whose output has objectively checkable structure (commit, PR, ADR, scan report, SKILL.md) MUST ship a validator in `assets/` and run it before finishing: exit 0 with `OK`, or exit 1 with `ERROR:` lines (fix all). See the Output Validation section in `skill-style-guide.md`.

## Formatting

- Format Markdown (and other supported files) with `npm run fmt`; verify with `npm run fmt:check`.
- A husky pre-commit hook runs `lint-staged` → `oxfmt` on staged `*.md` files. Run `npm install` once to enable it.

## Testing

Contract for every validator: `--file`/`--body`/`--message` input (or stdin), exit 0 printing `OK` when valid, else exit 1 with one parseable `ERROR:` line per problem; `WARNING:` lines do not change the exit code.

- `create-pr`: `python3 skills/git/create-pr/assets/validate_pr_description.py --body <file> [--title "<title>"]`
- `create-commit`: `python3 skills/git/create-commit/assets/validate_commit_message.py --message "<subject>"`
- `adr`: `python3 skills/design/adr/assets/validate_adr.py --file <adr> [--allow-placeholders]`
- `bug-scan`: `python3 skills/quality/bug-scan/assets/reconcile.py --report <report.json>` then `python3 skills/quality/bug-scan/assets/validate_report.py --file <report.json>`
- `mutation-test`: `python3 skills/quality/mutation-test/assets/reconcile.py --report <report.json>` then `python3 skills/quality/mutation-test/assets/validate_report.py --file <report.json>`
- `api-security-scan`: `python3 skills/quality/api-security-scan/assets/reconcile.py --report <report.json>` then `python3 skills/quality/api-security-scan/assets/validate_report.py --file <report.json>`
- `tech-debt-scan`: `python3 skills/quality/tech-debt-scan/assets/reconcile.py --report <report.json>` then `python3 skills/quality/tech-debt-scan/assets/validate_report.py --file <report.json>`
- `module-design`: `python3 skills/design/module-design/assets/reconcile.py --report <brief.json>` then `python3 skills/design/module-design/assets/validate_brief.py --file <brief.json>`
- `skill-creator` / `skill-improver`: `python3 skills/authoring/skill-creator/assets/validate_skill.py --file <SKILL.md>`
- Validate every skill against `skill-style-guide.md` after edits using `skill-improver`.
