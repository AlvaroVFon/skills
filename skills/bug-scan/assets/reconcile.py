#!/usr/bin/env python3
"""Reconcile a bug-scan report against the previous report and write its delta.

Usage:
    reconcile.py --report <report.json> [--docs docs/bug-scan] [--repo-root <dir>]

Finds the baseline report in --docs (or honors report["baseline"] when it points
to an existing file), assigns each finding a stable id, and writes the ids plus
the computed `delta` back into the report JSON. The dated report is the only
artifact: there is no ledger and no rendered file.

Exit codes:
    0  report reconciled
    1  one or more `ERROR:` lines reported (nothing written)

Checks:
    E01 cannot read/write a file
    E02 report is not valid JSON or lacks required keys
    E03 finding lacks title/severity/category/status/location
    E04 unknown finding status
    E05 baseline is not a bug-scan report
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

SPEC = {
    "skill": "bug-scan",
    "report_schema": "bug-scan/report@1",
    "docs": "docs/bug-scan",
    "kind": "bug",
    "discriminator": "category",
    "open": ["new", "persists", "regressed"],
    "closed": ["fixed"],
    "report_closed": "fixed",
    "delta_closed": "fixed",
    "delta_closed_label": "fixed",
    "delta_closed_items": "fixed_items",
    "location_required": True,
    "baseline_match_module": False,
}


def die(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except OSError as e:
        die(f"E01 cannot read {path}: {e}")
    except json.JSONDecodeError as e:
        die(f"E02 invalid JSON in {path}: {e}")


def write_json(path, obj):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    except OSError as e:
        die(f"E01 cannot write {path}: {e}")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-") or "item"


def make_id(finding):
    disc = slug(finding.get(SPEC["discriminator"], ""))
    file = (finding.get("location") or {}).get("file", "")
    raw = "|".join([SPEC["kind"], disc, file, slug(finding["title"])])
    return f"{disc}-{hashlib.sha1(raw.encode()).hexdigest()[:12]}"


def title_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", str(text).lower()) if len(w) > 2}


def fuzzy_match(entries, taken, finding):
    disc = slug(finding.get(SPEC["discriminator"], ""))
    file = (finding.get("location") or {}).get("file", "")
    target = title_words(finding["title"])
    best, best_score = None, 0.0
    for entry in entries:
        if entry["id"] in taken:
            continue
        if slug(entry.get(SPEC["discriminator"], "")) != disc:
            continue
        if (entry.get("location") or {}).get("file", "") != file:
            continue
        other = title_words(entry["title"])
        union = target | other
        score = len(target & other) / len(union) if union else 0.0
        if score > best_score:
            best, best_score = entry, score
    return best if best_score >= 0.6 else None


def git_changed(repo, commit, head, path):
    if not commit or commit in ("none", "null") or not repo:
        return None
    try:
        out = subprocess.run(
            ["git", "-C", repo, "diff", "--name-only", f"{commit}..{head}", "--", path],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return bool(out.stdout.strip())


def repo_root_hint(repo_root):
    try:
        out = subprocess.run(
            ["git", "-C", repo_root, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return repo_root if os.path.isdir(repo_root) else None


def find_baseline(docs, current, explicit, report):
    if explicit and explicit not in ("none", "null") and os.path.exists(explicit):
        return explicit
    if not os.path.isdir(docs):
        return None
    current_abs = os.path.abspath(current)
    candidates = []
    for name in os.listdir(docs):
        if not name.endswith(".json"):
            continue
        path = os.path.join(docs, name)
        if os.path.abspath(path) == current_abs:
            continue
        if SPEC["baseline_match_module"]:
            try:
                with open(path, encoding="utf-8") as fh:
                    meta = json.load(fh)
            except (OSError, json.JSONDecodeError):
                continue
            if meta.get("module") != report.get("module"):
                continue
        candidates.append(path)
    if not candidates:
        return None
    candidates.sort(key=os.path.getmtime, reverse=True)
    return candidates[0]


def build_entries(baseline):
    entries = {}
    if not baseline:
        return entries
    for finding in baseline.get("findings") or []:
        entry_id = finding.get("id") or make_id(finding)
        entries[entry_id] = {
            "id": entry_id,
            "status": finding.get("status"),
            "title": finding.get("title", ""),
            SPEC["discriminator"]: finding.get(SPEC["discriminator"], ""),
            "location": finding.get("location") or {},
            "commit": baseline.get("commit"),
        }
    for item in (baseline.get("delta") or {}).get("not_rechecked_items") or []:
        entry_id = item.get("id")
        if not entry_id or entry_id in entries:
            continue
        raw = item.get("location", "") or ""
        file = raw.rsplit(":", 1)[0] if ":" in raw else raw
        entries[entry_id] = {
            "id": entry_id,
            "status": "persists",
            "title": "",
            SPEC["discriminator"]: "",
            "location": {"file": file, "line": 0},
            "commit": baseline.get("commit"),
        }
    return entries


def reconcile(report, baseline, repo):
    entries = build_entries(baseline)
    taken = set()
    delta = {
        "persists": 0,
        "new": 0,
        "regressed": 0,
        "not_rechecked": 0,
        SPEC["delta_closed"]: 0,
        SPEC["delta_closed_items"]: [],
        "not_rechecked_items": [],
    }

    for finding in report.get("findings") or []:
        required = ["title", "severity", "status"]
        if SPEC["location_required"]:
            required.append("location")
        for key in required:
            if not finding.get(key):
                die(f"E03 finding missing '{key}': {finding.get('title', '?')}")
        if not finding.get(SPEC["discriminator"]):
            die(f"E03 finding missing '{SPEC['discriminator']}': {finding['title']}")

        entry_id = finding.get("id") or make_id(finding)
        entry = entries.get(entry_id)
        if entry is None:
            entry = fuzzy_match(entries.values(), taken, finding)
            if entry is not None:
                entry_id = entry["id"]
        finding["id"] = entry_id

        status = finding["status"]
        if status not in [*SPEC["open"], SPEC["report_closed"]]:
            die(f"E04 unknown finding status {status!r}")
        if status == SPEC["report_closed"]:
            delta[SPEC["delta_closed"]] += 1
            loc = finding.get("location") or {}
            delta[SPEC["delta_closed_items"]].append(
                {
                    "id": entry_id,
                    "location": f"{loc.get('file', '')}:{loc.get('line', 0)}",
                    "title": finding["title"],
                }
            )
        elif status == "regressed" or (
            entry is not None
            and entry.get("status") in SPEC["closed"]
            and status in ("new", "persists")
        ):
            finding["status"] = "regressed"
            delta["regressed"] += 1
        elif status == "persists" or (entry is not None and status == "new"):
            finding["status"] = "persists"
            delta["persists"] += 1
        else:
            finding["status"] = "new"
            delta["new"] += 1
        taken.add(entry_id)

    head = report.get("commit") or "HEAD"
    for entry in entries.values():
        if entry["id"] in taken or entry.get("status") in SPEC["closed"]:
            continue
        path = (entry.get("location") or {}).get("file")
        changed = git_changed(repo, entry.get("commit"), head, path) if path else None
        reason = f"file changed since {entry.get('commit')}" if changed else "out of scan scope"
        delta["not_rechecked"] += 1
        delta["not_rechecked_items"].append(
            {
                "id": entry["id"],
                "location": f"{path}:{(entry.get('location') or {}).get('line', 0)}",
                "reason": reason,
            }
        )
    return delta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--docs", default=SPEC["docs"])
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    report = load_json(args.report)
    for key in ("schema", "date", "commit"):
        if not report.get(key):
            die(f"E02 report missing '{key}'")
    if report.get("schema") != SPEC["report_schema"]:
        die(f"E02 schema must be '{SPEC['report_schema']}'")
    if not isinstance(report.get("findings"), list):
        die("E02 report missing 'findings' list")

    baseline_path = find_baseline(args.docs, args.report, report.get("baseline"), report)
    baseline = load_json(baseline_path) if baseline_path else None
    if baseline and baseline.get("schema") != SPEC["report_schema"]:
        die(f"E05 baseline is not a {SPEC['skill']} report: {baseline_path}")

    repo = repo_root_hint(args.repo_root)
    report["baseline"] = baseline_path or "none"
    report["delta"] = reconcile(report, baseline, repo)
    write_json(args.report, report)

    delta = report["delta"]
    print(
        f"OK {delta['new']} new, {delta['persists']} persists, "
        f"{delta[SPEC['delta_closed']]} {SPEC['delta_closed_label']}, "
        f"{delta['regressed']} regressed, {delta['not_rechecked']} not re-checked"
    )


if __name__ == "__main__":
    main()
