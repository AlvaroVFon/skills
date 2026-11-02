#!/usr/bin/env python3
"""Validate a code review bot report.

Usage:
    validate_review_report.py --file <report.json>   # or pipe the report on stdin

The report is the JSON artifact produced by prepare_review.py and described by
review-report.schema.json.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR: lines

Checks:
    E01 report not readable
    E02 report is not a JSON object
    E03 missing required top-level key
    E04 invalid schema_version
    E05 invalid repo
    E06 invalid pr
    E07 invalid url
    E08 invalid head_sha or base_sha
    E09 invalid verdict
    E10 invalid event, or APPROVE used
    E11 invalid review_id
    E12 exit_code does not match the verdict
    E13 dry_run or stale is not a boolean
    E14 invalid counts object
    E15 invalid policy object
    E16 invalid skipped entry
    E17 invalid finding
    E18 severity counts do not match findings
    E19 status counts do not match findings
    E20 discarded count does not match discarded entries
    E21 invalid discarded entry
    E22 verdict does not match findings/skip_reason/errors
    E23 event does not match the verdict and blocking_gate
    E24 invalid skip_reason
    E25 invalid config_warnings or errors entry
    E26 invalid check_run fields
    W27 unknown top-level key
"""

import argparse
import json
import re
import sys

SEVERITIES = ("blocking", "should", "nit")
STATUSES = ("inline", "file", "summary", "deduped", "truncated")
VERDICTS = ("clean", "findings", "blocking", "skipped", "error")
REQUIRED = (
    "schema_version",
    "generated_at",
    "repo",
    "pr",
    "url",
    "head_sha",
    "base_sha",
    "verdict",
    "event",
    "review_id",
    "exit_code",
    "dry_run",
    "stale",
    "counts",
    "skipped",
    "findings",
    "discarded",
    "config_warnings",
    "errors",
)
ALLOWED = set(REQUIRED) | {
    "skip_reason",
    "policy",
    "check_run_id",
    "check_run_url",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REPO_RE = re.compile(r"^[^/\s]+/[^/\s]+$")
URL_RE = re.compile(r"^https?://")
FP_RE = re.compile(r"^[0-9a-f]{12}$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def non_empty(value):
    return isinstance(value, str) and bool(value.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    args = parser.parse_args()

    try:
        if args.file:
            with open(args.file, encoding="utf-8") as handle:
                report = json.load(handle)
        else:
            report = json.loads(sys.stdin.read())
    except OSError as exc:
        print(f"ERROR: E01 cannot read report: {exc}")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: E02 report is not valid JSON: {exc}")
        sys.exit(1)

    errors, warnings = [], []
    if not isinstance(report, dict):
        print("ERROR: E02 report must be a JSON object")
        sys.exit(1)

    for key in REQUIRED:
        if key not in report:
            errors.append(f"ERROR: E03 missing required key {key!r}")
    for key in sorted(set(report) - ALLOWED):
        warnings.append(f"WARNING: W27 unknown top-level key {key!r}")

    if report.get("schema_version") != "1.0":
        errors.append(f"ERROR: E04 schema_version must be '1.0', found {report.get('schema_version')!r}")

    if not ISO_RE.match(str(report.get("generated_at", ""))):
        errors.append(f"ERROR: E04 generated_at must be an ISO-8601 UTC timestamp, found {report.get('generated_at')!r}")

    if not REPO_RE.match(str(report.get("repo", ""))):
        errors.append(f"ERROR: E05 repo must be owner/name, found {report.get('repo')!r}")

    if not is_int(report.get("pr")) or report.get("pr", 0) <= 0:
        errors.append(f"ERROR: E06 pr must be a positive integer, found {report.get('pr')!r}")

    if not URL_RE.match(str(report.get("url", ""))):
        errors.append(f"ERROR: E07 url must start with http(s)://, found {report.get('url')!r}")

    for key in ("head_sha", "base_sha"):
        if not SHA_RE.match(str(report.get(key, ""))):
            errors.append(f"ERROR: E08 {key} must be 40 lowercase hex characters, found {report.get(key)!r}")

    verdict = report.get("verdict")
    if verdict not in VERDICTS:
        errors.append(f"ERROR: E09 invalid verdict {verdict!r}")

    event = report.get("event")
    if event == "APPROVE":
        errors.append("ERROR: E10 APPROVE is forbidden for the bot")
    elif event not in ("COMMENT", "REQUEST_CHANGES", None):
        errors.append(f"ERROR: E10 invalid event {event!r}")

    review_id = report.get("review_id")
    if review_id is not None and (not is_int(review_id) or review_id <= 0):
        errors.append(f"ERROR: E11 review_id must be null or a positive integer, found {review_id!r}")

    exit_code = report.get("exit_code")
    expected_exit = {"error": 2, "blocking": 1}.get(verdict, 0)
    if not is_int(exit_code) or exit_code != expected_exit:
        errors.append(
            f"ERROR: E12 exit_code must be {expected_exit} for verdict {verdict!r}, "
            f"found {exit_code!r}"
        )

    for key in ("dry_run", "stale"):
        if not isinstance(report.get(key), bool):
            errors.append(f"ERROR: E13 {key} must be a boolean")

    counts = report.get("counts")
    count_keys = SEVERITIES + STATUSES + ("discarded",)
    if not isinstance(counts, dict):
        errors.append("ERROR: E14 counts must be an object")
        counts = {}
    else:
        for key in count_keys:
            if key not in counts:
                errors.append(f"ERROR: E14 counts is missing {key!r}")
            elif not is_int(counts[key]) or counts[key] < 0:
                errors.append(f"ERROR: E14 counts.{key} must be a non-negative integer")
        for key in sorted(set(counts) - set(count_keys)):
            warnings.append(f"WARNING: W27 unknown counts key {key!r}")

    policy = report.get("policy")
    if not isinstance(policy, dict):
        errors.append("ERROR: E15 policy must be an object")
        policy = {}
    else:
        if not isinstance(policy.get("blocking_gate"), bool):
            errors.append("ERROR: E15 policy.blocking_gate must be a boolean")
        severities = policy.get("inline_severities")
        if (
            not isinstance(severities, list)
            or not severities
            or any(item not in SEVERITIES for item in severities)
            or len(set(severities)) != len(severities)
        ):
            errors.append(
                "ERROR: E15 policy.inline_severities must be a non-empty unique "
                "list of blocking|should|nit"
            )
        if not non_empty(policy.get("language")):
            errors.append("ERROR: E15 policy.language must be a non-empty string")

    skipped = report.get("skipped")
    if not isinstance(skipped, list):
        errors.append("ERROR: E16 skipped must be a list")
        skipped = []
    else:
        for index, item in enumerate(skipped):
            if (
                not isinstance(item, dict)
                or not non_empty(item.get("path"))
                or not non_empty(item.get("reason"))
            ):
                errors.append(f"ERROR: E16 skipped[{index}] must have non-empty path and reason")

    findings = report.get("findings")
    if not isinstance(findings, list):
        errors.append("ERROR: E17 findings must be a list")
        findings = []
    else:
        for index, item in enumerate(findings):
            where = f"findings[{index}]"
            if not isinstance(item, dict):
                errors.append(f"ERROR: E17 {where} must be an object")
                continue
            if not FP_RE.match(str(item.get("fingerprint", ""))):
                errors.append(f"ERROR: E17 {where}.fingerprint must be 12 lowercase hex characters")
            if item.get("severity") not in SEVERITIES:
                errors.append(f"ERROR: E17 {where}.severity is invalid")
            if not non_empty(item.get("path")):
                errors.append(f"ERROR: E17 {where}.path must be non-empty")
            line = item.get("line")
            if line is not None and (not is_int(line) or line <= 0):
                errors.append(f"ERROR: E17 {where}.line must be null or a positive integer")
            side = item.get("side")
            if side not in ("RIGHT", "LEFT"):
                errors.append(f"ERROR: E17 {where}.side must be RIGHT or LEFT")
            start_line = item.get("start_line")
            if start_line is not None and (not is_int(start_line) or start_line <= 0):
                errors.append(f"ERROR: E17 {where}.start_line must be null or a positive integer")
            if is_int(line) and is_int(start_line) and start_line > line:
                errors.append(f"ERROR: E17 {where}.start_line cannot exceed line")
            if not non_empty(item.get("rule")):
                errors.append(f"ERROR: E17 {where}.rule must be non-empty")
            if item.get("confidence") not in ("high", "medium", "low"):
                errors.append(f"ERROR: E17 {where}.confidence is invalid")
            status = item.get("status")
            if status not in STATUSES:
                errors.append(f"ERROR: E17 {where}.status is invalid")
            if status == "inline" and not is_int(line):
                errors.append(f"ERROR: E17 {where} is inline but has no line")
            if not non_empty(item.get("body")):
                errors.append(f"ERROR: E17 {where}.body must be non-empty")

    for severity in SEVERITIES:
        actual = sum(1 for item in findings if item.get("severity") == severity)
        if counts.get(severity) != actual:
            errors.append(
                f"ERROR: E18 counts.{severity} is {counts.get(severity)!r}, "
                f"but findings contain {actual}"
            )

    for status in STATUSES:
        actual = sum(1 for item in findings if item.get("status") == status)
        if counts.get(status) != actual:
            errors.append(
                f"ERROR: E19 counts.{status} is {counts.get(status)!r}, "
                f"but findings contain {actual}"
            )

    discarded = report.get("discarded")
    if not isinstance(discarded, list):
        errors.append("ERROR: E21 discarded must be a list")
        discarded = []
    else:
        for index, item in enumerate(discarded):
            if (
                not isinstance(item, dict)
                or not non_empty(item.get("path"))
                or (item.get("line") is not None and (not is_int(item.get("line")) or item.get("line") <= 0))
                or not non_empty(item.get("reason"))
            ):
                errors.append(
                    f"ERROR: E21 discarded[{index}] must have path, optional positive line and reason"
                )
    if counts.get("discarded") != len(discarded):
        errors.append(
            f"ERROR: E20 counts.discarded is {counts.get('discarded')!r}, "
            f"but discarded has {len(discarded)} entries"
        )

    skip_reason = report.get("skip_reason")
    if skip_reason is not None and not non_empty(skip_reason):
        errors.append("ERROR: E24 skip_reason must be null or a non-empty string")

    if verdict == "error":
        if not report.get("errors"):
            errors.append("ERROR: E22 verdict 'error' requires at least one errors entry")
    elif report.get("errors"):
        errors.append("ERROR: E22 errors must be empty unless verdict is 'error'")

    if verdict == "skipped":
        if not non_empty(skip_reason):
            errors.append("ERROR: E22 verdict 'skipped' requires a skip_reason")
        if findings:
            errors.append("ERROR: E22 verdict 'skipped' cannot contain findings")
    elif verdict is not None and skip_reason is not None:
        errors.append("ERROR: E22 skip_reason must be null unless verdict is 'skipped'")

    if verdict in ("clean", "findings", "blocking"):
        blocking = counts.get("blocking", 0)
        others = counts.get("should", 0) + counts.get("nit", 0)
        if verdict == "clean" and (blocking or others):
            errors.append("ERROR: E22 verdict 'clean' requires zero findings")
        if verdict == "findings" and (blocking or not others):
            errors.append("ERROR: E22 verdict 'findings' requires zero blocking and at least one should/nit")
        if verdict == "blocking" and not blocking:
            errors.append("ERROR: E22 verdict 'blocking' requires at least one blocking finding")

    if verdict in ("error", "skipped"):
        if event is not None:
            errors.append(f"ERROR: E23 event must be null for verdict {verdict!r}")
    elif verdict == "blocking" and policy.get("blocking_gate") is True:
        if event != "REQUEST_CHANGES":
            errors.append("ERROR: E23 blocking verdict with blocking_gate requires REQUEST_CHANGES")
    elif event != "COMMENT":
        errors.append(f"ERROR: E23 event must be COMMENT for verdict {verdict!r}")

    for key in ("config_warnings", "errors"):
        values = report.get(key)
        if not isinstance(values, list):
            errors.append(f"ERROR: E25 {key} must be a list")
            continue
        for index, value in enumerate(values):
            if not non_empty(value):
                errors.append(f"ERROR: E25 {key}[{index}] must be a non-empty string")

    check_run_id = report.get("check_run_id")
    check_run_url = report.get("check_run_url")
    if check_run_id is not None and (not is_int(check_run_id) or check_run_id <= 0):
        errors.append("ERROR: E26 check_run_id must be null or a positive integer")
    if check_run_url is not None and not non_empty(check_run_url):
        errors.append("ERROR: E26 check_run_url must be null or a non-empty string")

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
