#!/bin/bash
# rclone-config-deploy.sh — Write all authorized cloud storage remotes to rclone.conf
# Run on Hostinger VPS as root: bash rclone-config-deploy.sh
#
# REQUIRES: /etc/sjl-rclone-tokens.env  (never committed to git)
# See: scripts/vps-fix/rclone-tokens.env.example for format
#
# Remotes configured:
#   [idrive-primary]  — iDrive E2 S3 (primary storage, static credentials)
#   [dropbox-fcpx]    — Dropbox FCPXServerSJL@gmail.com (OAuth token)
#   [dropbox-sjl]     — Dropbox shannonjlove@mac.com (OAuth token)
#   [pcloud-sjl]      — pCloud SJL account (OAuth token)

set -euo pipefail
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERR]${NC} $*"; }
log()  { echo -e "${CYAN}[$(date +%T)]${NC} $*"; }
hdr()  { echo -e "\n${BOLD}${CYAN}━━━ $* ━━━${NC}"; }

TOKENS_FILE="${SJL_TOKENS_FILE:-/etc/sjl-rclone-tokens.env}"
RCLONE_CONF="${RCLONE_CONFIG:-/root/.config/rclone/rclone.conf}"

# ─────────────────────────────────────────────────────────────────────────────
# Load tokens
# ─────────────────────────────────────────────────────────────────────────────
hdr "Loading Tokens"

if [[ ! -f "$TOKENS_FILE" ]]; then
    err "Tokens file not found: $TOKENS_FILE"
    echo ""
    echo "Create it with your OAuth tokens (see rclone-tokens.env.example):"
    echo "  nano $TOKENS_FILE && chmod 600 $TOKENS_FILE"
    echo ""
    echo "Or pass a custom path:"
    echo "  SJL_TOKENS_FILE=/path/to/tokens.env bash rclone-config-deploy.sh"
    exit 1
fi

# shellcheck disable=SC1090
source "$TOKENS_FILE"
ok "Loaded tokens from $TOKENS_FILE"

# Validate required variables
MISSING=()
[[ -z "${DROPBOX_FCPX_TOKEN:-}" ]] && MISSING+=("DROPBOX_FCPX_TOKEN")
[[ -z "${DROPBOX_SJL_TOKEN:-}" ]]  && MISSING+=("DROPBOX_SJL_TOKEN")
[[ -z "${PCLOUD_TOKEN:-}" ]]        && MISSING+=("PCLOUD_TOKEN")

if [[ ${#MISSING[@]} -gt 0 ]]; then
    err "Missing variables in $TOKENS_FILE: ${MISSING[*]}"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# Backup and clean existing config
# ─────────────────────────────────────────────────────────────────────────────
hdr "Preparing rclone Config"

mkdir -p "$(dirname "$RCLONE_CONF")"
BACKUP="${RCLONE_CONF}.bak.$(date +%Y%m%d-%H%M%S)"

if [[ -f "$RCLONE_CONF" ]]; then
    cp "$RCLONE_CONF" "$BACKUP"
    ok "Backed up → $BACKUP"

    # Remove stale/invalid remotes we're replacing
    python3 - <<PYEOF
import re, os

conf_path = os.environ.get("RCLONE_CONFIG", os.path.expanduser("~/.config/rclone/rclone.conf"))
with open(conf_path) as f:
    content = f.read()

to_remove = ["mediafire-sjl", "idrive-primary", "dropbox-fcpx", "dropbox-sjl", "pcloud-sjl"]
for remote in to_remove:
    before = content
    content = re.sub(r'\[' + re.escape(remote) + r'\][^\[]*', '', content)
    if content != before:
        print(f"Removed [{remote}]")

with open(conf_path, 'w') as f:
    f.write(content.strip() + '\n')
PYEOF
else
    log "No existing config — creating fresh"
    touch "$RCLONE_CONF"
    chmod 600 "$RCLONE_CONF"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Write remotes
# ─────────────────────────────────────────────────────────────────────────────
hdr "Writing Remotes"

cat >> "$RCLONE_CONF" << REMOTES

[idrive-primary]
type = s3
provider = Other
env_auth = false
access_key_id = hNOOh0odHmPwKt9xDbll
secret_access_key = w8X3Ubjfp6rnGzjoFjBv1kwpdMpn9MxzbQcjozA6
endpoint = https://p3h2.va.idrivee2-48.com
region = us-east-1

[dropbox-fcpx]
type = dropbox
token = ${DROPBOX_FCPX_TOKEN}

[dropbox-sjl]
type = dropbox
token = ${DROPBOX_SJL_TOKEN}

[pcloud-sjl]
type = pcloud
token = ${PCLOUD_TOKEN}
hostname = api.pcloud.com
REMOTES

ok "Wrote 4 remotes to $RCLONE_CONF"

# ─────────────────────────────────────────────────────────────────────────────
# Verify
# ─────────────────────────────────────────────────────────────────────────────
hdr "Verifying Remotes"

echo ""
log "Configured remotes:"
rclone listremotes | sed 's/^/  /'

echo ""
log "Testing idrive-primary..."
if rclone lsd idrive-primary: --max-depth 1 2>/dev/null | head -5; then
    ok "idrive-primary — reachable"
else
    warn "idrive-primary — could not list (check endpoint/keys)"
fi

for remote in dropbox-fcpx dropbox-sjl pcloud-sjl; do
    echo ""
    log "Testing $remote..."
    if rclone lsd "${remote}:" --max-depth 1 2>/dev/null | head -3; then
        ok "$remote — reachable"
    else
        warn "$remote — unreachable (token may have expired; rclone auto-refreshes on next use)"
    fi
done

echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  rclone Config Deploy Complete${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Config: $RCLONE_CONF"
[[ -f "$BACKUP" ]] && echo "  Backup: $BACKUP"
echo ""
echo "  Next steps:"
echo "  1. Run fix-routing.sh if not already done"
echo "  2. Add MEDIAFIRE_PASSWORD to /etc/sjl-inbox-sync.env"
echo "  3. Trigger first sync: /opt/sjl-scripts/inbox-routing/inbox-sync.sh"
echo ""
