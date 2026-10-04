#!/usr/bin/env python3
"""Validate a module-design brief (JSON) against module-design-brief.schema.json.

Usage:
    validate_brief.py --file <brief.json>

Reads the brief from --file, or stdin if omitted. Exits 0 and prints OK when
the brief is structurally valid and its delta agrees, otherwise exits 1
printing one concise parseable `ERROR:` line per problem. Warnings do not
change the exit code.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR lines reported

Checks:
    E01 missing/unreadable file
    E02 invalid JSON
    E03 missing top-level key
    E04 schema != 'module-design/brief@1'
    E05 date is not YYYY-MM-DD
    E06 depth_verdict macro/micro invalid
    E07 a finding is missing a field or has an unknown enum value
    E08 delta counter disagrees with its item list
    E09 unresolved '{...}' placeholder remains in an authored field
    W10 a finding has neither location nor a module-level justification
"""

import argparse
import json
import re
import sys

TOP_KEYS = (
    "schema",
    "date",
    "requested_by",
    "commit",
    "baseline",
    "module",
    "responsibility",
    "public_interface",
    "depth_verdict",
    "findings",
    "delta",
)
TYPES = {
    "leakage-interface",
    "leakage-back-door",
    "shallow",
    "over-config",
    "temporal-decomposition",
    "improvement",
}
SEVERITIES = {"Critical", "Major", "Minor"}
STATUSES = {"new", "persists", "resolved", "regressed"}
DEPTHS = {"deep", "acceptable", "shallow"}
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


def authored_strings(brief):
    for key in ("date", "requested_by", "commit", "baseline", "module", "language", "responsibility"):
        yield brief.get(key)
    for key in ("hidden_knowledge", "complexity_absorbed"):
        yield from brief.get(key) or []
    for item in brief.get("failure_contract") or []:
        yield from item.values()
    yield from (brief.get("split_merge") or {}).values()
    yield from (brief.get("depth_verdict") or {}).values()
    for finding in brief.get("findings") or []:
        for key in ("type", "title", "severity", "status", "module", "detail"):
            yield finding.get(key)
    for key in ("resolved_items", "not_rechecked_items"):
        for item in (brief.get("delta") or {}).get(key) or []:
            yield from item.values()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="-")
    args = parser.parse_args()
    brief = load(args.file)
    errors, warnings = [], []

    if not isinstance(brief, dict):
        print("ERROR: E03 brief is not a JSON object")
        sys.exit(1)
    for key in TOP_KEYS:
        if key not in brief:
            errors.append(f"ERROR: E03 missing top-level key '{key}'")
    if brief.get("schema") != "module-design/brief@1":
        errors.append("ERROR: E04 schema must be 'module-design/brief@1'")
    if not DATE_RE.match(str(brief.get("date", ""))):
        errors.append("ERROR: E05 date is not YYYY-MM-DD")

    depth = brief.get("depth_verdict") or {}
    for level in ("macro", "micro"):
        if depth.get(level) not in DEPTHS:
            errors.append(f"ERROR: E06 depth_verdict.{level} {depth.get(level)!r} not deep/acceptable/shallow")

    for finding in brief.get("findings") or []:
        name = finding.get("title", "?") if isinstance(finding, dict) else "?"
        if not isinstance(finding, dict):
            errors.append(f"ERROR: E07 finding {name!r} is not an object")
            continue
        for key in ("type", "title", "severity", "status", "module", "detail"):
            if not finding.get(key):
                errors.append(f"ERROR: E07 finding '{name}' missing '{key}'")
        if finding.get("type") not in TYPES:
            errors.append(f"ERROR: E07 finding '{name}' type {finding.get('type')!r} invalid")
        if finding.get("severity") not in SEVERITIES:
            errors.append(f"ERROR: E07 finding '{name}' severity {finding.get('severity')!r} invalid")
        if finding.get("status") not in STATUSES:
            errors.append(f"ERROR: E07 finding '{name}' status {finding.get('status')!r} invalid")
        if not finding.get("location") and not finding.get("module"):
            warnings.append(f"WARNING: W10 finding '{name}' has no location and no module")

    delta = brief.get("delta") or {}
    for key in ("persists", "resolved", "new", "not_rechecked"):
        if not isinstance(delta.get(key), int):
            errors.append(f"ERROR: E08 delta missing integer '{key}'")
    if isinstance(delta.get("resolved"), int) and delta["resolved"] != len(delta.get("resolved_items") or []):
        errors.append("ERROR: E08 delta.resolved disagrees with delta.resolved_items")
    if isinstance(delta.get("not_rechecked"), int) and delta["not_rechecked"] != len(
        delta.get("not_rechecked_items") or []
    ):
        errors.append("ERROR: E08 delta.not_rechecked disagrees with delta.not_rechecked_items")

    for value in authored_strings(brief):
        if isinstance(value, str) and PLACEHOLDER_RE.search(value):
            errors.append(f"ERROR: E09 unresolved placeholder in {value!r}")
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
