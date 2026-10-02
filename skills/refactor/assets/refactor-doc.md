---
date: "{YYYY-MM-DD}"
requested_by: "{git config user.name}"
slug: "{slug}"
status: "{draft | implemented}"
---

# Refactor — {target}

## Goal & Problem

{Why this refactor: the structural pain, where it hurts, and the outcome. One paragraph.}

## Acceptance Criteria

Invariants that MUST hold after the refactor:

- [ ] {observable behavior preserved}
- [ ] {public interface preserved / intentionally unchanged}
- [ ] {performance or resource characteristic preserved}

## Test Plan

| Case                    | Type             | Input / state | Expected result    | Test file |
| ----------------------- | ---------------- | ------------- | ------------------ | --------- |
| {characterization case} | characterization | {input}       | {current behavior} | `{path}`  |
