#!/bin/bash
# Install phinq-governance config for Codex in current repo
# Run: bash install-codex.sh

set -e

echo "Installing phinq-governance for Codex in $(pwd)..."

# Create .codex directory
mkdir -p .codex

# Create Codex config with governance instructions
cat > .codex/config.json << 'EOF'
{
  "instructions": "BEFORE any file modification, external API call, or communication: Read SKILL.md from phinq-governance skill and follow the 5-step governance procedure (Classify → Check Rules → Pause/Confirm → Log → Execute). When in doubt, classify actions one level higher than your best guess. Pause and confirm with the operator for IRREVERSIBLE_MEDIUM and IRREVERSIBLE_HIGH actions. Action classes: RISK_REDUCING (always allowed), REVERSIBLE (log only), IRREVERSIBLE_LOW (log + notify), IRREVERSIBLE_MEDIUM (pause for confirmation), IRREVERSIBLE_HIGH (always pause)."
}
EOF

echo "✓ Codex governance config installed"
echo "  - Config: .codex/config.json"
echo ""
echo "To use: Run 'codex exec \"<task>\"' in this repo"
