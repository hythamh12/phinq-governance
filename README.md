# phinq-governance

A self-governance skill for autonomous AI agents. Drops into Claude Code, Codex, OpenCode, and any [agentskills.io](https://agentskills.io)-compatible runtime — no framework lock-in.

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

A **tamper-evident**, append-only JSONL audit log at `~/.phinq/audit.jsonl` containing every governed action, its classification, the rule check, any operator confirmation, and the execution outcome. Entries are hash-chained (`entry_hash = sha256(prev_hash + jcs(entry))`, RFC 8785 canonical JSON), so any modification, reordering, or deletion of history is detectable:

```bash
python3 scripts/audit_verify.py            # OK — 214 entries, chain intact
```

Operators can retrospectively grade interventions — true positive or false alarm, with estimated damage prevented — which turns the log into calibration and actuarial data:

```bash
python3 scripts/phinq_assess.py <action_id> --judgment true_positive --damage-gbp 500 --category data_loss
```

## Install

Clone the repo, then run the installer for your agent:

```bash
git clone https://github.com/hythamh12/phinq-governance && cd phinq-governance

bash install-claude-code.sh   # Claude Code — global, works in any repo
bash install-codex.sh         # Codex — current repo
bash install-opencode.sh      # OpenCode — current repo
```

### Any agentskills.io runtime

Drop `SKILL.md` into your skills directory (or clone the repo there). Most clients auto-discover skills in their configured skill paths — e.g. `hermes skills install https://github.com/hythamh12/phinq-governance` for Hermes.

## Configuration

The skill respects two environment variables:

- `PHINQ_AUDIT_PATH` — override the default audit log location
- `PHINQ_SESSION_ID` — stable session identifier (auto-generated if absent)

Operator rules and constraints should live in your agent's standard context files (`SOUL.md`, `AGENTS.md`, or whatever your runtime uses). The skill reads these to check whether actions are permitted.

## How it integrates with operator rules

The skill cross-references your existing rules document. If you have a `SOUL.md` saying "never send emails after midnight", the skill catches the violation and pauses. You don't need to learn a new rules format — write rules where you already write them.

## What it does not do

- It does not intercept calls at the runtime level. The agent must consult the skill before acting, which means the skill works on agents that respect their skills system. For hard enforcement — a proxy that sits between the agent and its LLM provider, inspects every tool call before the agent sees it, and holds high-risk actions for operator approval via Telegram — see **Phinq Proxy** at [phinq.co](https://www.phinq.co) (same classification model, same audit format; logs from both verify with the same tools).
- It does not prevent a sufficiently capable adversarial agent from bypassing it. It is a governance protocol, not a sandbox.
- It does not store credentials or secrets itself. It refuses to log them.

## Hosted

For multi-agent dashboards, cross-session audit aggregation, anomaly detection, and team-shareable governance reports across many agents and runtimes, see [phinq.co](https://www.phinq.co).

## License

MIT
