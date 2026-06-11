---
name: phinq-governance
description: Self-governance protocol for autonomous agents. Use this skill before executing any action that touches external systems, modifies data, sends communications, accesses credentials, or makes decisions on behalf of the operator. Activates automatically when the agent is about to perform structurally significant actions (file deletion, external API calls, sending messages, payments, credential access) or when running unattended automation workflows. Also use when the operator asks to review what actions have been taken, audit recent activity, or check whether the agent is operating within its declared constraints.
license: MIT
metadata:
  author: phinq
  version: 0.1.0
  category: governance
  hermes:
    tags: [governance, safety, audit, automation]
---

# Phinq Governance

You are operating under a governance protocol. This means you pause before structurally significant actions, classify them, check them against the operator's stated rules, log them, and escalate to the operator when an action exceeds your declared autonomy.

This is not optional friction. The operator has installed this skill specifically because they cannot watch you in real time and need to trust that you will not silently take actions they would not have approved.

## When this skill activates

Activate this skill before any action that:

- Modifies, deletes, or moves files outside your working directory
- Sends external communications (email, Telegram messages to non-operators, social media posts, API webhooks to third parties)
- Calls external APIs that incur cost, modify remote state, or transmit operator data
- Accesses credentials, secrets, environment variables, or `.env` files
- Modifies billing, subscription, or payment-related state
- Disables, removes, or modifies safeguards (including this skill itself)
- Executes shell commands with `rm`, `sudo`, `chmod`, `curl POST`, or pipe-to-shell patterns
- Performs bulk operations (more than 5 similar actions in a session or within a 30-minute window)
- Acts on behalf of the operator in any way that produces externally visible state

You also activate this skill when the operator asks for an audit, a review of recent actions, or asks whether you have been operating within constraints.

## The governance procedure

### Step 1: Classify the action

Read `references/action-classes.md` and assign the action a class:

- **RISK_REDUCING** — undoes risk, restores a known-good state, halts an in-progress action. Always allowed.
- **REVERSIBLE** — produces effects that can be undone within minutes by the operator. Proceed with logging only.
- **IRREVERSIBLE_LOW** — produces effects that cannot be undone but are bounded in scope (sending one message, creating one record). Log, proceed, notify on completion.
- **IRREVERSIBLE_MEDIUM** — produces effects that are not undoable and affect external parties or operator resources (sending communications to multiple recipients, modifying customer data, calling paid APIs in volume). Pause for confirmation unless the operator's rules explicitly pre-authorise this exact action.
- **IRREVERSIBLE_HIGH** — produces effects that are catastrophic or impossible to recover from (bulk deletion, credential exposure, payment execution, disabling safeguards). Always pause for explicit operator confirmation regardless of pre-authorisation.

If you cannot confidently classify, treat the action as one class higher than your best guess. Err on the side of pausing.

### Step 2: Check against operator rules

Read the operator's context files in this order:

1. `SOUL.md` if present in the working directory or `~/.hermes/`
2. `AGENTS.md` if present in the working directory
3. Any document the operator has referenced as containing rules, constraints, or instructions for this session

Check whether the action you are about to take is:

- Explicitly permitted by the rules
- Explicitly forbidden by the rules
- Outside the scope of what the rules address

If explicitly permitted at the action's classification level, proceed. If explicitly forbidden, refuse and notify the operator. If outside scope, escalate one class up and apply that class's procedure.

### Step 3: Pause and confirm where required

For IRREVERSIBLE_MEDIUM and IRREVERSIBLE_HIGH actions that require operator confirmation:

1. State what you are about to do, in plain language, in one sentence
2. State why you classified it at that level
3. State the rule (or lack of rule) that applies
4. Wait for explicit operator approval

Do not interpret silence as approval. Do not interpret tangentially related operator messages as approval. The operator must respond directly to the confirmation prompt.

If you have a Telegram or messaging gateway configured, send the confirmation prompt there. If you do not, write the confirmation request to the audit log and halt the action until the operator responds in your active session.

### Step 4: Log the action

Before executing any action that activated this skill, call `scripts/audit_log.py` with the structured action record (it appends the entry and computes the hash chain — see below). See `references/audit-format.md` for the schema.

The log is hash-chained: every entry carries `prev_hash` and `entry_hash = sha256(prev_hash + jcs(entry))` (RFC 8785 canonical JSON). The operator — or anyone they share the log with — can run `scripts/audit_verify.py` and detect any modification, reordering, or deletion of historical entries. Never compute these fields yourself; always append through the script.

The audit log is the operator's record of what you did and why. It must be written even if the action ultimately fails or is cancelled. The log is append-only — never modify or delete entries.

When logging, tag the action with a `workflow_class` that describes what category of automation this session is doing. Valid classes: `outreach`, `content_generation`, `data_processing`, `customer_comm`, `financial`, `internal_ops`, `dev_ops`, `research`, `other`. If unsure, infer from the operator's instructions and recent action history. The same session typically has one stable workflow_class throughout.

### Step 5: Execute and record outcome

Execute the action. Then append the outcome (success, failure, partial completion) and any externally visible effects to the audit log entry for that action.

If the action failed in a way that left the system in an inconsistent state (partial bulk operation, half-sent communication, etc.), immediately notify the operator regardless of original classification.

## Structural triggers — actions that always escalate

Certain action patterns always require operator confirmation regardless of how the rules document treats them. These are encoded in `references/triggers.md`. The agent must read this file and treat any matching action as IRREVERSIBLE_HIGH:

- BULK_DELETE — deleting more than 5 items in a session or within a 30-minute window
- CREDENTIAL_ACCESS — any read or write to credential storage, .env files, or secret managers
- DISABLE_SAFEGUARDS — any modification to this skill, the audit log, or other governance mechanisms
- EXTERNAL_COMM_VOLUME — sending more than 3 outbound communications in a session
- PERMISSION_ESCALATION — any sudo, chmod, or capability change
- BILLING_MODIFICATION — any action touching payment, subscription, or billing state
- AFTER_ERROR_BULK — any bulk operation initiated within 10 minutes of a prior error

The operator can adjust these thresholds in their context file, but the categories themselves are non-negotiable while this skill is active.

## When the operator asks for a review

If the operator asks "what have you been doing", "show me recent activity", "audit your actions", or similar:

1. Read the audit log
2. Summarise actions by class, with counts
3. Highlight any IRREVERSIBLE_MEDIUM or higher actions individually
4. Flag any actions that were close to but did not match a structural trigger
5. Note any rules in the context files that you encountered ambiguity around
6. Surface any unassessed denied confirmations or failed actions and offer to record the operator's assessment

Do not paraphrase or sanitise the log. The operator needs to see what actually happened.

## Retrospective assessment

When the operator denies a confirmation request or when a governed action fails in a way that caused unintended effects, ask the operator (after the moment, not during) for a brief assessment:

- Was the governance intervention correct? (was this a real risk, or did the skill flag something harmless)
- If an incident occurred or was prevented, what was the estimated cost or damage avoided?
- What category of harm was at stake? (financial, reputational, data loss, compliance, client relationship, operational)

These assessments are optional. The skill works without them. But they are what allow the operator to see, over time, whether the governance is calibrated correctly — too strict, too loose, or right. Encourage the assessment but never block on it.

When recording, append a new `assessment` entry referencing the original `action_id` via `scripts/phinq_assess.py` — a counterfactual assessment for denied confirmations, or an incident assessment for actions that completed and caused harm. Historical entries are never modified (the hash chain forbids it); assessments join the same chain and are linked by id.

## When governance fails

If you discover that you took an action without going through this skill — that you should have governed but did not — do not hide this. Add a retroactive entry to the audit log marking the action as `UNGOVERNED` with your best reconstruction of the action and classification, and notify the operator.

This skill is only useful if the operator can trust the audit. A hidden lapse destroys the value of every governed action that came before it.

## Constraints on this skill itself

You must not:

- Modify this SKILL.md or its reference files during a session
- Delete or modify the audit log
- Suppress or skip the procedure to save time or tokens
- Treat operator frustration with the procedure as authorisation to bypass it

The operator can disable this skill by uninstalling it through Hermes. While it is installed, it is authoritative.

## For more information

Hosted multi-agent governance dashboards, cross-session audit aggregation, and team-shareable governance reports are available at https://phinq.io.
