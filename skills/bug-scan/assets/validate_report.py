#!/usr/bin/env python3
"""Validate a bug-scan report (JSON) against assets/bug-scan-report.schema.json.

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
    E03 missing top-level key (schema, date, scan_type, requested_by, commit,
        baseline, coverage, counters, findings, delta)
    E04 schema != 'bug-scan/report@1'
    E05 scan_type not 'global'/'targeted', or targeted without 'scope'
    E06 date is not YYYY-MM-DD
    E07 coverage missing 'reviewed'/'not_reviewed'
    E08 counters disagree with listed (non-fixed) findings
    E09 a finding is missing a field or has an unknown enum value
    E10 delta is missing a counter or its item lists disagree
    E11 unresolved '{...}' placeholder remains in an authored field
    W12 global scan has a 'scope' list
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
    "counters",
    "findings",
    "delta",
)
FINDING_FIELDS = ("title", "severity", "category", "verdict", "status", "location", "scenario")
SEVERITIES = {"Critical", "Major", "Minor"}
CATEGORIES = {"logic", "concurrency", "errors-resources", "data-integrity"}
VERDICTS = {"Confirmed", "Unconfirmed"}
STATUSES = {"new", "persists", "fixed", "regressed"}
LISTED = {"new", "persists", "regressed"}
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
    yield from (report.get(k) for k in ("date", "scan_type", "requested_by", "commit", "baseline"))
    for group in ("reviewed", "not_reviewed"):
        for item in (report.get("coverage") or {}).get(group) or []:
            yield from item.values()
    for finding in report.get("findings") or []:
        for key in ("title", "severity", "category", "verdict", "status", "scenario"):
            yield finding.get(key)
        for value in (finding.get("location") or {}).values():
            yield value
        yield from finding.get("manual_steps") or []
    delta = report.get("delta") or {}
    for key in ("fixed_items", "not_rechecked_items"):
        for item in delta.get(key) or []:
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
    if report.get("schema") != "bug-scan/report@1":
        errors.append("ERROR: E04 schema must be 'bug-scan/report@1'")

    scan_type = report.get("scan_type")
    if scan_type not in ("global", "targeted"):
        errors.append(f"ERROR: E05 scan_type {scan_type!r} not 'global' or 'targeted'")
    scope = report.get("scope")
    if scan_type == "targeted" and not scope:
        errors.append("ERROR: E05 targeted scan requires a non-empty 'scope' list")
    if scan_type == "global" and scope:
        warnings.append("WARNING: W12 global scan has a 'scope' list; remove it")
    if not DATE_RE.match(str(report.get("date", ""))):
        errors.append("ERROR: E06 date is not YYYY-MM-DD")

    coverage = report.get("coverage") or {}
    for group in ("reviewed", "not_reviewed"):
        if not isinstance(coverage.get(group), list):
            errors.append(f"ERROR: E07 coverage missing list '{group}'")

    findings = report.get("findings")
    if not isinstance(findings, list):
        errors.append("ERROR: E03 'findings' must be a list")
        findings = []

    confirmed = unconfirmed = 0
    for finding in findings:
        name = finding.get("title", "?") if isinstance(finding, dict) else "?"
        if not isinstance(finding, dict):
            errors.append(f"ERROR: E09 finding {name!r} is not an object")
            continue
        for key in FINDING_FIELDS:
            if not finding.get(key):
                errors.append(f"ERROR: E09 finding '{name}' missing '{key}'")
        loc = finding.get("location") or {}
        if not loc.get("file") or not isinstance(loc.get("line"), int):
            errors.append(f"ERROR: E09 finding '{name}' location needs file and integer line")
        if finding.get("severity") not in SEVERITIES:
            errors.append(f"ERROR: E09 finding '{name}' severity {finding.get('severity')!r} invalid")
        if finding.get("category") not in CATEGORIES:
            errors.append(f"ERROR: E09 finding '{name}' category {finding.get('category')!r} invalid")
        if finding.get("verdict") not in VERDICTS:
            errors.append(f"ERROR: E09 finding '{name}' verdict {finding.get('verdict')!r} invalid")
        if finding.get("status") not in STATUSES:
            errors.append(f"ERROR: E09 finding '{name}' status {finding.get('status')!r} invalid")
        if finding.get("status") in LISTED:
            if finding.get("verdict") == "Confirmed":
                confirmed += 1
            else:
                unconfirmed += 1

    counters = report.get("counters") or {}
    declared = (counters.get("confirmed"), counters.get("unconfirmed"))
    if declared != (confirmed, unconfirmed):
        errors.append(
            f"ERROR: E08 counters {declared[0]} Confirmed/{declared[1]} Unconfirmed "
            f"but listed findings are {confirmed}/{unconfirmed}"
        )
    if not isinstance(counters.get("discarded"), int):
        errors.append("ERROR: E08 counters.discarded must be an integer")

    delta = report.get("delta") or {}
    for key in ("persists", "fixed", "new", "not_rechecked"):
        if not isinstance(delta.get(key), int):
            errors.append(f"ERROR: E10 delta missing integer '{key}'")
    if isinstance(delta.get("fixed"), int) and delta["fixed"] != len(delta.get("fixed_items") or []):
        errors.append("ERROR: E10 delta.fixed disagrees with delta.fixed_items")
    if isinstance(delta.get("not_rechecked"), int) and delta["not_rechecked"] != len(
        delta.get("not_rechecked_items") or []
    ):
        errors.append("ERROR: E10 delta.not_rechecked disagrees with delta.not_rechecked_items")

    for value in authored_strings(report):
        if isinstance(value, str) and PLACEHOLDER_RE.search(value):
            errors.append(f"ERROR: E11 unresolved placeholder in {value!r}")
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
