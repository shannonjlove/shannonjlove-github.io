#!/usr/bin/env bash
# Run inside the WebTop container to finish Claude Code setup after npm blocked
# the postinstall script with "approve-scripts".
# Usage: bash webtop-claude-postinstall.sh
set -euo pipefail

echo "==> Running Claude Code postinstall..."
node "$(npm root -g)/@anthropic-ai/claude-code/install.cjs"

echo ""
echo "==> Testing claude CLI..."
claude --version

echo ""
echo "Done! Run 'claude' to start a session."
