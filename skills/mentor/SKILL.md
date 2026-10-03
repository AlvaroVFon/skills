---
name: mentor
description: "Trigger: mentor, learning session, sesión de aprendizaje, teach me, study plan, design a lesson. Design and deliver profile-based sessions."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill to propose, design, and deliver learning sessions grounded in the learner's profile. Activate on requests to learn, study, or practice a topic with guidance, or to plan a curriculum. Not for building or editing the profile itself (`learning-profile`).

## Hard Rules

- DEPENDS ON `learning-profile`. ALWAYS load it in two cases: (1) at start if `profile.md` is absent, to create it; (2) at the end of every session, to fold the logged evidence into the profile. Never design or deliver without a profile.
- NEVER edit `profile.md` or the evidence log directly; all profile writes go through `learning-profile`.
- Resolve the same base as `learning-profile` (`references/03-location-and-format.md`): `LEARNING_HOME`, else the platform base, else ask.
- Design from the profile: match modality, structure, pacing, feedback, and constraints, and stay in the learner's zone of proximal development.
- NEVER contradict a `[confirmed]` constraint; if the requested session conflicts, surface it and ask before proceeding.
- Append one evidence event per meaningful signal to `{base}/learning/evidence/{YYYY-MM}.jsonl`; append-only, never edit or delete.
- If `learning-profile` is unavailable, stop and report the missing dependency; do not fabricate a profile.

## Decision Gates

| Condition                        | Action                                                  |
| -------------------------------- | ------------------------------------------------------- |
| `profile.md` absent              | Load `learning-profile`; create the profile first       |
| Session goal unclear             | Ask via the question tool                               |
| Goal conflicts with a constraint | Surface it; ask; never proceed silently                 |
| Session designed                 | Confirm scope and format with the learner, then deliver |
| Session delivered                | Append evidence events, then load `learning-profile`    |
| Strong new signal (gap/strength) | Log with confidence; flag it as a profile-update input  |
| `learning-profile` missing       | Stop; report the dependency; do not invent a profile    |

## Execution Steps

1. Resolve base and check for `profile.md` (`references/03-location-and-format.md`).
2. If absent, load `learning-profile` and create the profile; then continue.
3. Load the profile and clarify this session's goal via the question tool.
4. Design the session from `assets/session-plan-template.md` using `references/01-session-design.md`; confirm it with the learner.
5. Deliver interactively; adapt within the profile's constraints.
6. Record the session to `sessions/{YYYY-MM-DD}-{slug}.md` and append evidence events (`references/02-evidence-logging.md`).
7. Load `learning-profile` to update the profile from the new evidence.
8. Report.

## Output Contract

Return: session plan path; what was delivered; evidence events logged; the profile-update result reported by `learning-profile`; open questions and next-session suggestions.

## References

- `references/01-session-design.md` — profile → objectives, modality, difficulty, assessment
- `references/02-evidence-logging.md` — evidence signals, append-only protocol, cursor
- `references/03-location-and-format.md` — path resolution and file formats
- `assets/session-plan-template.md` — session plan and record skeleton
- `assets/evidence-event-template.jsonl` — evidence event schema
