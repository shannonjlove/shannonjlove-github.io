#!/usr/bin/env bash
# =============================================================================
# PROMPT ROUTER INSTALLER — shannonjlove.cloud
# Installs NadirClaw — self-hosted LLM prompt router & cost optimizer.
# NadirClaw/NadirClaw (https://github.com/NadirRouter/NadirClaw)
#
# Routes every prompt to the cheapest model that can answer it reliably.
# Simple prompts → Ollama phi3:mini (local, zero API cost)
# Complex prompts → Claude API (premium, only when needed)
# Estimated savings: 40–70% on AI API costs.
#
# REQUIREMENTS:
#   - Python 3.10+
#   - Ollama running at localhost:11434 (for local model tier)
#   - ANTHROPIC_API_KEY (for Claude tier — set in .env)
#
# SJL DEFAULTS (configured in /opt/prompt-router/.env):
#   SIMPLE:  ollama/phi3:mini    (3 GB RAM, ~10s/request — fast local)
#   COMPLEX: claude-sonnet-4-20250514  (via ANTHROPIC_API_KEY)
#   PORT:    8856
#   PM2:     prompt-router
#
# Usage: bash scripts/install/install-prompt-router.sh
#
# After install:
#   # Start:  pm2 start prompt-router
#   # Stop:   pm2 stop prompt-router
#   # Status: nadirclaw status
#   # Test:   nadirclaw classify "what is 2+2?"
#   # Test:   nadirclaw classify "refactor the auth module to use JWT"
#
# Integration with Claude Code (as OpenAI-compatible proxy):
#   Add to ~/.claude/settings.json or .mcp.json:
#     "ANTHROPIC_BASE_URL": "http://localhost:8856"
#
# Integration with n8n (replaces Ollama node):
#   OpenAI node → base URL: http://localhost:8856
#   Model: claude-sonnet-4-20250514 (NadirClaw decides actual model used)
# =============================================================================

set -euo pipefail

REPO="https://github.com/NadirRouter/NadirClaw.git"
INSTALL_DIR="/opt/prompt-router"
PM2_NAME="prompt-router"
PORT="${NADIRCLAW_PORT:-8856}"
SIMPLE_MODEL="${NADIRCLAW_SIMPLE_MODEL:-ollama/phi3:mini}"
COMPLEX_MODEL="${NADIRCLAW_COMPLEX_MODEL:-claude-sonnet-4-20250514}"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

# ---- Python check ----------------------------------------------------------
PYTHON=""
for py in python3.11 python3.10 python3; do
    if command -v "$py" &>/dev/null; then
        VER=$("$py" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJ=$("$py" -c 'import sys; print(sys.version_info.major)')
        MIN=$("$py" -c 'import sys; print(sys.version_info.minor)')
        if [[ "$MAJ" -gt 3 ]] || [[ "$MAJ" -eq 3 && "$MIN" -ge 10 ]]; then
            PYTHON="$py"
            log "Python: $py ($VER)"
            break
        fi
    fi
done
[[ -z "$PYTHON" ]] && die "Python 3.10+ required. Install: sudo apt install python3.11"

# ---- Clone or update -------------------------------------------------------
if [[ -d "$INSTALL_DIR/.git" ]]; then
    log "Updating existing NadirClaw at $INSTALL_DIR..."
    # Preserve .env if it exists — it may have user's API keys
    if [[ -f "$INSTALL_DIR/.env" ]]; then
        cp "$INSTALL_DIR/.env" /tmp/nadirclaw-env-backup.tmp
    fi
    git -C "$INSTALL_DIR" pull --ff-only origin main 2>/dev/null \
        || log "WARN: could not pull — using existing source"
    if [[ -f /tmp/nadirclaw-env-backup.tmp ]]; then
        cp /tmp/nadirclaw-env-backup.tmp "$INSTALL_DIR/.env"
        rm /tmp/nadirclaw-env-backup.tmp
    fi
else
    log "Cloning NadirClaw → $INSTALL_DIR..."
    git clone --depth=1 "$REPO" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
log "Source: $INSTALL_DIR"

# ---- Python virtual environment --------------------------------------------
if [[ ! -d "$INSTALL_DIR/venv" ]]; then
    log "Creating Python venv..."
    "$PYTHON" -m venv "$INSTALL_DIR/venv"
fi

log "Installing NadirClaw and dependencies..."
"$INSTALL_DIR/venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install --quiet -e "$INSTALL_DIR"

# ---- Write .env (SJL defaults, preserve existing) --------------------------
if [[ ! -f "$INSTALL_DIR/.env" ]]; then
    log "Writing SJL default .env..."
    cat > "$INSTALL_DIR/.env" <<EOF
# NadirClaw — SJL Configuration
# Prompt router for shannonjlove.cloud
# Simple prompts → Ollama (local, zero cost)
# Complex prompts → Claude API (premium, when needed)

# ── Tier models ──────────────────────────────────────────────
NADIRCLAW_SIMPLE_MODEL=$SIMPLE_MODEL
NADIRCLAW_COMPLEX_MODEL=$COMPLEX_MODEL

# ── Ollama (local tier) ──────────────────────────────────────
OLLAMA_API_BASE=http://localhost:11434

# ── Claude API key (premium tier) ───────────────────────────
# ANTHROPIC_API_KEY=sk-ant-...

# ── Server ──────────────────────────────────────────────────
NADIRCLAW_PORT=$PORT
NADIRCLAW_CONFIDENCE_THRESHOLD=0.06
NADIRCLAW_LOG_DIR=$INSTALL_DIR/logs

# ── Fallback chain ──────────────────────────────────────────
# If phi3:mini fails, fall back to mistral:7b before escalating to Claude
NADIRCLAW_SIMPLE_FALLBACK=ollama/mistral:7b
EOF
    log ".env written (add ANTHROPIC_API_KEY to enable Claude tier)"
else
    log ".env already exists — preserving existing credentials"
fi

# ---- CLI wrapper -----------------------------------------------------------
mkdir -p "$INSTALL_DIR/bin"
cat > "$INSTALL_DIR/bin/nadirclaw" <<WRAPPER
#!/bin/sh
export NADIRCLAW_LOG_DIR="$INSTALL_DIR/logs"
exec "$INSTALL_DIR/venv/bin/nadirclaw" "\$@"
WRAPPER
chmod +x "$INSTALL_DIR/bin/nadirclaw"
ln -sf "$INSTALL_DIR/bin/nadirclaw" /usr/local/bin/nadirclaw 2>/dev/null \
    || log "WARN: could not symlink to /usr/local/bin/nadirclaw (need root?)"

# ---- pm2 deployment --------------------------------------------------------
if ! command -v pm2 &>/dev/null; then
    log "Installing pm2..."
    npm install -g pm2 2>/dev/null || log "WARN: npm not found — skipping pm2 install"
fi

if command -v pm2 &>/dev/null; then
    mkdir -p "$INSTALL_DIR/logs"

    if pm2 list 2>/dev/null | grep -q "$PM2_NAME"; then
        log "Restarting pm2 process '$PM2_NAME'..."
        pm2 restart "$PM2_NAME"
    else
        log "Starting NadirClaw via pm2 on port $PORT..."
        # Load .env and start nadirclaw serve
        (
            set -a
            # shellcheck disable=SC1090
            source "$INSTALL_DIR/.env" 2>/dev/null || true
            set +a
            pm2 start "$INSTALL_DIR/bin/nadirclaw" \
                --name "$PM2_NAME" \
                -- serve --port "$PORT"
        )
    fi
    pm2 save
    log "NadirClaw running as pm2 process: $PM2_NAME"
else
    log ""
    log "pm2 not available. Start manually with:"
    log "  source $INSTALL_DIR/.env && $INSTALL_DIR/bin/nadirclaw serve --port $PORT"
fi

# ---- Verify Ollama model is available --------------------------------------
OLLAMA_MODEL="${SIMPLE_MODEL#ollama/}"   # strip "ollama/" prefix
if command -v ollama &>/dev/null; then
    if ollama list 2>/dev/null | grep -q "^${OLLAMA_MODEL}"; then
        log "Ollama model '$OLLAMA_MODEL' is available."
    else
        log "WARN: Ollama model '$OLLAMA_MODEL' not found locally."
        log "      Pull it with: ollama pull $OLLAMA_MODEL"
    fi
fi

# ---- Usage summary ---------------------------------------------------------
echo ""
echo "================================================================"
echo "NadirClaw prompt router installed at: $INSTALL_DIR"
echo "Listening on: http://localhost:$PORT (OpenAI-compatible API)"
echo ""
echo "SJL routing tiers:"
echo "  SIMPLE  → $SIMPLE_MODEL (Ollama, local, zero cost)"
echo "  COMPLEX → $COMPLEX_MODEL (Claude API)"
echo ""
echo "Test classification:"
echo "  nadirclaw classify 'what is 2+2?'              → should route SIMPLE"
echo "  nadirclaw classify 'refactor auth module JWT'  → should route COMPLEX"
echo "  nadirclaw status"
echo ""
echo "API endpoint (OpenAI-compatible):"
echo "  http://localhost:$PORT/v1/chat/completions"
echo ""
echo "Claude Code integration (add to ~/.claude/settings.json):"
echo '  "env": { "ANTHROPIC_BASE_URL": "http://localhost:'"$PORT"'" }'
echo ""
echo "n8n integration:"
echo "  OpenAI node → Base URL: http://localhost:$PORT"
echo "  Model: claude-sonnet-4-20250514 (NadirClaw decides actual model)"
echo ""
echo "IMPORTANT: Set your Anthropic API key in $INSTALL_DIR/.env"
echo "  ANTHROPIC_API_KEY=sk-ant-..."
echo "  Then: pm2 restart $PM2_NAME"
echo ""
echo "Ollama model for SIMPLE tier:"
echo "  ollama pull $OLLAMA_MODEL"
echo "================================================================"
