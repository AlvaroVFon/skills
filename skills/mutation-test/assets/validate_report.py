#!/usr/bin/env python3
"""Validate a mutation-test report (JSON) against mutation-test-report.schema.json.

Usage:
    validate_report.py --file <report.json>

Reads the report from --file, or stdin if omitted. Exits 0 and prints OK when
the report is structurally valid and its counters agree, otherwise exits 1
printing one concise parseable `ERROR:` line per problem. Warnings do not
change the exit code.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR lines reported

Checks:
    E01 missing/unreadable file
    E02 invalid JSON
    E03 missing top-level key
    E04 schema != 'mutation-test/report@1'
    E05 scan_type invalid or targeted without 'scope'
    E06 date is not YYYY-MM-DD
    E07 coverage missing reviewed/not_reviewed/not_covered
    E08 summary score disagrees with killed/survived
    E09 a survivor finding is missing a field or has an unknown enum value
    E10 summary.survived disagrees with survivor blocks
    E11 delta counter disagrees with its item list
    E12 unresolved '{...}' placeholder remains in an authored field
    W13 by-module Killed/Survived totals disagree with the summary
    W14 global scan has a 'scope' list
"""

import argparse
import json
import re
import sys

TOP_KEYS = (
    "schema",
    "date",
    "scan_type",
    "requested_by",
    "commit",
    "baseline",
    "coverage",
    "summary",
    "by_module",
    "findings",
    "delta",
)
SEVERITIES = {"Critical", "Major", "Minor"}
OPERATORS = {
    "boundary",
    "conditional",
    "logical",
    "arithmetic",
    "statement-removal",
    "return",
    "literal",
    "branch",
    "argument",
}
STATUSES = {"new", "persists", "killed", "regressed"}
SURVIVOR = {"new", "persists", "regressed"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLACEHOLDER_RE = re.compile(r"\{[^{}\n]+\}")


def load(path):
    if path == "-":
        text = sys.stdin.read()
    else:
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            print(f"ERROR: E01 cannot read file: {e}")
            sys.exit(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR: E02 invalid JSON: {e}")
        sys.exit(1)


def authored_strings(report):
    for key in ("date", "scan_type", "requested_by", "commit", "baseline", "target", "cap"):
        yield report.get(key)
    for group in ("reviewed", "not_reviewed", "not_covered"):
        for item in (report.get("coverage") or {}).get(group) or []:
            yield from item.values()
    for row in report.get("by_module") or []:
        yield row.get("module")
    for finding in report.get("findings") or []:
        for key in ("title", "severity", "operator", "status", "gap"):
            yield finding.get(key)
        for value in (finding.get("location") or {}).values():
            yield value
    for key in ("killed_items", "not_rechecked_items"):
        for item in (report.get("delta") or {}).get(key) or []:
            yield from item.values()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="-")
    args = parser.parse_args()
    report = load(args.file)
    errors, warnings = [], []

    if not isinstance(report, dict):
        print("ERROR: E03 report is not a JSON object")
        sys.exit(1)
    for key in TOP_KEYS:
        if key not in report:
            errors.append(f"ERROR: E03 missing top-level key '{key}'")
    if report.get("schema") != "mutation-test/report@1":
        errors.append("ERROR: E04 schema must be 'mutation-test/report@1'")

    scan_type = report.get("scan_type")
    if scan_type not in ("global", "targeted"):
        errors.append(f"ERROR: E05 scan_type {scan_type!r} not 'global' or 'targeted'")
    if scan_type == "targeted" and not report.get("scope"):
        errors.append("ERROR: E05 targeted scan requires a non-empty 'scope' list")
    if scan_type == "global" and report.get("scope"):
        warnings.append("WARNING: W14 global scan has a 'scope' list; remove it")
    if not DATE_RE.match(str(report.get("date", ""))):
        errors.append("ERROR: E06 date is not YYYY-MM-DD")

    coverage = report.get("coverage") or {}
    for group in ("reviewed", "not_reviewed", "not_covered"):
        if not isinstance(coverage.get(group), list):
            errors.append(f"ERROR: E07 coverage missing list '{group}'")

    summary = report.get("summary") or {}
    killed = summary.get("killed")
    survived = summary.get("survived")
    if not isinstance(killed, int) or not isinstance(survived, int):
        errors.append("ERROR: E08 summary killed/survived must be integers")
    else:
        if killed + survived > 0:
            expected = round(killed * 100 / (killed + survived))
            if abs(int(summary.get("score", -1)) - expected) > 1:
                errors.append(
                    f"ERROR: E08 score {summary.get('score')}% but {killed} Killed/{survived} Survived => {expected}%"
                )
        blocks = [
            f
            for f in (report.get("findings") or [])
            if isinstance(f, dict) and f.get("status") in SURVIVOR
        ]
        if len(blocks) != survived:
            errors.append(
                f"ERROR: E10 summary.survived={survived} but {len(blocks)} survivor finding(s)"
            )

    for finding in report.get("findings") or []:
        name = finding.get("title", "?") if isinstance(finding, dict) else "?"
        if not isinstance(finding, dict):
            errors.append(f"ERROR: E09 finding {name!r} is not an object")
            continue
        for key in ("title", "severity", "operator", "status", "location", "gap"):
            if not finding.get(key):
                errors.append(f"ERROR: E09 finding '{name}' missing '{key}'")
        loc = finding.get("location") or {}
        if not loc.get("file") or not isinstance(loc.get("line"), int):
            errors.append(f"ERROR: E09 finding '{name}' location needs file and integer line")
        if finding.get("severity") not in SEVERITIES:
            errors.append(f"ERROR: E09 finding '{name}' severity {finding.get('severity')!r} invalid")
        if finding.get("operator") not in OPERATORS:
            errors.append(f"ERROR: E09 finding '{name}' operator {finding.get('operator')!r} invalid")
        if finding.get("status") not in STATUSES:
            errors.append(f"ERROR: E09 finding '{name}' status {finding.get('status')!r} invalid")

    delta = report.get("delta") or {}
    for key in ("persists", "killed", "new", "not_rechecked"):
        if not isinstance(delta.get(key), int):
            errors.append(f"ERROR: E11 delta missing integer '{key}'")
    if isinstance(delta.get("killed"), int) and delta["killed"] != len(delta.get("killed_items") or []):
        errors.append("ERROR: E11 delta.killed disagrees with delta.killed_items")
    if isinstance(delta.get("not_rechecked"), int) and delta["not_rechecked"] != len(
        delta.get("not_rechecked_items") or []
    ):
        errors.append("ERROR: E11 delta.not_rechecked disagrees with delta.not_rechecked_items")

    rows = report.get("by_module") or []
    if rows and isinstance(killed, int) and isinstance(survived, int):
        mod_killed = sum(r.get("killed", 0) for r in rows)
        mod_survived = sum(r.get("survived", 0) for r in rows)
        if (mod_killed, mod_survived) != (killed, survived):
            warnings.append(
                f"WARNING: W13 by-module totals {mod_killed} Killed/{mod_survived} Survived "
                f"differ from summary {killed}/{survived}"
            )

    for value in authored_strings(report):
        if isinstance(value, str) and PLACEHOLDER_RE.search(value):
            errors.append(f"ERROR: E12 unresolved placeholder in {value!r}")
            break

    for w in warnings:
        print(w)
    for e in errors:
        print(e)
    if errors:
        sys.exit(1)
    print("OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
