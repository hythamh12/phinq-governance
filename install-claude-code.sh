#!/bin/bash
# Install phinq-governance for Claude Code (global - works in any repo)
# Run: bash install-claude-code.sh

set -e

echo "Installing phinq-governance for Claude Code..."

# Create global Claude config directory
mkdir -p ~/.claude/agents ~/.claude/rules

# Copy governance agent globally
cp .claude/agents/governance-reviewer.md ~/.claude/agents/

# Copy governance rules globally  
cp .claude/rules/governance.md ~/.claude/rules/

# Create global CLAUDE.md with governance reference
if [ ! -f ~/.claude/CLAUDE.md ]; then
  cat > ~/.claude/CLAUDE.md << 'EOF'
# Global Rules

## Phinq Governance
All actions that touch external systems, modify data, or send communications must follow the phinq-governance protocol:
1. Read phinq-governance SKILL.md (in ~/.hermes/skills/phinq-governance/)
2. Classify the action
3. Check against operator rules
4. Pause for IRREVERSIBLE_MEDIUM/HIGH actions
5. Log the action
EOF
else
  echo "~/.claude/CLAUDE.md already exists, skipping"
fi

echo "✓ Claude Code governance installed globally"
echo "  - Agent: ~/.claude/agents/governance-reviewer.md"
echo "  - Rules: ~/.claude/rules/governance.md"
echo "  - Global CLAUDE.md updated"
echo ""
echo "To use: Run 'claude' in any repo, then '@governance-reviewer review <action>'"
