# 02 — Evidence Logging

Evidence is the contract between `mentor` and `learning-profile`. Log what the learner did or
said, not your interpretation.

## What counts as evidence

| Signal     | Example observation                                     |
| ---------- | ------------------------------------------------------- |
| preference | "asked for a diagram before the explanation"            |
| strength   | "solved the recursion exercise unaided on first try"    |
| gap        | "confused dependency arrays with cleanup timing"        |
| goal       | "wants to ship a side project by December"              |
| constraint | "only has 20 minutes on weekdays"                       |
| pace       | "lost focus after ~25 minutes; picked up after a break" |
| feedback   | "wanted to try before any correction"                   |

One event per meaningful signal. Do not log every utterance, and do not log inferences without
the behavior that supports them.

## Event schema

Append to `{base}/learning/evidence/{YYYY-MM}.jsonl` following
`assets/evidence-event-template.jsonl`. Required fields: `id`, `ts`, `session`, `domain`,
`signal`, `observation`, `confidence`, `evidence`.

- `id` is sortable: `{ISO-timestamp}-{nn}`.
- `confidence` reflects how strong the evidence is, not how sure you are of the learner.
- `evidence` is the concrete behavior; keep the learner's wording when it matters.

## Protocol

1. Append events immediately after the session, before the profile update.
2. Never edit, reorder, or delete lines — the log is append-only.
3. Split by month; a session may append several events.
4. Then load `learning-profile` to fold the new events (it owns `evidence_cursor`).
5. If `learning-profile` cannot be loaded, say so; the events remain for the next run.

## Ownership

`mentor` writes events; `learning-profile` reads them and writes the profile. Neither skill
edits the other's artifacts. This one-way dependency keeps the profile auditable: every
`[inferred]` field traces back to a logged event id.
