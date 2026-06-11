#!/usr/bin/env python3
"""Record an operator assessment of a past governed action — `phinq assess`.

Usage:
    python3 phinq_assess.py <action_id> \
        --judgment true_positive|false_positive|unclear \
        [--damage-gbp 250] \
        [--category financial_loss|reputational|data_loss|compliance|client_relationship|operational|none] \
        [--remediation-minutes 30] \
        [--note "free text"]

Assessments are what turn governance logs into actuarial data: the operator's
retrospective judgment of whether an intervention was correct, and what it
would have cost (counterfactual) or did cost (incident) if harm occurred.

Because the audit log is hash-chained, historical entries are never modified.
An assessment is appended as a NEW entry of type "assessment" that references
the original action_id — verifiers and reporting tools join them by id.

Optional and encouraged, never required. The skill works without assessments;
with them, the dataset measures risk, not just activity.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

JUDGMENTS = ["true_positive", "false_positive", "unclear"]
CATEGORIES = [
    "financial_loss", "reputational", "data_loss", "compliance",
    "client_relationship", "operational", "none",
]


def main() -> int:
    p = argparse.ArgumentParser(description="Append an operator assessment to the audit log")
    p.add_argument("action_id", help="action_id (or hold_id) of the entry being assessed")
    p.add_argument("--judgment", required=True, choices=JUDGMENTS,
                   help="was the governance intervention correct?")
    p.add_argument("--damage-gbp", type=int, default=None,
                   help="estimated damage in GBP (prevented if true_positive, incurred if incident)")
    p.add_argument("--category", choices=CATEGORIES, default=None,
                   help="primary type of damage at stake")
    p.add_argument("--remediation-minutes", type=int, default=None,
                   help="time spent remediating, if an incident occurred")
    p.add_argument("--incident", action="store_true",
                   help="the action executed and caused harm (incident, not counterfactual)")
    p.add_argument("--note", default=None, help="free-text context")
    args = p.parse_args()

    entry = {
        "type": "assessment",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_id": args.action_id,
        "kind": "incident" if args.incident else "counterfactual",
        "operator_judgment": args.judgment,
    }
    if args.damage_gbp is not None:
        entry["estimated_damage_gbp"] = args.damage_gbp
    if args.category:
        entry["damage_category"] = args.category
    if args.remediation_minutes is not None:
        entry["remediation_time_minutes"] = args.remediation_minutes
    if args.note:
        entry["note"] = args.note

    # Reuse the chained appender so the assessment joins the same chain.
    result = subprocess.run(
        [sys.executable, __file__.replace("phinq_assess.py", "audit_log.py"),
         json.dumps(entry, ensure_ascii=False)],
        capture_output=True, text=True,
    )
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        return result.returncode
    print(f"assessment recorded for {args.action_id} ({entry['kind']}, {args.judgment})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
