#!/usr/bin/env python3
"""Validate a github-planner plan.

Usage:
    validate_plan.py --file <plan.json>   # or pipe the plan on stdin

A plan is the JSON returned by the github-planner skill. `mode` selects the
schema: `scope` answers single/split/spike/blocked, `implementation` returns
ordered steps.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR: lines

Checks:
    E01 plan not readable or not valid JSON
    E02 missing or invalid mode (scope | implementation)
    E03 scope: missing or invalid verdict (single | split | spike | blocked)
    E04 scope: missing reason
    E05 scope split: subtasks must be a list of 2-6 items
    E06 scope single/spike: subtasks must be empty
    E07 scope blocked: questions must be a non-empty list
    E08 subtask missing or invalid summary
    E09 subtask missing objective
    E10 subtask scope, changes or tests must be non-empty lists of strings
    E11 subtask acceptance must be a non-empty list of AC objects
    E12 subtask type is not a rubric type
    E13 subtask estimate must be 1h, 2h, 3h, 5h or 8h
    E14 subtask dependsOn must list earlier 0-based positions only
    E15 implementation: blocked must be a boolean
    E16 implementation blocked: questions must be non-empty and steps empty
    E17 implementation: steps must be a non-empty list
    E18 step missing title, files, creates or test
    E19 step files and creates must be lists of strings
    W20 step names neither an existing file nor a new one
    W21 step has no test
    W22 objective is longer than three sentences
"""

import argparse
import json
import re
import sys

TYPES = ("Documentación", "Análisis", "Mantenimiento", "Deuda técnica", "Funcionalidad")
ESTIMATES = ("1h", "2h", "3h", "5h", "8h")
VERDICTS = ("single", "split", "spike", "blocked")
SENTENCE_RE = re.compile(r"[.!?]+")


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def is_text_list(value):
    return isinstance(value, list) and bool(value) and all(is_text(v) for v in value)


def sentences(text):
    return [part for part in SENTENCE_RE.split(text) if part.strip()]


def check_subtask(index, subtask, errors, warnings):
    where = f"subtask[{index}]"
    if not isinstance(subtask, dict):
        errors.append(f"ERROR: E08 {where}: must be an object")
        return
    if not is_text(subtask.get("summary")):
        errors.append(f"ERROR: E08 {where}: missing summary")
    objective = subtask.get("objective")
    if not is_text(objective):
        errors.append(f"ERROR: E09 {where}: missing objective")
    elif len(sentences(objective)) > 3:
        warnings.append(f"WARNING: W22 {where}: objective is longer than three sentences")
    for field in ("scope", "changes", "tests"):
        if not is_text_list(subtask.get(field)):
            errors.append(f"ERROR: E10 {where}: {field} must be a non-empty list of strings")
    acceptance = subtask.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        errors.append(f"ERROR: E11 {where}: acceptance must be a non-empty list")
    else:
        for criterion in acceptance:
            if not isinstance(criterion, dict) or not all(
                is_text(criterion.get(key)) for key in ("id", "given", "when", "then")
            ):
                errors.append(
                    f"ERROR: E11 {where}: every acceptance item needs id, given, when and then"
                )
                break
    if subtask.get("type") not in TYPES:
        errors.append(f"ERROR: E12 {where}: invalid type {subtask.get('type')!r}")
    if subtask.get("estimate") not in ESTIMATES:
        errors.append(f"ERROR: E13 {where}: estimate must be one of {', '.join(ESTIMATES)}")
    depends = subtask.get("dependsOn")
    if not isinstance(depends, list) or not all(
        isinstance(d, int) and not isinstance(d, bool) and 0 <= d < index for d in depends
    ):
        errors.append(f"ERROR: E14 {where}: dependsOn must list earlier 0-based positions only")


def check_step(index, step, errors, warnings):
    where = f"step[{index}]"
    if not isinstance(step, dict):
        errors.append(f"ERROR: E18 {where}: must be an object")
        return
    if not is_text(step.get("title")):
        errors.append(f"ERROR: E18 {where}: missing title")
    if not is_text(step.get("test")):
        errors.append(f"ERROR: E18 {where}: missing test")
    for field in ("files", "creates"):
        value = step.get(field)
        if not isinstance(value, list) or not all(is_text(v) for v in value):
            errors.append(f"ERROR: E19 {where}: {field} must be a list of strings")
    files, creates = step.get("files"), step.get("creates")
    if isinstance(files, list) and isinstance(creates, list) and not files and not creates:
        warnings.append(f"WARNING: W20 {where}: names neither an existing file nor a new one")


def check_scope(plan, errors, warnings):
    verdict = plan.get("verdict")
    if verdict not in VERDICTS:
        errors.append(f"ERROR: E03 invalid verdict {verdict!r}")
        return
    if not is_text(plan.get("reason")):
        errors.append("ERROR: E04 missing reason")
    subtasks = plan.get("subtasks", [])
    if not isinstance(subtasks, list):
        errors.append("ERROR: E05 subtasks must be a list")
        return
    if verdict == "split":
        if not 2 <= len(subtasks) <= 6:
            errors.append(f"ERROR: E05 split needs 2-6 subtasks, found {len(subtasks)}")
        for index, subtask in enumerate(subtasks):
            check_subtask(index, subtask, errors, warnings)
    elif subtasks:
        errors.append(f"ERROR: E06 verdict {verdict} must not return subtasks")
    if verdict == "blocked":
        questions = plan.get("questions")
        if not isinstance(questions, list) or not questions or not all(
            is_text(q) for q in questions
        ):
            errors.append("ERROR: E07 blocked needs a non-empty questions list")


def check_implementation(plan, errors, warnings):
    blocked = plan.get("blocked")
    if not isinstance(blocked, bool):
        errors.append("ERROR: E15 blocked must be a boolean")
        return
    steps = plan.get("steps", [])
    questions = plan.get("questions", [])
    if blocked:
        if not isinstance(questions, list) or not questions:
            errors.append("ERROR: E16 blocked needs a non-empty questions list")
        if steps:
            errors.append("ERROR: E16 blocked must not return steps")
        return
    if not isinstance(steps, list) or not steps:
        errors.append("ERROR: E17 steps must be a non-empty list")
        return
    for index, step in enumerate(steps):
        check_step(index, step, errors, warnings)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    args = parser.parse_args()

    try:
        text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    except OSError as e:
        print(f"ERROR: E01 cannot read plan: {e}")
        sys.exit(1)

    try:
        plan = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR: E01 plan is not valid JSON: {e}")
        sys.exit(1)

    if not isinstance(plan, dict):
        print("ERROR: E02 plan must be a JSON object")
        sys.exit(1)

    mode = plan.get("mode")
    if mode not in ("scope", "implementation"):
        print(f"ERROR: E02 invalid mode {mode!r} (expected scope or implementation)")
        sys.exit(1)

    errors, warnings = [], []
    if mode == "scope":
        check_scope(plan, errors, warnings)
    else:
        check_implementation(plan, errors, warnings)

    for warning in warnings:
        print(warning)
    for error in errors:
        print(error)
    if errors:
        sys.exit(1)
    print("OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
