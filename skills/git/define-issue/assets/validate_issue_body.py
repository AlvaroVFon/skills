#!/usr/bin/env python3
"""Validate a GitHub issue body written by the define-issue skill.

Usage:
    validate_issue_body.py --body <file> [--title "<title>"]   # body may also come from stdin

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR: lines

Checks:
    E01 body not readable
    E02 first non-empty line must be AI_GENERATED
    E03 missing required section
    E04 required section present but empty
    E05 Criterios de Aceptación has no '### AC-<n>' heading
    E06 an acceptance criterion is missing Dado, Cuando or Entonces
    E07 title empty or longer than 72 characters
    E08 unresolved placeholder (TODO, TBD, FIXME, <...>, {{...}} or a bracketed AC title)
    W09 Objetivo is longer than three sentences
"""

import argparse
import re
import sys

SECTIONS = ("Objetivo", "Descripción", "Criterios de Aceptación")
TITLE_MAX = 72
PLACEHOLDER_RE = re.compile(r"(?i)\b(TODO|TBD|FIXME)\b|<[^>\n]{2,}>|\{\{[^}\n]+\}\}")
AC_HEADING_RE = re.compile(r"^###\s+AC-(\d+)\b(.*)$")
AC_PLACEHOLDER_RE = re.compile(r"\[[^\]\n]+\]\s*$")


def parse_sections(text):
    sections, current = {}, None
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1)
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--body")
    parser.add_argument("--title")
    args = parser.parse_args()

    try:
        body = open(args.body, encoding="utf-8").read() if args.body else sys.stdin.read()
    except OSError as e:
        print(f"ERROR: E01 cannot read body: {e}")
        sys.exit(1)

    errors, warnings = [], []
    lines = body.splitlines()

    first = next((line.strip() for line in lines if line.strip()), "")
    if first != "AI_GENERATED":
        errors.append("ERROR: E02 first non-empty line must be AI_GENERATED")

    if args.title is not None:
        title = args.title.strip()
        if not title:
            errors.append("ERROR: E07 title is empty")
        elif len(title) > TITLE_MAX:
            errors.append(f"ERROR: E07 title is {len(title)} chars (max {TITLE_MAX})")

    sections = parse_sections(body)
    for name in SECTIONS:
        if name not in sections:
            errors.append(f"ERROR: E03 missing required section '## {name}'")
        elif not any(line.strip() for line in sections[name]):
            errors.append(f"ERROR: E04 required section '## {name}' is present but empty")

    criteria = sections.get("Criterios de Aceptación", [])
    heading_indexes = []
    for index, line in enumerate(criteria):
        match = AC_HEADING_RE.match(line.strip())
        if match:
            heading_indexes.append(index)
            if AC_PLACEHOLDER_RE.search(match.group(2).strip()):
                errors.append(f"ERROR: E08 AC-{match.group(1)} title is still a placeholder")

    if not heading_indexes:
        errors.append("ERROR: E05 Criterios de Aceptación has no '### AC-<n>' heading")
    else:
        for position, start in enumerate(heading_indexes):
            end = heading_indexes[position + 1] if position + 1 < len(heading_indexes) else len(criteria)
            block = "\n".join(criteria[start + 1 : end]).lower()
            missing = [word for word in ("Dado", "Cuando", "Entonces") if word.lower() not in block]
            if missing:
                errors.append("ERROR: E06 AC block is missing " + ", ".join(missing))

    for number, line in enumerate(lines, start=1):
        match = PLACEHOLDER_RE.search(line)
        if match:
            errors.append(f"ERROR: E08 line {number}: unresolved placeholder {match.group(0)!r}")

    objective = " ".join(sections.get("Objetivo", []))
    sentences = [s for s in re.split(r"[.!?]+", objective) if s.strip()]
    if len(sentences) > 3:
        warnings.append(f"WARNING: W09 Objetivo has {len(sentences)} sentences (max 3)")

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
