#!/usr/bin/env python3
"""Validate a commit subject against the Conventional Commits format.

Usage:
    validate_commit_message.py [--message "<subject>"]
                                [--file <path>]

Reads the message from --message, or from --file, or from stdin if neither is
given. Exits 0 and prints OK when the subject is valid, otherwise exits 1
printing one concise parseable `ERROR:` line per problem. Warnings do not
change the exit code.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR lines reported

Checks:
    E01 Subject does not match 'type(scope): subject'
    E02 Type is not an allowed Conventional Commits type
    E03 Scope missing, contains spaces, or exceeds 40 chars
    E04 Subject part empty
    E05 Full subject exceeds 72 characters
    W06 Subject starts with uppercase letter (imperative style)
    W07 Subject ends with a trailing period
"""

import argparse
import re
import sys

SUBJECT_MAX = 72
SCOPE_MAX = 40
VALID_TYPES = (
    "feat", "fix", "refactor", "perf", "test",
    "docs", "chore", "ci", "style", "build",
)

PATTERN = re.compile(r"^(?P<type>[a-z][a-z0-9]*)"     # type
                     r"\((?P<scope>[^()\s]*)\)"        # scope (required)
                     r":\s+(?P<subject>.+)$", re.DOTALL)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--message")
    parser.add_argument("--file")
    args = parser.parse_args()

    if args.message is not None:
        subject = args.message
    elif args.file:
        subject = open(args.file, encoding="utf-8").read().strip()
    else:
        subject = sys.stdin.read().strip()

    subject = subject.strip().replace("\n", " ").replace("  ", " ")
    errors, warnings = [], []

    m = PATTERN.match(subject)
    if not m:
        errors.append("ERROR: E01 subject does not match 'type(scope): subject', "
                      f"got {subject!r}")
        for line in errors:
            print(line)
        sys.exit(1)

    ctype, scope, csubject = m.group("type"), m.group("scope"), m.group("subject")

    if ctype not in VALID_TYPES:
        errors.append(f"ERROR: E02 type {ctype!r} not allowed; "
                      f"valid types: {', '.join(VALID_TYPES)}")

    if not scope:
        errors.append("ERROR: E03 scope is required, e.g. feat(auth): ...")
    elif any(c.isspace() for c in scope):
        errors.append(f"ERROR: E03 scope must not contain spaces, got {scope!r}")
    elif len(scope) > SCOPE_MAX:
        errors.append(f"ERROR: E03 scope exceeds {SCOPE_MAX} chars ({len(scope)})")

    if not csubject.strip():
        errors.append("ERROR: E04 subject part is empty after ': '")

    if len(subject) > SUBJECT_MAX:
        errors.append(f"ERROR: E05 subject exceeds {SUBJECT_MAX} chars ({len(subject)})")

    if csubject[0:1].isupper():
        warnings.append(f"WARNING: W06 subject starts with uppercase; "
                        "use lowercase imperative, e.g. 'add ...'")
    if csubject.rstrip().endswith("."):
        warnings.append("WARNING: W07 subject ends with a trailing period")

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