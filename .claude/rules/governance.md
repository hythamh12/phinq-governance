# Phinq Governance Rules

## Mandatory Activation

Before ANY action that:
- Modifies, deletes, or moves files outside your working directory
- Sends external communications (email, Telegram, social media, webhooks)
- Calls external APIs that incur cost or modify state
- Accesses credentials, secrets, or .env files
- Executes `rm`, `sudo`, `chmod`, `curl POST` commands
- Performs bulk operations (>5 similar actions)

## Required Procedure (from SKILL.md)

1. **Classify** the action using `references/action-classes.md`
2. **Check** against operator rules (SOUL.md, AGENTS.md)
3. **Pause** for IRREVERSIBLE_MEDIUM/HIGH actions (unless pre-authorised)
4. **Log** the action using `scripts/audit_log.py` (schema in `references/audit-format.md`)
5. **Execute** and record outcome

## Structural Triggers (Always IRREVERSIBLE_HIGH)

- BULK_DELETE: >5 deletions in sequence
- CREDENTIAL_ACCESS: Read/write credentials or .env
- DISABLE_SAFEGUARDS: Modify governance files
- EXTERNAL_COMM_VOLUME: >3 outbound communications
- PERMISSION_ESCALATION: sudo, chmod, capability changes
- BILLING_MODIFICATION: Payment/billing state changes
- AFTER_ERROR_BULK: Bulk ops within 10 mins of error

## Quick Reference

| Class | Action | Requirement |
|-------|--------|-------------|
| RISK_REDUCING | Undo risk, restore state | Always allowed |
| REVERSIBLE | Can be undone quickly | Log only |
| IRREVERSIBLE_LOW | Bounded, can't undo | Log, notify on completion |
| IRREVERSIBLE_MEDIUM | Affects external parties | Pause for confirmation |
| IRREVERSIBLE_HIGH | Catastrophic potential | Always pause |

**When in doubt: classify one level higher. Err on the side of pausing.**
