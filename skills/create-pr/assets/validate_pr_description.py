#!/usr/bin/env python3
"""Validate a PR description body against the standardized create-pr template.

Usage:
    validate_pr_description.py --body <file> [--title "<title>"]

Reads the body from <file> (or stdin if omitted). Exits 0 when all required
checks pass and prints OK, otherwise exits 1 printing one concise parseable
`ERROR:` line per problem. Warnings do not change the exit code.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR lines reported

Checks:
    E01 Missing required section
    E02 Required section present but empty
    E03 Optional validation section missing
    E04 Items under 'Changes' are not bullet list entries
    E05 Title exceeds 72 characters
"""

import argparse
import re
import sys

TITLE_MAX = 72
REQUIRED_SECTIONS = ("Objective", "Changes")
OPTIONAL_SECTIONS = ("Validation", "Risks")


def parse_sections(body):
    sections, current = {}, None
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+)", line)
        if m:
            current = m.group(1).strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", default="-")
    parser.add_argument("--title")
    args = parser.parse_args()

    body = sys.stdin.read() if args.body == "-" else open(args.body, encoding="utf-8").read()

    errors, warnings = [], []
    sections = parse_sections(body)

    for name in REQUIRED_SECTIONS:
        if name not in sections:
            errors.append(f"ERROR: E01 missing required section '## {name}'")
        elif not any(s.strip() for s in sections[name]):
            errors.append(f"ERROR: E02 required section '## {name}' is present but empty")

    if "Validation" not in sections:
        warnings.append("WARNING: E03 optional section '## Validation' missing")

    for line in sections.get("Changes", []):
        if line.strip() and not line.strip().startswith("- "):
            errors.append(f"ERROR: E04 item under 'Changes' is not a bullet: {line.strip()!r}")

    if args.title and len(args.title) > TITLE_MAX:
        errors.append(f"ERROR: E05 title exceeds {TITLE_MAX} chars ({len(args.title)})")

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