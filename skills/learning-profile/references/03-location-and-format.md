# 03 — Location & Formats

## Resolving the base

Both `learning-profile` and `mentor` share one base directory so they read the same files.

1. If `LEARNING_HOME` is set and non-empty, use it (escape hatch to share one profile across
   platforms).
2. Else derive the platform base from the loaded skill's own path. A skill lives at
   `<base>/skills/<name>/SKILL.md`, so the base is the grandparent of the skill directory:
   - opencode → `~/.config/opencode`
   - Claude Code → `~/.claude`
   - Codex → `~/.codex`
3. If neither is available, ask the learner for the path via the question tool. Never guess and
   never write outside the resolved base.

## Layout

```
{base}/learning/
├── profile.md                     # structured learner profile
├── evidence/
│   └── {YYYY-MM}.jsonl            # append-only evidence events, one per month
└── sessions/
    └── {YYYY-MM-DD}-{slug}.md     # session plan and record
```

Create `learning/`, `evidence/`, and `sessions/` on first write if missing. Do not create them
just to check for a profile.

## Profile file

- Markdown with YAML frontmatter: `learner`, `version`, `created`, `updated`,
  `evidence_cursor`, `source_base`.
- Body follows `assets/profile-template.md`; preserve unknown sections and fields verbatim.
- Version increments only on structural changes to the template, not on routine updates.

## Evidence event (one JSON object per line)

```json
{
  "id": "2026-10-03T14:05:00Z-01",
  "ts": "2026-10-03T14:05:00Z",
  "session": "2026-10-03-react-hooks",
  "domain": "react",
  "signal": "gap",
  "observation": "confused by dependency arrays after cleanup",
  "confidence": 0.7,
  "evidence": "took 3 attempts; asked why cleanup reruns"
}
```

- `signal` is one of `preference|strength|gap|goal|constraint|pace|feedback`.
- `confidence` is a float `0..1`; `evidence` is the concrete behavior that justifies it.
- Append only. Never edit, reorder, or delete a line.
- Split files by month (`{YYYY-MM}.jsonl`); a session may append several events.

## Session file

Session plans and records live in `sessions/` and follow `mentor`'s
`assets/session-plan-template.md`. `learning-profile` reads them only if the evidence log
points to them.
