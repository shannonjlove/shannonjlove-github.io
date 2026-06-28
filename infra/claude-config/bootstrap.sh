#!/usr/bin/env bash
# SJL Claude Code Bootstrap
# Sets up Claude Code CLI + memory files on any server (VPS, Oracle, etc.)
# Usage: bash bootstrap.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"
SCRIPTS_DIR="${CLAUDE_DIR}/scripts"

echo "==> SJL Claude Code Bootstrap"
echo "    Repo dir : $REPO_DIR"
echo "    Claude   : $CLAUDE_DIR"
echo ""

# ── 1. Install Node.js + Claude Code ─────────────────────────────────────────
if ! command -v claude &>/dev/null; then
  echo "==> Installing Node.js 20..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs

  echo "==> Installing Claude Code CLI..."
  npm install -g @anthropic-ai/claude-code
else
  echo "==> Claude Code already installed: $(claude --version 2>/dev/null || echo 'unknown')"
fi

# ── 2. Create ~/.claude directories ──────────────────────────────────────────
mkdir -p "$CLAUDE_DIR" "$SCRIPTS_DIR"

# ── 3. Copy CLAUDE.md ────────────────────────────────────────────────────────
echo "==> Installing CLAUDE.md..."
cp "$REPO_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
echo "    Installed: $CLAUDE_DIR/CLAUDE.md"

# ── 4. Copy scripts ──────────────────────────────────────────────────────────
echo "==> Installing scripts..."
cp "$REPO_DIR/scripts/bookstack-inject.sh" "$SCRIPTS_DIR/bookstack-inject.sh"
cp "$REPO_DIR/scripts/raindrop-add-infra.sh" "$SCRIPTS_DIR/raindrop-add-infra.sh"
chmod +x "$SCRIPTS_DIR/"*.sh
echo "    Installed: $SCRIPTS_DIR/"

# ── 5. Create settings.json ──────────────────────────────────────────────────
SETTINGS="$CLAUDE_DIR/settings.json"

if [ -f "$SETTINGS" ]; then
  echo ""
  echo "==> settings.json already exists. Skipping credential setup."
  echo "    Edit manually if needed: $SETTINGS"
else
  echo ""
  echo "==> Creating settings.json (credentials required)"
  echo "    Leave blank to skip a field and fill in later."
  echo ""

  read -rp "  ANTHROPIC_API_KEY         : " ANTHROPIC_API_KEY
  read -rp "  BOOKSTACK_TOKEN_ID        : " BOOKSTACK_TOKEN_ID
  read -rp "  BOOKSTACK_TOKEN_SECRET    : " BOOKSTACK_TOKEN_SECRET
  read -rp "  RAINDROP_TOKEN            : " RAINDROP_TOKEN
  read -rp "  RAINDROP_CLIENT_ID        : " RAINDROP_CLIENT_ID
  read -rp "  RAINDROP_CLIENT_SECRET    : " RAINDROP_CLIENT_SECRET
  read -rp "  RAINDROP_WRITE_TOKEN      : " RAINDROP_WRITE_TOKEN

  cat > "$SETTINGS" <<JSON
{
  "env": {
    "BOOKSTACK_URL": "https://bookstack.shannonjlove.cloud",
    "BOOKSTACK_TOKEN_ID": "${BOOKSTACK_TOKEN_ID}",
    "BOOKSTACK_TOKEN_SECRET": "${BOOKSTACK_TOKEN_SECRET}",
    "RAINDROP_TOKEN": "${RAINDROP_TOKEN}",
    "RAINDROP_CLIENT_ID": "${RAINDROP_CLIENT_ID}",
    "RAINDROP_CLIENT_SECRET": "${RAINDROP_CLIENT_SECRET}",
    "RAINDROP_WRITE_TOKEN": "${RAINDROP_WRITE_TOKEN}",
    "SJL_VPS_IP": "72.61.74.250",
    "SJL_DOMAIN": "shannonjlove.cloud"
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/scripts/bookstack-inject.sh",
            "timeout": 15,
            "statusMessage": "Loading BookStack knowledge base..."
          }
        ]
      }
    ]
  }
}
JSON

  chmod 600 "$SETTINGS"

  # Set ANTHROPIC_API_KEY in shell profile if provided
  if [ -n "${ANTHROPIC_API_KEY}" ]; then
    PROFILE="${HOME}/.bashrc"
    if ! grep -q "ANTHROPIC_API_KEY" "$PROFILE" 2>/dev/null; then
      echo "export ANTHROPIC_API_KEY='${ANTHROPIC_API_KEY}'" >> "$PROFILE"
      echo "    Added ANTHROPIC_API_KEY to $PROFILE"
    fi
    export ANTHROPIC_API_KEY
  fi

  echo "    Created: $SETTINGS"
fi

# ── 6. Install jq if missing (needed by bookstack-inject.sh) ─────────────────
if ! command -v jq &>/dev/null; then
  echo "==> Installing jq..."
  apt-get install -y jq
fi

echo ""
echo "Done! Run 'claude' to start a session."
echo "  Memory  : $CLAUDE_DIR/CLAUDE.md"
echo "  Settings: $SETTINGS"
echo "  Scripts : $SCRIPTS_DIR/"
