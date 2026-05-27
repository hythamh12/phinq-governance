#!/bin/bash
# Install phinq-governance config for OpenCode in current repo
# Run: bash install-opencode.sh

set -e

echo "Installing phinq-governance for OpenCode in $(pwd)..."

# Create .opencode directory
mkdir -p .opencode

# Create OpenCode config with governance instructions
cat > .opencode/config.json << 'EOF'
{
  "agent": "build",
  "model": "openrouter/anthropic/claude-sonnet-4",
  "instructions": "BEFORE any file modification, external API call, or communication: Read SKILL.md from phinq-governance skill and follow the 5-step governance procedure (Classify → Check Rules → Pause/Confirm → Log → Execute). When in doubt, classify actions one level higher than your best guess. Pause and confirm with the operator for IRREVERSIBLE_MEDIUM and IRREVERSIBLE_HIGH actions. Action classes: RISK_REDUCING (always allowed), REVERSIBLE (log only), IRREVERSIBLE_LOW (log + notify), IRREVERSIBLE_MEDIUM (pause for confirmation), IRREVERSIBLE_HIGH (always pause). Structural triggers that always escalate: BULK_DELETE, CREDENTIAL_ACCESS, DISABLE_SAFEGUARDS, EXTERNAL_COMM_VOLUME, PERMISSION_ESCALATION, BILLING_MODIFICATION, AFTER_ERROR_BULK."
}
EOF

echo "✓ OpenCode governance config installed"
echo "  - Config: .opencode/config.json"
echo ""
echo "To use: Run 'opencode run \"<task>\"' in this repo"
