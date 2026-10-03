# 02 — Evidence Updates

The profile is a living document. Update mode folds evidence events into it; it never
rewrites the whole profile.

## Signal → field mapping

| `signal`   | Target field(s)                                     |
| ---------- | --------------------------------------------------- |
| preference | Preferences (modality, structure, pacing, feedback) |
| goal       | Snapshot goals, current focus, target level         |
| strength   | Meta-cognition strengths, domain strengths          |
| gap        | Meta-cognition gaps, domain gaps, Open Questions    |
| constraint | Motivation & Constraints                            |
| pace       | Preferences pacing, session length                  |
| feedback   | Preferences feedback style                          |

A signal the learner rejects, or that contradicts a `[confirmed]` field, is not applied
silently — confirm it first.

## Merge rules

1. **Confirmed beats inferred.** A `[confirmed]` field is only changed by new `[confirmed]`
   input or by confirming an inferred change with the learner.
2. **Inferred updates inferred.** New evidence may overwrite an older `[inferred:<id>]` field
   when the newer event has equal or higher confidence.
3. **Confidence gate.** Apply `confidence >= 0.6` automatically; below that, record under Open
   Questions instead of changing a field.
4. **Additive.** New domains, strengths, gaps, and constraints are appended; removed items are
   struck only with explicit learner consent.
5. **Provenance.** Retag the field with the event id that justified the change.

## Cursor protocol

`evidence_cursor` in the profile frontmatter holds the last event id folded in.

1. Read only events whose `id` sorts after the cursor.
2. Fold them (log or caller batch treated identically).
3. Set the cursor to the newest event id folded and bump `updated`.
4. If there are no new events, report "no changes" and leave the file untouched.

Event `id` values are monotonically sortable (`YYYY-MM-DDThh:mm:ssZ-{n}`).

## Conflict handling

- Two events disagree: keep the more recent `[confirmed]` one; note the other in Open Questions.
- Evidence contradicts a confirmed field: ask the learner which is right before changing.
- Duplicate observations: fold once; do not inflate confidence by counting repeats.

## Never

- Never edit, reorder, or delete lines in the evidence log.
- Never invent an event id or provenance tag.
- Never drop a field because its evidence is thin; leave it and mark it uncertain.
