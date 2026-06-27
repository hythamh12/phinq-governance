#!/usr/bin/env python3
"""Append a governed-action record to the Phinq audit log (hash-chained).

Usage:
    python3 audit_log.py '<json entry>'
    echo '<json entry>' | python3 audit_log.py

The entry is a JSON object per references/audit-format.md. This script adds:
    prev_hash   entry_hash of the previous line (64 zeros for the first)
    entry_hash  sha256(prev_hash + canonical(entry))

so that modifying, reordering, or deleting any historical entry breaks every
subsequent link. Verify with scripts/audit_verify.py.

Canonicalization follows RFC 8785 (JCS): keys sorted by UTF-16 code units,
no whitespace, UTF-8. Keep numeric fields as integers and everything else as
strings — integer/string-only entries canonicalize identically in every JCS
implementation, so logs written here verify under any other Phinq tool.

Log location: ~/.phinq/audit.jsonl (override: PHINQ_AUDIT_PATH).
Zero dependencies. Append-only — this script can only ever add lines.
"""
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone

GENESIS_PREV = "0" * 64


def audit_path() -> str:
    return os.environ.get(
        "PHINQ_AUDIT_PATH",
        os.path.expanduser("~/.phinq/audit.jsonl"),
    )


def jcs(value) -> str:
    """RFC 8785 canonical JSON for JSON-safe values (sorted keys, compact)."""
    if isinstance(value, bool) or value is None:
        return json.dumps(value)
    if isinstance(value, (int,)):
        return json.dumps(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("JCS: non-finite numbers are not JSON")
        return json.dumps(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(jcs(v) for v in value) + "]"
    if isinstance(value, dict):
        keys = sorted(value.keys())  # code-unit order for ASCII/BMP keys
        return "{" + ",".join(
            json.dumps(k, ensure_ascii=False) + ":" + jcs(value[k]) for k in keys
        ) + "}"
    raise ValueError(f"JCS: unsupported type {type(value).__name__}")


def entry_hash(prev_hash: str, entry: dict) -> str:
    return hashlib.sha256((prev_hash + jcs(entry)).encode("utf-8")).hexdigest()


def last_hash(path: str) -> str:
    if not os.path.exists(path):
        return GENESIS_PREV
    last = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = line
    if last is None:
        return GENESIS_PREV
    try:
        return json.loads(last)["entry_hash"]
    except (json.JSONDecodeError, KeyError):
        sys.stderr.write("warning: audit log tail unparseable — chain will not link\n")
        return GENESIS_PREV


def append(path: str, entry: dict) -> dict:
    prev = last_hash(path)
    h = entry_hash(prev, entry)
    record = dict(entry)
    record["prev_hash"] = prev
    record["entry_hash"] = h
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def main() -> int:
    raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    try:
        entry = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"error: entry is not valid JSON: {e}\n")
        return 2
    if not isinstance(entry, dict):
        sys.stderr.write("error: entry must be a JSON object\n")
        return 2
    if "prev_hash" in entry or "entry_hash" in entry:
        sys.stderr.write("error: do not supply hash fields — they are computed here\n")
        return 2

    path = audit_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # First write to a new file: genesis entry anchors the chain.
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        append(path, {
            "type": "genesis",
            "log_id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    record = append(path, entry)
    print(record["entry_hash"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
