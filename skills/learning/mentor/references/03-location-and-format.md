# 03 — Location & Formats

## Resolving the base

Both `mentor` and `learning-profile` share one base directory so they read the same files.

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
├── profile.md                     # owned by learning-profile
├── evidence/
│   └── {YYYY-MM}.jsonl            # append-only, written by mentor
└── sessions/
    └── {YYYY-MM-DD}-{slug}.md     # written by mentor, from assets/session-plan-template.md
```

Create `evidence/` and `sessions/` when you first write to them.

## Reading the profile

`mentor` reads `profile.md` frontmatter (`version`, `evidence_cursor`) and body but never writes
it. If it is absent, load `learning-profile` to create it before designing anything.

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

Append only; never edit, reorder, or delete a line. `learning-profile` owns the cursor that
tracks which events it has folded.

## Session file

One file per session under `sessions/`, named `{YYYY-MM-DD}-{slug}.md`. It doubles as the plan
(before) and the record (after); update its `status` and Record section after delivery.
