# Phinq Governance Repo

## Governance Protocol
This repo implements the **phinq-governance** skill. All actions that touch external systems, modify data, or make decisions on behalf of the operator MUST follow the procedure in `SKILL.md`.

## Quick Rules for Coding Agents
- Before any file modification, external API call, or communication: read `SKILL.md` and follow the 5-step governance procedure.
- Action classes are defined in `references/action-classes.md`.
- Audit format is in `references/audit-format.md`.
- Structural triggers that always escalate are in `references/triggers.md`.

## Repo Structure
- `SKILL.md` — the governance protocol
- `references/` — action classes, audit format, triggers
- `scripts/audit_log.py` — (to be implemented) audit logging script

## When in Doubt
Classify actions one level higher than your best guess. Pause and confirm with the operator for IRREVERSIBLE_MEDIUM and IRREVERSIBLE_HIGH actions.
