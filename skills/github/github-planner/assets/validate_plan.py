#!/usr/bin/env python3
"""Validate a github-planner assessment.

Usage:
    validate_plan.py --file <plan.json>   # or pipe the plan on stdin

A plan is the JSON returned by the github-planner skill. It always has
`mode: "scope"` and a verdict: `single` returns one deliverable, `split`
returns 2-6, `spike` and `blocked` return none.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR: lines

Checks:
    E01 plan not readable or not valid JSON
    E02 missing or invalid mode (scope)
    E03 missing or invalid verdict (single | split | spike | blocked)
    E04 missing reason
    E05 deliverable count does not match the verdict
    E06 deliverable missing or invalid summary
    E07 deliverable missing objective
    E08 deliverable scope, changes or tests must be non-empty lists of strings
    E09 deliverable acceptance must be a non-empty list of AC objects
    E10 deliverable type is not a rubric type
    E11 deliverable estimate is not a rubric estimate
    E12 split deliverable estimate exceeds 8h
    E13 deliverable dependsOn must list earlier 0-based positions only
    E14 blocked needs a non-empty questions list
    E15 deliverable files must be a non-empty list of repository paths
    E16 deliverable estimatedLines must be a non-negative integer
    E17 split deliverable estimatedLines exceeds 500
    W15 single deliverable above 8h: explain it in reason
    W16 objective is longer than three sentences
    W18 single deliverable above 500 estimated lines: explain it in reason
"""

import argparse
import json
import re
import sys

TYPES = ("Documentación", "Análisis", "Mantenimiento", "Deuda técnica", "Funcionalidad")
ESTIMATES = ("1h", "2h", "3h", "5h", "8h", "13h", "21h")
SPLIT_ESTIMATES = ("1h", "2h", "3h", "5h", "8h")
VERDICTS = ("single", "split", "spike", "blocked")
SENTENCE_RE = re.compile(r"[.!?]+")


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def is_text_list(value):
    return isinstance(value, list) and bool(value) and all(is_text(v) for v in value)


def sentences(text):
    return [part for part in SENTENCE_RE.split(text) if part.strip()]


def check_deliverable(index, deliverable, verdict, errors, warnings):
    where = f"deliverable[{index}]"
    if not isinstance(deliverable, dict):
        errors.append(f"ERROR: E06 {where}: must be an object")
        return
    if not is_text(deliverable.get("summary")):
        errors.append(f"ERROR: E06 {where}: missing summary")
    objective = deliverable.get("objective")
    if not is_text(objective):
        errors.append(f"ERROR: E07 {where}: missing objective")
    elif len(sentences(objective)) > 3:
        warnings.append(f"WARNING: W16 {where}: objective is longer than three sentences")
    for field in ("scope", "changes", "tests"):
        if not is_text_list(deliverable.get(field)):
            errors.append(f"ERROR: E08 {where}: {field} must be a non-empty list of strings")
    files = deliverable.get("files")
    if not is_text_list(files):
        errors.append(f"ERROR: E15 {where}: files must be a non-empty list of repository paths")
    else:
        unsafe = [p for p in files if p.startswith("/") or ".." in p.split("/")]
        if unsafe:
            errors.append(
                f"ERROR: E15 {where}: files must be repository-relative paths, found {unsafe!r}"
            )
    estimated_lines = deliverable.get("estimatedLines")
    if (
        not isinstance(estimated_lines, int)
        or isinstance(estimated_lines, bool)
        or estimated_lines < 0
    ):
        errors.append(
            f"ERROR: E16 {where}: estimatedLines must be a non-negative integer"
        )
    elif verdict == "split" and estimated_lines > 500:
        errors.append(
            f"ERROR: E17 {where}: split deliverable estimates {estimated_lines} lines; split it below 500"
        )
    elif verdict == "single" and estimated_lines > 500:
        warnings.append(
            f"WARNING: W18 {where}: single deliverable estimates {estimated_lines} lines; explain it in reason"
        )
    acceptance = deliverable.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        errors.append(f"ERROR: E09 {where}: acceptance must be a non-empty list")
    else:
        for criterion in acceptance:
            if not isinstance(criterion, dict) or not all(
                is_text(criterion.get(key)) for key in ("id", "given", "when", "then")
            ):
                errors.append(
                    f"ERROR: E09 {where}: every acceptance item needs id, given, when and then"
                )
                break
    if deliverable.get("type") not in TYPES:
        errors.append(f"ERROR: E10 {where}: invalid type {deliverable.get('type')!r}")
    estimate = deliverable.get("estimate")
    if estimate not in ESTIMATES:
        errors.append(f"ERROR: E11 {where}: estimate must be one of {', '.join(ESTIMATES)}")
    elif verdict == "split" and estimate not in SPLIT_ESTIMATES:
        errors.append(f"ERROR: E12 {where}: split deliverables must be 8h or less")
    elif verdict == "single" and estimate not in SPLIT_ESTIMATES:
        warnings.append(f"WARNING: W15 {where}: single deliverable above 8h; explain it in reason")
    depends = deliverable.get("dependsOn")
    if not isinstance(depends, list) or not all(
        isinstance(d, int) and not isinstance(d, bool) and 0 <= d < index for d in depends
    ):
        errors.append(f"ERROR: E13 {where}: dependsOn must list earlier 0-based positions only")


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

    errors, warnings = [], []

    if plan.get("mode") != "scope":
        print(f"ERROR: E02 invalid mode {plan.get('mode')!r} (expected scope)")
        sys.exit(1)

    verdict = plan.get("verdict")
    if verdict not in VERDICTS:
        print(f"ERROR: E03 invalid verdict {verdict!r}")
        sys.exit(1)

    if not is_text(plan.get("reason")):
        errors.append("ERROR: E04 missing reason")

    deliverables = plan.get("deliverables", [])
    if not isinstance(deliverables, list):
        errors.append("ERROR: E05 deliverables must be a list")
        deliverables = []
    else:
        expected = {"single": 1, "spike": 0, "blocked": 0}
        if verdict == "split":
            if not 2 <= len(deliverables) <= 6:
                errors.append(f"ERROR: E05 split needs 2-6 deliverables, found {len(deliverables)}")
        elif len(deliverables) != expected[verdict]:
            errors.append(
                f"ERROR: E05 verdict {verdict} needs {expected[verdict]} deliverable(s), "
                f"found {len(deliverables)}"
            )
        for index, deliverable in enumerate(deliverables):
            check_deliverable(index, deliverable, verdict, errors, warnings)

    if verdict == "blocked":
        questions = plan.get("questions")
        if not isinstance(questions, list) or not questions or not all(
            is_text(q) for q in questions
        ):
            errors.append("ERROR: E14 blocked needs a non-empty questions list")

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
