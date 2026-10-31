#!/usr/bin/env python3
"""Validate a GitHub triage report table.

Usage:
    validate_triage_report.py --file <report.md>   # or pipe the report on stdin

The report is the markdown table returned by the github-triage skill plus one
totals line:

    | issue | outcome | type | factors | score | estimate | links | reason |
    | --- | --- | --- | --- | --- | --- | --- | --- |
    | owner/repo#12 | triaged | Funcionalidad | 2/5 3/5 1/5 0/5 2/5 1/5 | 9/32 | 3h | - | - |

    Totals: triaged=1 split=0 skipped=0 failed=0

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR: lines

Checks:
    E01 report not readable
    E02 missing table header with the required columns, in order
    E03 data row does not have 8 cells
    E04 invalid issue reference (expected owner/repo#N or #N)
    E05 invalid outcome (triaged | split | skipped | failed)
    E06 invalid type (or a type on a skipped/failed row)
    E07 factors must be six 'n/5' scores, optionally marked 'assumed' with '*'
    E08 score must be 'N/32' with N <= 32
    E09 invalid estimate (1h | 2h | 3h | 5h | 8h | 13h | 21h, or '-' when skipped/failed)
    E10 invalid links cell (expected '-', 'none', or '#N' references)
    E11 missing totals line, or totals do not match the rows
    E12 no data rows
    E13 estimate below the score band (overrides may only raise it)
    W14 estimate above the score band: allowed, but the reason must explain the override
    W15 empty reason on a split/skipped/failed row
"""

import argparse
import re
import sys

COLUMNS = ["issue", "outcome", "type", "factors", "score", "estimate", "links", "reason"]
OUTCOMES = ("triaged", "split", "skipped", "failed")
TYPES = ("Documentación", "Análisis", "Mantenimiento", "Deuda técnica", "Funcionalidad")
ESTIMATES = (1, 2, 3, 5, 8, 13, 21)
SEPARATOR = re.compile(r"^:?-{3,}:?$")
ISSUE_RE = re.compile(r"^(?:[\w.-]+/[\w.-]+)?#\d+$")
FACTOR_RE = re.compile(r"^([0-5])/5(\*?)$")
SCORE_RE = re.compile(r"^(\d{1,2})/32$")
ESTIMATE_RE = re.compile(r"^(\d{1,2})h$")
LINKS_RE = re.compile(r"^(?:-|none|#\d+(?:[\s,]+#\d+)*)$")
TOTALS_RE = re.compile(
    r"^totals:\s*triaged=(\d+),?\s*split=(\d+),?\s*skipped=(\d+),?\s*failed=(\d+)$",
    re.IGNORECASE,
)


def band(score):
    for limit, estimate in ((3, 1), (6, 2), (9, 3), (13, 5), (17, 8), (22, 13)):
        if score <= limit:
            return estimate
    return 21


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    args = parser.parse_args()

    try:
        if args.file:
            text = open(args.file, encoding="utf-8").read()
        else:
            text = sys.stdin.read()
    except OSError as e:
        print(f"ERROR: E01 cannot read report: {e}")
        sys.exit(1)

    errors, warnings = [], []
    header_index = None
    for i, line in enumerate(text.splitlines()):
        if line.strip().startswith("|") and [c.lower() for c in cells(line)] == COLUMNS:
            header_index = i
            break
    if header_index is None:
        print(f"ERROR: E02 missing table header with columns: {' | '.join(COLUMNS)}")
        sys.exit(1)

    rows, totals = [], None
    for line in text.splitlines()[header_index + 1 :]:
        stripped = line.strip()
        if stripped.startswith("|"):
            row = cells(stripped)
            if all(SEPARATOR.match(c) for c in row if c):
                continue
            rows.append((header_index + 2 + len(rows), row))
            continue
        match = TOTALS_RE.match(stripped)
        if match:
            totals = tuple(int(g) for g in match.groups())

    if not rows:
        errors.append("ERROR: E12 report has no data rows")

    counts = {outcome: 0 for outcome in OUTCOMES}
    for line_no, row in rows:
        where = f"line {line_no}"
        if len(row) != len(COLUMNS):
            errors.append(f"ERROR: E03 {where}: expected 8 cells, found {len(row)}")
            continue
        issue, outcome, task_type, factors, score, estimate, links, reason = row

        if not ISSUE_RE.match(issue):
            errors.append(f"ERROR: E04 {where}: invalid issue reference {issue!r}")
        if outcome not in OUTCOMES:
            errors.append(f"ERROR: E05 {where}: invalid outcome {outcome!r}")
        else:
            counts[outcome] += 1
            if outcome == "triaged" and task_type not in TYPES:
                errors.append(f"ERROR: E06 {where}: invalid type {task_type!r}")

        factor_values = [f for f in re.split(r"[\s,]+", factors) if f]
        parsed_factors = [FACTOR_RE.match(f) for f in factor_values]
        if len(factor_values) != 6 or not all(parsed_factors):
            errors.append(
                f"ERROR: E07 {where}: factors must be six 'n/5' scores, found {factors!r}"
            )

        score_match = SCORE_RE.match(score)
        if not score_match or int(score_match.group(1)) > 32:
            errors.append(f"ERROR: E08 {where}: invalid score {score!r}")
            score_value = None
        else:
            score_value = int(score_match.group(1))

        estimate_value = None
        estimate_match = ESTIMATE_RE.match(estimate)
        if estimate in ("-", "none") and outcome in ("skipped", "failed"):
            pass
        elif not estimate_match or int(estimate_match.group(1)) not in ESTIMATES:
            errors.append(f"ERROR: E09 {where}: invalid estimate {estimate!r}")
        else:
            estimate_value = int(estimate_match.group(1))

        if not LINKS_RE.match(links):
            errors.append(f"ERROR: E10 {where}: invalid links cell {links!r}")
        if outcome in ("split", "skipped", "failed") and reason in ("-", "", "none"):
            warnings.append(f"WARNING: W15 {where}: {outcome} row without a reason")

        if score_value is not None and estimate_value is not None:
            expected = band(score_value)
            if estimate_value < expected:
                errors.append(
                    f"ERROR: E13 {where}: estimate {estimate_value}h is below the "
                    f"{expected}h band for score {score_value}"
                )
            elif estimate_value > expected and reason in ("-", "", "none"):
                warnings.append(
                    f"WARNING: W14 {where}: estimate {estimate_value}h above the "
                    f"{expected}h band; explain the override in reason"
                )

    if totals is None:
        errors.append("ERROR: E11 missing 'Totals: triaged=N split=N skipped=N failed=N' line")
    elif totals != tuple(counts[o] for o in OUTCOMES):
        expected = " ".join(f"{o}={counts[o]}" for o in OUTCOMES)
        found = " ".join(f"{o}={v}" for o, v in zip(OUTCOMES, totals))
        errors.append(f"ERROR: E11 totals mismatch: found {found!r}, rows count {expected!r}")

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
