# Audit Log Format

The audit log is the operator's authoritative record of governed actions. It must be human-readable, append-only, and complete.

## Location

Default: `~/.hermes/phinq-audit/audit.jsonl`

The path can be overridden by the `PHINQ_AUDIT_PATH` environment variable. If the directory does not exist, create it before writing the first entry.

## Format

One JSON object per line (JSONL). Each entry is a single action record. Never split an action across multiple lines.

## Hash chain (tamper evidence)

Every entry carries two additional fields, computed at append time by `scripts/audit_log.py`:

```
prev_hash   entry_hash of the previous line (64 zeros for the first line)
entry_hash  sha256(prev_hash + jcs(entry))   # hex; entry excludes both hash fields
```

`jcs` is RFC 8785 (JCS) canonical JSON: object keys sorted by UTF-16 code units, no whitespace, UTF-8 bytes. Use integers and strings for field values — they canonicalize identically in every JCS implementation, so a log written by one Phinq tool verifies under any other.

The first line of every log file is a genesis entry that anchors the chain:

```json
{"type": "genesis", "log_id": "<uuid>", "created_at": "<ISO 8601>"}
```

Verification (`scripts/audit_verify.py`, or `npm run audit:verify` in the proxy) walks the chain and reports the first break: any modification, reordering, or deletion of a historical entry is detected at its exact index. Known limitation: truncating the tail of the file is not detectable from the file alone; anchoring the chain head externally is a future addition.

Always append through `scripts/audit_log.py`. Never compute hash fields by hand and never write lines directly.

## Schema

```json
{
  "timestamp": "ISO 8601 UTC timestamp of when the action was initiated",
  "session_id": "Stable identifier for the current agent session",
  "action_id": "Unique identifier for this action within the session",
  "workflow_class": "Category of automation this session is performing (outreach, content_generation, data_processing, customer_comm, financial, internal_ops, dev_ops, research, other)",
  "intent": "One-sentence plain language description of what the action will do",
  "action_type": "Mechanical category (file_write, api_call, message_send, shell_exec, etc.)",
  "class": "RISK_REDUCING | REVERSIBLE | IRREVERSIBLE_LOW | IRREVERSIBLE_MEDIUM | IRREVERSIBLE_HIGH",
  "triggers": ["List of structural triggers matched, or empty array"],
  "rule_check": {
    "permitted_by": "Path or document reference if the action is explicitly permitted by a rule, else null",
    "forbidden_by": "Path or document reference if forbidden, else null",
    "ambiguous": "true if rules did not cover this action class"
  },
  "confirmation": {
    "required": "true if class required operator confirmation",
    "requested_at": "ISO 8601 timestamp of when confirmation was requested, or null",
    "received_at": "ISO 8601 timestamp of when operator responded, or null",
    "response": "approve | deny | timeout | not_required",
    "operator_message": "The literal text of the operator's response, or null",
    "counterfactual": {
      "operator_judgment": "true_positive | false_positive | unclear | not_assessed — operator's assessment of whether the governance intervention was correct in retrospect",
      "estimated_damage_prevented_gbp": "Operator's estimated cost in GBP if the action had been allowed to proceed, or null if not assessed",
      "estimated_damage_category": "financial_loss | reputational | data_loss | compliance | client_relationship | operational | none — primary type of damage that would have occurred",
      "assessed_at": "ISO 8601 timestamp of when the operator made this assessment, or null"
    }
  },
  "execution": {
    "started_at": "ISO 8601 timestamp",
    "completed_at": "ISO 8601 timestamp or null if still running",
    "status": "success | failure | partial | cancelled | pending",
    "error": "Error message if status is failure or partial, else null",
    "external_effects": ["List of externally visible effects produced by this action"],
    "incident": {
      "occurred": "true if this action caused unintended harm or required remediation, else false",
      "estimated_cost_gbp": "Operator's estimated cost of remediation and damage in GBP, or null",
      "cost_category": "financial_loss | reputational | data_loss | compliance | client_relationship | operational — primary type of damage that occurred",
      "remediation_time_minutes": "Operator's estimate of time spent remediating, or null",
      "assessed_at": "ISO 8601 timestamp of when the operator assessed this incident, or null"
    }
  },
  "context": {
    "operator_request": "The operator instruction or context that led to this action",
    "preceding_action_ids": ["Action IDs of immediately preceding related actions in this session"]
  }
}
```

## Note on counterfactual and incident assessment

The `counterfactual` and `incident` blocks are populated retrospectively by the operator, not at the moment of action. Most actions will have these fields null at write time — and because the log is hash-chained, they are **never filled in by editing the original entry**. Instead, `scripts/phinq_assess.py <action_id> --judgment ...` appends a separate `assessment` entry that references the original `action_id`; reporting tools join the two by id. The original blocks remain in the schema as the documented shape of what an assessment captures.

These fields are what transform raw governance logs into actuarial data. Without operator assessment of what actually happened (or would have happened), the dataset measures activity but cannot measure risk. With assessment, the dataset measures both, and the relationship between governance interventions and prevented damage becomes quantifiable.

Operators should be encouraged but never required to assess. The skill works fine without these fields. They are the difference between data that monitors and data that underwrites.

## Special entry types

### UNGOVERNED

If you discover that an action was taken without going through this skill, log it retroactively with:

```json
{
  "timestamp": "ISO 8601 of when the action was actually taken, or best estimate",
  "class": "UNGOVERNED",
  "intent": "Reconstruction of what the action did",
  "discovered_at": "ISO 8601 of when the lapse was discovered",
  "discovery_context": "How the lapse was discovered"
}
```

### SESSION_BOUNDARY

At the start and end of each governed session, write a session marker:

```json
{
  "timestamp": "ISO 8601",
  "session_id": "...",
  "type": "session_start | session_end",
  "agent_identity": "Identifier for the agent instance",
  "operator_identity": "Identifier for the operator, if known"
}
```

## Integrity

The audit log is append-only. Never:

- Modify existing entries
- Delete entries
- Reorder entries
- Rewrite the file

These rules are now mechanically enforced: the hash chain makes any in-place modification, reordering, or deletion detectable by `scripts/audit_verify.py`. If the file becomes corrupted, write a new entry of type `INTEGRITY_NOTE` describing what was observed, then continue appending to the same file. Notify the operator.

If you must rotate the log for size reasons, copy the existing log to `audit-{ISO date}.jsonl` and begin a fresh file with a SESSION_BOUNDARY entry that references the archive.
