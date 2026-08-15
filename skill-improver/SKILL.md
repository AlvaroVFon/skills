---
name: skill-improver
description: "Trigger: improve skills, audit skills, refactor skills, skill quality. Audit and upgrade existing LLM-first skills."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## Activation Contract

Use this skill when asked to audit, refactor, normalize, or improve existing `SKILL.md` files. Use `skill-creator` instead when creating a brand-new skill from a reusable pattern.

## Hard Rules

- ALWAYS treat `references/skill-style-guide.md` as the normative style contract, whether working in this repo or on an installed global skill.
- Treat `SKILL.md` as the source of truth; preserve author intent, critical rules, activation semantics, and output requirements.
- Discover skills by scanning `.github/skills/`, `.opencode/skills/`, and `.claude/skills/` for `*/SKILL.md`; this repo has no generated skill registry. Each skill is mirrored across the three directories.
- Default to audit-only. Modify files only when the user explicitly asks to apply improvements.
- Never delete meaningful content silently; move long explanation, examples, templates, or schemas into local `references/` or `assets/`.
- Do not invent triggers, policies, or domain rules. Mark ambiguous cases for human review.

## Decision Gates

| Situation                           | Action                                                               |
| ----------------------------------- | -------------------------------------------------------------------- |
| Missing or invalid frontmatter      | Fix `name`, quoted one-line `description`, `license`, and `metadata` |
| Skill reads like tutorial docs      | Convert to runtime instructions and move background to `references/` |
| Body exceeds budget                 | Preserve rules, move examples/background to supporting files         |
| Branching logic hidden in prose     | Convert to a compact decision table                                  |
| Rules conflict or intent is unclear | Report the issue; do not rewrite that rule automatically             |

## Execution Steps

1. Read `references/skill-style-guide.md` and apply it. If it's missing, enforce the core LLM-first structure directly: frontmatter, Activation Contract, Hard Rules, Decision Gates, Execution Steps, Output Contract, References.
2. Scan `.github/skills/`, `.opencode/skills/`, and `.claude/skills/` for `*/SKILL.md` and select the skills to audit from those paths.
3. For each selected skill, audit metadata, trigger clarity, section order, body budget, actionability, decision gates, output contract, and local references.
4. Return an audit report grouped by skill with severity and exact proposed changes.
5. In apply mode, edit only safe issues, preserve content, and create supporting files when needed.

## Output Contract

Return:

- Skills audited and paths used.
- Issues found, grouped by severity.
- Files changed, if apply mode was requested.
- Ambiguities that need human review.

## References

- `references/skill-style-guide.md` — normative LLM-first skill style guide.
