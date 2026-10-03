---
name: learning-profile
description: "Trigger: learning profile, perfil de aprendizaje, learner profile, questionnaire, update profile. Build and update a structured learner profile."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill to create or update the learner's structured profile. Activate when the learner asks to build or refresh their profile, or when `mentor` invokes it to create a missing profile or fold post-session evidence. Not for designing sessions (`mentor`).

## Hard Rules

- ALWAYS resolve the base path first and write only under `{base}/learning/` (`references/03-location-and-format.md`): use `LEARNING_HOME` if set, else the platform base of the loaded skill, else ask.
- Create mode only when `profile.md` is absent; otherwise update mode. In update mode never discard existing fields.
- ALWAYS interview with the question tool in themed blocks from `assets/questionnaire.md`; never infer answers. One block at a time; adapt follow-ups.
- Tag every field `[confirmed]` (asked) or `[inferred:<event-id>]` (evidence). Never fabricate values; leave unknowns in Open Questions.
- Fold evidence the same way whether it comes from the log or a caller-supplied batch. Advance `evidence_cursor` only after folding.
- Confirm with the learner before changing a `[confirmed]` field from weak evidence. Never edit the append-only evidence log.

## Decision Gates

| Condition                     | Action                                                    |
| ----------------------------- | --------------------------------------------------------- |
| `LEARNING_HOME` set           | Use it as base                                            |
| Loaded skill path known       | Base = grandparent of `skills/<name>/`                    |
| Base still unknown            | Ask the learner via the question tool                     |
| `profile.md` absent           | Create mode: questionnaire, then write                    |
| `profile.md` present          | Update mode: read profile + events past `evidence_cursor` |
| No new events past cursor     | Report "no changes"; do not rewrite the file              |
| Evidence conflicts with field | Confirm with the learner before changing it               |
| Caller passed an evidence set | Fold it, then advance the cursor                          |

## Execution Steps

1. Resolve base and paths for `profile.md`, `evidence/`, `sessions/` (`references/03-location-and-format.md`).
2. Load `profile.md` if present; otherwise start from `assets/profile-template.md` in create mode.
3. Create: run questionnaire blocks (`assets/questionnaire.md`) one at a time, probing dimensions (`references/01-dimensions.md`).
4. Create: synthesize answers into the template and write `profile.md`.
5. Update: read events past `evidence_cursor` plus any caller batch; map signals to fields, apply merge rules, confirm conflicts (`references/02-evidence-updates.md`).
6. Advance `evidence_cursor`, bump `updated`, rewrite `profile.md` preserving untouched fields.

## Output Contract

Return: profile path; mode (create|update); fields added or changed with provenance; events processed and the new cursor; open questions; what was not asked or remains uncertain.

## References

- `references/01-dimensions.md` — profile dimensions and how to probe them
- `references/02-evidence-updates.md` — signal mapping, merge rules, cursor, provenance
- `references/03-location-and-format.md` — path resolution and file formats
- `assets/questionnaire.md` — interactive question blocks
- `assets/profile-template.md` — profile skeleton
