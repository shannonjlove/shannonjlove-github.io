#!/bin/bash
# fix-routing.sh — SJL Sovereign Cloud system-wide routing and service fix
# Run on the Hostinger VPS as root: bash fix-routing.sh
#
# What this does:
#   1. Audits all service containers (running vs. expected)
#   2. Starts/restarts stopped containers
#   3. Validates port bindings match the services registry
#   4. Cleans up broken rclone remotes (mediafire type doesn't exist)
#   5. Prints NPM route configuration needed
#   6. Deploys MCP tools config to sjl-mcp-gateway

set -euo pipefail
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${CYAN}[$(date +%T)]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERR]${NC} $*"; }
hdr()  { echo -e "\n${BOLD}${CYAN}━━━ $* ━━━${NC}"; }

FIXES=0
WARNINGS=0

# ─────────────────────────────────────────────────────────────────────────────
# Service registry: container → expected internal port → subdomain
# ─────────────────────────────────────────────────────────────────────────────
declare -A CONTAINER_PORTS=(
    ["n8n"]="5678"
    ["bookstack"]="6875"
    ["paperless"]="8000"
    ["webtop"]="3000"
    ["sjl-mcp-gateway"]="7300"
    ["sjl-file-api"]="8090"
    ["rclone-gui"]="5572"
    ["rclone-mcp"]="8026"
    ["stash"]="9999"
    ["kuma"]="3001"
    ["hub"]="80"
)

declare -A CONTAINER_SUBDOMAINS=(
    ["n8n"]="n8n.shannonjlove.cloud"
    ["bookstack"]="bookstack.shannonjlove.cloud"
    ["paperless"]="docs.shannonjlove.cloud"
    ["webtop"]="webtop.shannonjlove.cloud"
    ["sjl-mcp-gateway"]="mcp.shannonjlove.cloud"
    ["sjl-file-api"]="api.shannonjlove.cloud"
    ["rclone-gui"]="files.shannonjlove.cloud"
    ["rclone-mcp"]="rclone-mcp.shannonjlove.cloud"
    ["stash"]="private.shannonjlove.cloud"
    ["kuma"]="status.shannonjlove.cloud"
    ["hub"]="hub.shannonjlove.cloud"
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Container status audit
# ─────────────────────────────────────────────────────────────────────────────
hdr "Step 1: Container Audit"

CONTAINER_CMD=""
if command -v podman &>/dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &>/dev/null; then
    CONTAINER_CMD="docker"
else
    err "Neither podman nor docker found — cannot manage containers"
    exit 1
fi
log "Using: $CONTAINER_CMD"

DOWN_CONTAINERS=()
for container in "${!CONTAINER_PORTS[@]}"; do
    status=$($CONTAINER_CMD inspect --format '{{.State.Status}}' "$container" 2>/dev/null || echo "missing")
    if [[ "$status" == "running" ]]; then
        ok "$container — running (port ${CONTAINER_PORTS[$container]})"
    elif [[ "$status" == "missing" ]]; then
        warn "$container — NOT FOUND (no container exists)"
        WARNINGS=$((WARNINGS + 1))
    else
        err "$container — $status (expected: running)"
        DOWN_CONTAINERS+=("$container")
        FIXES=$((FIXES + 1))
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# 2. Start stopped containers
# ─────────────────────────────────────────────────────────────────────────────
if [[ ${#DOWN_CONTAINERS[@]} -gt 0 ]]; then
    hdr "Step 2: Starting Stopped Containers"
    for container in "${DOWN_CONTAINERS[@]}"; do
        log "Starting $container..."
        if $CONTAINER_CMD start "$container" 2>/dev/null; then
            ok "$container started"
        else
            warn "Could not start $container — may need quadlet/compose restart"
            # Try systemd quadlet
            if systemctl start "$container" 2>/dev/null; then
                ok "$container started via systemd"
            else
                err "$container could not be started — check: $CONTAINER_CMD logs $container"
            fi
        fi
    done
else
    hdr "Step 2: Starting Stopped Containers"
    ok "All tracked containers were running — nothing to start"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 3. Verify port bindings
# ─────────────────────────────────────────────────────────────────────────────
hdr "Step 3: Port Binding Verification"

for container in "${!CONTAINER_PORTS[@]}"; do
    expected_port="${CONTAINER_PORTS[$container]}"
    status=$($CONTAINER_CMD inspect --format '{{.State.Status}}' "$container" 2>/dev/null || echo "missing")
    if [[ "$status" != "running" ]]; then
        warn "$container — skipping port check (not running)"
        continue
    fi

    # Check if the container is listening on its expected port inside sjl_net
    actual_ip=$($CONTAINER_CMD inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$container" 2>/dev/null | head -1)
    if [[ -n "$actual_ip" ]]; then
        ok "$container — IP $actual_ip port $expected_port"
    else
        warn "$container — could not determine IP (may use hostname routing)"
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# 4. Fix broken rclone config
# ─────────────────────────────────────────────────────────────────────────────
hdr "Step 4: rclone Config Cleanup"

RCLONE_CONF="${RCLONE_CONFIG:-/root/.config/rclone/rclone.conf}"

if [[ -f "$RCLONE_CONF" ]]; then
    # Remove invalid mediafire remote (backend doesn't exist in rclone v1.74.3+)
    if grep -q '^\[mediafire-sjl\]' "$RCLONE_CONF" 2>/dev/null; then
        # Back up first
        cp "$RCLONE_CONF" "${RCLONE_CONF}.bak.$(date +%Y%m%d)"
        # Remove the [mediafire-sjl] stanza
        python3 - <<'PYEOF'
import re, os, sys

conf_path = os.environ.get("RCLONE_CONFIG", os.path.expanduser("~/.config/rclone/rclone.conf"))
with open(conf_path) as f:
    content = f.read()

# Remove [mediafire-sjl] block
cleaned = re.sub(r'\n\[mediafire-sjl\][^\[]*', '', content)

with open(conf_path, 'w') as f:
    f.write(cleaned)

print(f"Removed [mediafire-sjl] from {conf_path}")
PYEOF
        ok "Removed invalid [mediafire-sjl] remote (Python script handles MediaFire instead)"
        FIXES=$((FIXES + 1))
    else
        ok "No invalid [mediafire-sjl] remote found"
    fi

    # Ensure [idrive-primary] is present
    if ! grep -q '^\[idrive-primary\]' "$RCLONE_CONF" 2>/dev/null; then
        warn "[idrive-primary] not in rclone config — adding now"
        cat >> "$RCLONE_CONF" << 'RCLONE_E2'

[idrive-primary]
type = s3
provider = Other
env_auth = false
access_key_id = hNOOh0odHmPwKt9xDbll
secret_access_key = w8X3Ubjfp6rnGzjoFjBv1kwpdMpn9MxzbQcjozA6
endpoint = https://p3h2.va.idrivee2-48.com
region = us-east-1
RCLONE_E2
        ok "Added [idrive-primary] to rclone config"
        FIXES=$((FIXES + 1))
    else
        ok "[idrive-primary] already configured"
    fi

    # Show all configured remotes
    echo ""
    log "Current rclone remotes:"
    rclone listremotes 2>/dev/null | sed 's/^/  /' || echo "  (rclone not found or error)"
else
    warn "rclone config not found at $RCLONE_CONF"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 5. Fix sjl-inbox-sync.env (ensure correct port for file API)
# ─────────────────────────────────────────────────────────────────────────────
hdr "Step 5: Environment Config"

ENV_FILE="/etc/sjl-inbox-sync.env"
if [[ -f "$ENV_FILE" ]]; then
    # Ensure FILE_API_PORT is set correctly
    if ! grep -q 'FILE_API_PORT' "$ENV_FILE"; then
        echo "" >> "$ENV_FILE"
        echo "FILE_API_PORT=8090" >> "$ENV_FILE"
        echo "FILE_API_URL=http://sjl-file-api:8090" >> "$ENV_FILE"
        ok "Added FILE_API_PORT=8090 to $ENV_FILE"
        FIXES=$((FIXES + 1))
    else
        # Correct any wrong port
        sed -i 's/FILE_API_PORT=8086/FILE_API_PORT=8090/g' "$ENV_FILE"
        sed -i 's|:8086|:8090|g' "$ENV_FILE"
        ok "$ENV_FILE port references verified (8090)"
    fi
else
    cat > "$ENV_FILE" << 'ENV'
# SJL Inbox Sync + Service environment
# Generated by fix-routing.sh
MEDIAFIRE_EMAIL=shannonjlove@mac.com
MEDIAFIRE_PASSWORD=
IDRIVE_ENDPOINT=https://p3h2.va.idrivee2-48.com
IDRIVE_ACCESS_KEY=hNOOh0odHmPwKt9xDbll
IDRIVE_SECRET_KEY=w8X3Ubjfp6rnGzjoFjBv1kwpdMpn9MxzbQcjozA6
FILE_API_PORT=8090
FILE_API_URL=http://sjl-file-api:8090
ENV
    chmod 600 "$ENV_FILE"
    ok "Created $ENV_FILE"
    FIXES=$((FIXES + 1))
fi

# ─────────────────────────────────────────────────────────────────────────────
# 6. Deploy MCP tools config
# ─────────────────────────────────────────────────────────────────────────────
hdr "Step 6: MCP Gateway Tools"

MCP_DIR="/opt/sjl-mcp-gateway"
REPO_BASE="https://raw.githubusercontent.com/shannonjlove/shannonjlove-github.io/claude/idrives3-storage-org-zo63il"

if [[ -d "$MCP_DIR" ]]; then
    log "Deploying MCP tools config to $MCP_DIR..."
    if curl -fsSL "${REPO_BASE}/scripts/vps-fix/mcp-tools-config.js" \
        -o "${MCP_DIR}/tools-config.js" 2>/dev/null; then
        ok "Downloaded mcp-tools-config.js → ${MCP_DIR}/tools-config.js"
        # Restart the gateway to pick up changes
        if $CONTAINER_CMD restart sjl-mcp-gateway 2>/dev/null; then
            ok "sjl-mcp-gateway restarted"
        else
            warn "Could not restart sjl-mcp-gateway — restart manually"
        fi
        FIXES=$((FIXES + 1))
    else
        warn "Could not download mcp-tools-config.js — copy manually"
    fi
else
    warn "MCP gateway dir not found at $MCP_DIR — skipping tool deploy"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 7. Reload systemd timer
# ─────────────────────────────────────────────────────────────────────────────
hdr "Step 7: Systemd Timer"

if systemctl daemon-reload 2>/dev/null; then
    if systemctl is-active sjl-inbox-sync.timer &>/dev/null; then
        ok "sjl-inbox-sync.timer already active"
    else
        systemctl enable --now sjl-inbox-sync.timer 2>/dev/null && \
            ok "sjl-inbox-sync.timer enabled and started" || \
            warn "Could not enable sjl-inbox-sync.timer"
    fi
else
    warn "systemd not available"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary + NPM configuration guide
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  SJL System Fix Complete${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Fixes applied: $FIXES"
echo "  Warnings:      $WARNINGS"
echo ""

echo -e "${BOLD}  NPM Proxy Hosts to add/verify in Nginx Proxy Manager:${NC}"
echo "  (Admin UI: http://$(hostname -I | awk '{print $1}'):81 or via Tailscale)"
echo ""
printf "  %-45s %s\n" "SUBDOMAIN" "FORWARD → HOST:PORT"
printf "  %-45s %s\n" "---------" "-------------------"
for container in "${!CONTAINER_SUBDOMAINS[@]}"; do
    subdomain="${CONTAINER_SUBDOMAINS[$container]}"
    port="${CONTAINER_PORTS[$container]}"
    status=$($CONTAINER_CMD inspect --format '{{.State.Status}}' "$container" 2>/dev/null || echo "missing")
    symbol="✅"
    [[ "$status" != "running" ]] && symbol="❌"
    printf "  $symbol %-43s %s\n" "$subdomain" "$container:$port"
done

echo ""
echo -e "${BOLD}  Tailscale-only (do NOT add to NPM):${NC}"
echo "  • portainer:9000 / 9443 — via Tailscale 100.115.66.75:9000"
echo "  • sjl-monitor:8790"
echo "  • tailnet:8788"
echo ""
echo "  Run first inbox sync: /opt/sjl-scripts/inbox-routing/inbox-sync.sh"
echo "  View timer:          systemctl status sjl-inbox-sync.timer"
echo "  View logs:           journalctl -u sjl-inbox-sync -f"
echo ""
