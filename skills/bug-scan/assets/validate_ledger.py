#!/usr/bin/env python3
"""Validate a bug-scan ledger against assets/bug-scan-ledger.schema.json.

Usage:
    validate_ledger.py --file <ledger.json>

Reads the ledger from --file, or stdin if omitted. Exits 0 and prints OK when
valid, otherwise exits 1 printing one parseable `ERROR:` line per problem.
Warnings do not change the exit code.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR lines reported

Checks:
    E01 missing/unreadable file
    E02 invalid JSON
    E03 missing top-level key (version, skill, repo, updated, entries)
    E04 version/skill mismatch
    E05 updated is not YYYY-MM-DD
    E06 entry missing a required field
    E07 entry enum field has an unknown value
    E08 duplicate entry id
    E09 status/fixed field coherence
    W10 open entry has no 'evidence'
"""

import argparse
import json
import re
import sys

REQUIRED = ("version", "skill", "repo", "updated", "entries")
ENTRY_REQUIRED = (
    "id",
    "kind",
    "title",
    "severity",
    "category",
    "status",
    "location",
    "first_seen",
    "last_seen",
    "commit",
)
ENUMS = {
    "severity": {"Critical", "Major", "Minor"},
    "category": {"logic", "concurrency", "errors-resources", "data-integrity"},
    "status": {"open", "fixed", "regressed", "stale", "wontfix"},
    "verdict": {"Confirmed", "Unconfirmed"},
}
OPEN = {"open", "regressed", "stale"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="-")
    args = parser.parse_args()
    data = load(args.file)

    errors, warnings = [], []

    if not isinstance(data, dict):
        print("ERROR: E03 ledger is not a JSON object")
        sys.exit(1)
    for key in REQUIRED:
        if key not in data:
            errors.append(f"ERROR: E03 missing top-level key '{key}'")
    if data.get("version") != 1:
        errors.append("ERROR: E04 version must be 1")
    if data.get("skill") != "bug-scan":
        errors.append("ERROR: E04 skill must be 'bug-scan'")
    if not DATE_RE.match(str(data.get("updated", ""))):
        errors.append("ERROR: E05 'updated' is not YYYY-MM-DD")

    seen = set()
    for i, entry in enumerate(data.get("entries", [])):
        if not isinstance(entry, dict):
            errors.append(f"ERROR: E06 entry #{i} is not an object")
            continue
        eid = entry.get("id", f"#{i}")
        for key in ENTRY_REQUIRED:
            if not entry.get(key) and entry.get(key) != 0:
                errors.append(f"ERROR: E06 entry {eid} missing '{key}'")
        if entry.get("kind") != "bug":
            errors.append(f"ERROR: E07 entry {eid} kind must be 'bug'")
        for field, allowed in ENUMS.items():
            value = entry.get(field)
            if field == "verdict" and value is None:
                continue
            if value not in allowed:
                errors.append(f"ERROR: E07 entry {eid} {field} {value!r} not in {sorted(allowed)}")
        loc = entry.get("location") or {}
        if not loc.get("file") or not isinstance(loc.get("line"), int):
            errors.append(f"ERROR: E06 entry {eid} location needs file and integer line")
        if entry.get("id") in seen:
            errors.append(f"ERROR: E08 duplicate entry id {eid}")
        seen.add(entry.get("id"))
        status = entry.get("status")
        if status in OPEN and not entry.get("evidence"):
            warnings.append(f"WARNING: W10 open entry {eid} has no 'evidence'")
        if status in OPEN and entry.get("fixed_at"):
            errors.append(f"ERROR: E09 entry {eid} is {status} but has 'fixed_at'")
        if status == "fixed" and not entry.get("fixed_at"):
            errors.append(f"ERROR: E09 entry {eid} is fixed but 'fixed_at' is empty")

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
