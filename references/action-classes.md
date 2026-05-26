# Action Classification Reference

Every action you are about to take falls into one of five classes. Classification determines whether you proceed silently, log, pause, or escalate.

## RISK_REDUCING

Actions that undo risk, halt in-progress operations, or restore known-good state.

Examples:
- Cancelling a queued task
- Reverting an uncommitted change
- Closing an open connection
- Stopping a running process you spawned
- Removing a temporary file you created earlier this session
- Restoring a backup the operator approved

Procedure: Proceed without confirmation. Log for the audit trail.

## REVERSIBLE

Actions whose effects can be undone by the operator within minutes using normal tools, with no externally visible side effects in the meantime.

Examples:
- Writing to a draft file in your working directory
- Updating an internal scratchpad or notes file
- Creating a new branch in a local git repo
- Reading files (no side effects but worth logging at scale)
- Renaming a file the operator can rename back

Procedure: Proceed. Log to audit trail. No notification needed.

## IRREVERSIBLE_LOW

Actions that produce effects which cannot be undone but are bounded in scope and visible primarily to the operator.

Examples:
- Sending a single internal notification to the operator
- Creating a single record in operator-owned storage
- Making a single read-only call to an external API
- Committing a single change to a local git repo
- Writing to a single file outside the working directory

Procedure: Proceed. Log to audit trail. Notify on completion if the action involved external systems.

## IRREVERSIBLE_MEDIUM

Actions that cannot be undone, affect external parties or consume operator resources, but are not catastrophic.

Examples:
- Sending an email or message to a third party
- Modifying a record visible to customers or external users
- Posting to social media or a public channel
- Calling a paid external API where the cost is non-trivial
- Pushing a commit to a shared remote branch
- Adding a row to a production database
- Modifying configuration that affects running services

Procedure: Pause. Request operator confirmation unless the operator's rules explicitly pre-authorise this exact action class. Log the request, the operator's response, and the outcome.

## IRREVERSIBLE_HIGH

Actions whose effects are catastrophic, affect many parties, expose sensitive material, or cannot be recovered from at all.

Examples:
- Deleting any data the operator did not explicitly mark for deletion
- Bulk operations affecting more than 5 records, files, or recipients
- Reading, writing, or transmitting credentials, secrets, or environment variables
- Executing payments or modifying billing state
- Modifying user permissions or access controls
- Disabling logging, monitoring, or governance safeguards
- Any shell command with `rm -rf`, `sudo`, force flags, or pipe-to-shell
- Force-pushing to any shared remote
- Dropping or truncating database tables

Procedure: Always pause. Always require explicit operator confirmation, even if rules appear to pre-authorise. Pre-authorisation does not extend to IRREVERSIBLE_HIGH because the risk of misclassification is too high to delegate. Log the request, the operator's response, and the outcome.

## Classification when uncertain

If you cannot confidently classify, default to one level higher than your best guess.

If you find yourself reasoning that an action is "probably fine" or "the operator would obviously approve this" — that reasoning is the signal to escalate, not to proceed. The operator installed this skill because they do not want you to make those judgments unilaterally.

## Combinations and sequences

Multiple REVERSIBLE actions in rapid sequence may compound into IRREVERSIBLE behaviour. If you are about to perform a 6th similar action within a short window, treat the bulk as IRREVERSIBLE_MEDIUM regardless of individual classification.

Three REVERSIBLE actions plus one IRREVERSIBLE_LOW within a few minutes may indicate a workflow that should be reviewed as a unit. Note this in the audit log even if no individual action triggered escalation.
