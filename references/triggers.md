# Structural Triggers

Certain action patterns require operator confirmation regardless of how the operator's rules document treats them. The operator cannot pre-authorise these because the patterns themselves indicate elevated risk that overrides general permissions.

When you detect any of the following patterns, escalate the action to IRREVERSIBLE_HIGH and require explicit confirmation.

## BULK_DELETE

Triggered by: deleting more than 5 items (files, records, messages, emails, database rows) in a single session or within a 30-minute window.

Why this is non-negotiable: bulk deletions are the most common source of catastrophic agent failure. A single misinterpreted instruction can destroy hours, days, or years of operator data. The cost of pausing is trivial. The cost of proceeding incorrectly is unrecoverable.

Confirmation prompt should include: total count, sample of items to be deleted, source of the deletion instruction.

## CREDENTIAL_ACCESS

Triggered by: reading, writing, transmitting, or logging any of:
- Files matching `.env`, `.envrc`, `credentials`, `secrets`, `.pem`, `.key`, `id_rsa`
- Environment variables containing `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL`
- Contents of password managers, keychain entries, or secret managers
- API keys, access tokens, or session tokens in any form

Why this is non-negotiable: credentials exposed in logs, transmitted to external services, or accidentally committed cannot be unexposed. Rotation is possible but always costly. Many credential leaks are silent and only discovered after exploitation.

Confirmation prompt should include: which credential, where it is being accessed from, where it is being sent or written to.

## DISABLE_SAFEGUARDS

Triggered by: any modification to:
- This skill (`phinq-governance/SKILL.md` or any file in this skill's directory)
- The audit log file
- Other installed governance, monitoring, or safety skills
- Logging configuration that would suppress action records
- The skill registry or skill installation state

Why this is non-negotiable: an agent that can silently disable its own oversight provides no oversight. The operator must be aware whenever the governance layer is being modified, even if the modification looks benign.

Confirmation prompt should include: what is being modified, what behaviour will change as a result.

## EXTERNAL_COMM_VOLUME

Triggered by: sending more than 3 outbound communications (emails, messages, social posts, webhooks to third parties) within a single session.

Why this is non-negotiable: external communications cannot be recalled. A misfiring loop or misinterpreted instruction can damage operator reputation, violate platform policies, or constitute spam at machine speed.

Confirmation prompt should include: recipients, sample of message content, total count if continuing a sequence.

## PERMISSION_ESCALATION

Triggered by:
- `sudo` invocations
- `chmod`, `chown` with permission-elevating arguments
- `setcap`, `setuid`, `setgid` operations
- Cloud IAM modifications
- Granting or modifying access to repositories, databases, or services
- Adding users or modifying group memberships

Why this is non-negotiable: permission escalations expand the blast radius of subsequent actions. They are also often persistent — a misconfigured permission can outlive the session indefinitely.

Confirmation prompt should include: what permission is being granted, to whom, for what purpose.

## BILLING_MODIFICATION

Triggered by: any action touching:
- Payment methods, cards, or bank account details
- Subscription state (upgrade, downgrade, cancellation)
- Invoicing or billing records
- Customer payment information
- Credit limits, spending caps, or rate limits with cost implications

Why this is non-negotiable: financial actions have legal and reputational consequences beyond the operator's immediate scope. Even a successful unauthorised billing action creates compliance exposure.

Confirmation prompt should include: amount, party affected, nature of the change, reversibility.

## AFTER_ERROR_BULK

Triggered by: initiating any bulk operation (more than 3 similar actions) within 10 minutes of a prior error in the session.

Why this is non-negotiable: errors often indicate that the agent's model of the system is wrong. Continuing to take bulk action while operating on a wrong model is how small errors become large ones. The cooldown is a forcing function for the agent to verify the underlying assumption before scaling.

Confirmation prompt should include: the recent error, the proposed bulk action, the reasoning for why the error does not affect the bulk action.

## Trigger interaction

If a single action matches multiple triggers, treat as a single IRREVERSIBLE_HIGH action with all matching triggers cited in the confirmation prompt. Do not require separate confirmations per trigger.

If the operator declines a triggered action, do not retry the action in a different form to bypass the trigger. The decline applies to the underlying intent, not just the literal action.
