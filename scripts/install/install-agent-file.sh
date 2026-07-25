#!/usr/bin/env bash
# =============================================================================
# AGENT FILE INSTALLER — shannonjlove.cloud
# Clones and deploys shannonjlove/agent-file — the Letta .af open standard
# registry for stateful AI agents.
#
# The .af format packages an AI agent's full state: system prompt, memory,
# tool configs, and LLM settings into a portable file for Letta/MemGPT.
#
# Usage: bash scripts/install/install-agent-file.sh
# After install: http://localhost:3033 (or configured domain)
# =============================================================================

set -euo pipefail

REPO="https://github.com/shannonjlove/agent-file.git"
INSTALL_DIR="/opt/agent-file"
PORT="${AGENT_FILE_PORT:-3033}"
PM2_NAME="agent-file"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

# ---- Node.js check ---------------------------------------------------------
if ! command -v node &>/dev/null; then
    log "Node.js not found. Installing via NodeSource..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi
log "Node: $(node --version) | npm: $(npm --version)"

# ---- Clone or update -------------------------------------------------------
if [[ -d "$INSTALL_DIR/.git" ]]; then
    log "Updating $INSTALL_DIR..."
    git -C "$INSTALL_DIR" pull --ff-only origin main 2>/dev/null \
        || git -C "$INSTALL_DIR" pull --ff-only origin master 2>/dev/null
else
    log "Cloning agent-file → $INSTALL_DIR..."
    git clone --depth=1 "$REPO" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ---- Install dependencies + build ------------------------------------------
log "Installing npm dependencies..."
npm ci --prefer-offline 2>/dev/null || npm install

log "Building Next.js app..."
PORT="$PORT" npm run build

# ---- Deploy via pm2 --------------------------------------------------------
if ! command -v pm2 &>/dev/null; then
    log "Installing pm2..."
    npm install -g pm2
fi

if pm2 list 2>/dev/null | grep -q "$PM2_NAME"; then
    log "Restarting pm2 process $PM2_NAME..."
    pm2 restart "$PM2_NAME"
else
    log "Starting agent-file on port $PORT..."
    PORT="$PORT" pm2 start npm --name "$PM2_NAME" -- start
fi

pm2 save
log "agent-file deployed → port $PORT"

# ---- nginx snippet (print; add manually) -----------------------------------
echo ""
echo "================================================================"
echo "agent-file is running on port $PORT."
echo ""
echo "nginx snippet for agents.shannonjlove.cloud:"
echo ""
cat <<NGINX
server {
    listen 443 ssl;
    server_name agents.shannonjlove.cloud;
    location / {
        proxy_pass http://127.0.0.1:${PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
NGINX
echo "================================================================"
echo ""
echo ".af file format documentation: https://github.com/shannonjlove/agent-file"
echo "Deploy an agent to Letta: https://app.letta.com (import .af file)"
