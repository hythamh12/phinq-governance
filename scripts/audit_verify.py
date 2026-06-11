#!/usr/bin/env python3
"""Verify the Phinq audit log hash chain — `phinq audit verify`.

Usage:
    python3 audit_verify.py [path]

Walks the chain and reports the first break (index + timestamp). Detects any
modification, reordering, or deletion of historical entries. Truncation of
the file's tail is not detectable from the file alone (that requires
anchoring the chain head externally).

Exit codes: 0 = intact, 1 = break found, 2 = usage/IO error.
"""
import json
import os
import sys

from audit_log import GENESIS_PREV, audit_path, entry_hash


def verify(path: str) -> int:
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [l for l in f.readlines() if l.strip()]
    except OSError as e:
        sys.stderr.write(f"cannot read {path}: {e}\n")
        return 2

    prev = GENESIS_PREV
    for index, line in enumerate(lines):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            print(f"TAMPER DETECTED — entry {index}: unparseable line")
            return 1
        claimed_prev = record.pop("prev_hash", None)
        claimed_hash = record.pop("entry_hash", None)
        ts = record.get("timestamp") or record.get("created_at") or "?"
        if index == 0 and record.get("type") != "genesis":
            print(f"TAMPER DETECTED — entry 0 (ts {ts}): missing genesis entry")
            return 1
        if claimed_prev != prev:
            print(
                f"TAMPER DETECTED — entry {index} (ts {ts}): prev_hash does not match "
                "the preceding entry (modified, reordered, or removed)"
            )
            return 1
        if claimed_hash != entry_hash(prev, record):
            print(f"TAMPER DETECTED — entry {index} (ts {ts}): entry content modified")
            return 1
        prev = claimed_hash

    print(f"OK — {len(lines)} entries, chain intact ({path})")
    return 0


if __name__ == "__main__":
    sys.exit(verify(sys.argv[1] if len(sys.argv) > 1 else audit_path()))
