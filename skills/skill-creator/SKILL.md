---
name: skill-creator
description: "Trigger: new skills, agent instructions, documenting AI usage patterns. Create LLM-first skills with valid frontmatter."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.1"
---

## Activation Contract

Create a skill when:

- A pattern is used repeatedly and AI needs guidance
- Project-specific conventions differ from generic best practices
- Complex workflows need step-by-step instructions
- Decision trees help AI choose the right approach

Do not create a skill when the pattern is trivial, one-off, or better served by normal documentation.

## Hard Rules

- ALWAYS follow `references/skill-style-guide.md` as the normative source before creating or updating skills, whether working in this repo or on an installed global skill.
- If that file is missing, use the compact inline rules below.
- A skill is a runtime instruction contract for an LLM, not human documentation.
- Do not add a `Keywords` section; preserve essential trigger words in `description`.
- References must point to local files.
- Keep the skill body concise: target 180–450 tokens, recommended max 700, hard max 1000.
- ALWAYS run `python3 assets/validate_skill.py --file {skill}/SKILL.md` and fix every `ERROR` until exit 0 before finishing.

## Decision Gates

| Need                                                  | Action                           |
| ----------------------------------------------------- | -------------------------------- |
| Code templates, schemas, fixtures, generated examples | Put them in `assets/`            |
| Conceptual detail, edge cases, existing docs          | Put local links in `references/` |
| Long explanation in `SKILL.md`                        | Move it to a supporting file     |
| Multiple meaningful paths                             | Add a compact decision table     |

## Execution Steps

1. Read `references/skill-style-guide.md` and apply it. Fall back to the inline rules below only if that file is missing.
2. Confirm the skill does not already exist and the pattern is reusable.
3. Create or update `skills/{skill-name}/SKILL.md` using this required structure:

```
skills/{skill-name}/
├── SKILL.md              # Required - main skill file
├── assets/               # Optional - templates, schemas, examples
│   ├── template.py
│   └── schema.json
└── references/           # Optional - local docs the skill body links to
    └── docs.md
```

1. Use this frontmatter shape:

```markdown
---
name: { skill-name }
description: "Trigger: {essential trigger words users or agents will say}. {What this skill does}."
license: Apache-2.0
metadata:
  author: "{your-github-username}"
  version: "1.0"
---
```

1. Write sections in this order: Activation Contract, Hard Rules, Decision Gates, Execution Steps, Output Contract, References.
2. Run `python3 assets/validate_skill.py --file {skill}/SKILL.md`; fix every `ERROR:` until exit 0. A referenced `references/` or `assets/` file must exist.
3. Register the skill in `AGENTS.md` when it is a project skill.

## Inline Fallback Rules

- `description` MUST be one physical line, quoted, YAML-safe, and include essential trigger words first.
- `description` SHOULD be <=160 chars and MUST be <=250 chars.
- Frontmatter MUST include `name`, `description`, `license`, `metadata.author`, and `metadata.version`.
- Use imperative instructions, not tutorials or background prose.
- Put supporting material in `assets/` or `references/`, not the main skill body.

Good:

```yaml
description: "Trigger: Jira task, ticket, issue, task creation. Create Jira tasks in the team format."
```

Bad:

```yaml
description: >
  Create Jira tasks in the team format. Trigger: Jira task, ticket, issue, or task creation.

Keywords: jira, task
```

## Output Contract

Return:

- Files created or modified.
- Whether the style guide or the inline fallback rules were used.
- Any AGENTS.md registration change.
- Any supporting files added under `assets/` or `references/`.

## References

- `references/skill-style-guide.md` — normative LLM-first skill style guide.
- `assets/validate_skill.py` — SKILL.md validator (frontmatter, sections, budget, links).
