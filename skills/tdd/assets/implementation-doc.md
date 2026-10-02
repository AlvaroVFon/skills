---
date: "{YYYY-MM-DD}"
requested_by: "{git config user.name}"
slug: "{slug}"
status: "{draft | implemented}"
---

# Implementation — {title}

## Goal & Problem

{The problem and the user-facing outcome. One paragraph.}

## Acceptance Criteria

- [ ] {checkable, observable criterion}
- [ ] {checkable, observable criterion}

## Test Plan

| Case         | Type  | Input / state | Expected result | Test file |
| ------------ | ----- | ------------- | --------------- | --------- |
| {happy path} | happy | {input}       | {result}        | `{path}`  |
| {boundary}   | edge  | {input}       | {result}        | `{path}`  |
| {failure}    | error | {input}       | {result}        | `{path}`  |
