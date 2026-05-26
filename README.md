# phinq-governance

A self-governance skill for autonomous agents. Designed for [Hermes](https://github.com/NousResearch/hermes-agent) and any [agentskills.io](https://agentskills.io)-compatible runtime.

## What it does

Installs a procedural memory layer that the agent reads before taking any structurally significant action. The agent classifies the action, checks it against your rules documents, pauses for confirmation on high-risk actions, and writes an append-only audit log of everything it does.

This solves a specific problem: your AI automation runs unattended and you cannot watch it. You need to know what it did, why, and trust that it paused before doing anything it shouldn't.

## What it covers

- File deletions and bulk operations
- External communications (email, messaging, social, webhooks)
- Credential and secret access
- Payment and billing modifications
- Permission escalations and shell command risk
- Modifications to the agent's own safeguards
- Cascading actions after errors

## What it produces

An append-only JSONL audit log at `~/.hermes/phinq-audit/audit.jsonl` containing every governed action, its classification, the rule check, any operator confirmation, and the execution outcome.

## Install

### For Hermes users

```bash
hermes skills install https://github.com/hythamh12/phinq-governance
```

Or for an individual `SKILL.md`:

```bash
hermes skills install https://raw.githubusercontent.com/hythamh12/phinq-governance/main/SKILL.md
```

### For other agentskills.io runtimes

Clone the repo into your skills directory. Most clients auto-discover skills in their configured skill paths.

## Configuration

The skill respects two environment variables:

- `PHINQ_AUDIT_PATH` — override the default audit log location
- `PHINQ_SESSION_ID` — stable session identifier (auto-generated if absent)

Operator rules and constraints should live in your agent's standard context files (`SOUL.md`, `AGENTS.md`, or whatever your runtime uses). The skill reads these to check whether actions are permitted.

## How it integrates with operator rules

The skill cross-references your existing rules document. If you have a `SOUL.md` saying "never send emails after midnight", the skill catches the violation and pauses. You don't need to learn a new rules format — write rules where you already write them.

## What it does not do

- It does not intercept calls at the runtime level. The agent must consult the skill before acting, which means the skill works on agents that respect their skills system.
- It does not prevent a sufficiently capable adversarial agent from bypassing it. It is a governance protocol, not a sandbox.
- It does not store credentials or secrets itself. It refuses to log them.

## Hosted

For multi-agent dashboards, cross-session audit aggregation, anomaly detection, and team-shareable governance reports across multiple Hermes instances, see [phinq.io](https://phinq.io).

## License

MIT
