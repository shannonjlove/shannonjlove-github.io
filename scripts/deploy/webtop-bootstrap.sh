#!/bin/bash
# webtop-bootstrap.sh
# One-shot install + deploy of SJL Inbox Routing on the WebTop.
# Run this in the WebTop terminal: bash webtop-bootstrap.sh
#
# What it does:
#   1. Installs rclone (if not present)
#   2. Configures iDrive E2 remote
#   3. Opens browser OAuth for Dropbox (FCPXServerSJL + shannonjlove accounts)
#   4. Opens browser OAuth for pCloud
#   5. Deploys inbox-sync.sh + mediafire-inbox-sync.py to /opt/sjl-scripts/
#   6. Installs systemd timer (15-min sync)
#   7. Runs first sync immediately

set -euo pipefail
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

log()  { echo -e "${CYAN}[$(date +%T)]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERR]${NC} $*"; }

SCRIPTS_DIR="/opt/sjl-scripts/inbox-routing"
RCLONE_CONF="${RCLONE_CONFIG:-/root/.config/rclone/rclone.conf}"
REPO_BASE="https://raw.githubusercontent.com/shannonjlove/shannonjlove-github.io/claude/idrives3-storage-org-zo63il"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Install rclone
# ─────────────────────────────────────────────────────────────────────────────
log "Step 1/7 — rclone"

if command -v rclone &>/dev/null; then
    ok "rclone $(rclone --version | head -1 | awk '{print $2}') already installed"
else
    log "Installing rclone..."
    if command -v apt-get &>/dev/null; then
        apt-get update -qq && apt-get install -y -q rclone
    else
        curl -fsSL https://rclone.org/install.sh | bash
    fi
    ok "rclone installed: $(rclone --version | head -1)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 2. Configure iDrive E2 primary remote
# ─────────────────────────────────────────────────────────────────────────────
log "Step 2/7 — iDrive E2 remote"
mkdir -p "$(dirname "$RCLONE_CONF")"

if grep -q '^\[idrive-primary\]' "$RCLONE_CONF" 2>/dev/null; then
    ok "idrive-primary already in rclone config"
else
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
fi

# Verify connectivity
if rclone lsd idrive-primary: 2>/dev/null | grep -q inbox-idrive-e2; then
    ok "iDrive E2 connection verified — inbox-idrive-e2 bucket accessible"
else
    warn "Could not verify iDrive E2 — check network and credentials"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 3. OAuth — Dropbox FCPXServerSJL
# ─────────────────────────────────────────────────────────────────────────────
log "Step 3/7 — Dropbox OAuth (FCPXServerSJL@gmail.com)"

if grep -q '^\[dropbox-fcpx\]' "$RCLONE_CONF" 2>/dev/null; then
    ok "dropbox-fcpx already configured — skipping OAuth"
else
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  DROPBOX OAUTH — FCPXServerSJL@gmail.com${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "  A browser window will open. Log in with FCPXServerSJL@gmail.com"
    echo "  and click Allow. Return here when done."
    echo ""
    read -p "  Press ENTER to open Dropbox auth browser... " _

    rclone config create dropbox-fcpx dropbox \
        --config "$RCLONE_CONF" \
        2>&1 | tail -5 || {
        warn "rclone config create failed — trying interactive config"
        rclone config --config "$RCLONE_CONF" <<< $'n\ndropbox-fcpx\ndropbox\n\n\ny\n\n\ny\n'
    }

    if grep -q '^\[dropbox-fcpx\]' "$RCLONE_CONF" 2>/dev/null; then
        ok "dropbox-fcpx configured"
    else
        warn "dropbox-fcpx OAuth may not have completed — run manually: rclone config"
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 4. OAuth — Dropbox shannonjlove
# ─────────────────────────────────────────────────────────────────────────────
log "Step 4/7 — Dropbox OAuth (shannonjlove@mac.com)"

if grep -q '^\[dropbox-sjl\]' "$RCLONE_CONF" 2>/dev/null; then
    ok "dropbox-sjl already configured — skipping OAuth"
else
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  DROPBOX OAUTH — shannonjlove@mac.com${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "  Log in with shannonjlove@mac.com and click Allow."
    echo ""
    read -p "  Press ENTER to open Dropbox auth browser... " _

    rclone config create dropbox-sjl dropbox \
        --config "$RCLONE_CONF" \
        2>&1 | tail -5 || true

    if grep -q '^\[dropbox-sjl\]' "$RCLONE_CONF" 2>/dev/null; then
        ok "dropbox-sjl configured"
    else
        warn "dropbox-sjl OAuth may not have completed"
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 5. OAuth — pCloud
# ─────────────────────────────────────────────────────────────────────────────
log "Step 5/7 — pCloud OAuth"

if grep -q '^\[pcloud-sjl\]' "$RCLONE_CONF" 2>/dev/null; then
    ok "pcloud-sjl already configured — skipping OAuth"
else
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  PCLOUD OAUTH${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "  Log in with your pCloud credentials. If 2FA is required, enter the code."
    echo ""
    read -p "  Press ENTER to open pCloud auth browser... " _

    rclone config create pcloud-sjl pcloud \
        --config "$RCLONE_CONF" \
        2>&1 | tail -5 || true

    if grep -q '^\[pcloud-sjl\]' "$RCLONE_CONF" 2>/dev/null; then
        ok "pcloud-sjl configured"
    else
        warn "pcloud-sjl OAuth may not have completed"
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# 6. Deploy inbox routing scripts
# ─────────────────────────────────────────────────────────────────────────────
log "Step 6/7 — Deploy scripts to $SCRIPTS_DIR"

mkdir -p "$SCRIPTS_DIR"

# Download scripts from git repo
for script in inbox-sync.sh mediafire-inbox-sync.py setup-rclone-idrive.sh; do
    target="$SCRIPTS_DIR/$script"
    if curl -fsSL "${REPO_BASE}/scripts/inbox-routing/${script}" -o "$target" 2>/dev/null; then
        ok "Downloaded: $script"
    else
        warn "Could not download $script from repo — copy manually from scripts/inbox-routing/"
    fi
done

chmod +x "$SCRIPTS_DIR/inbox-sync.sh" "$SCRIPTS_DIR/setup-rclone-idrive.sh" 2>/dev/null || true

# Write MediaFire env file
if [[ ! -f /etc/sjl-inbox-sync.env ]]; then
    cat > /etc/sjl-inbox-sync.env << 'ENV'
# SJL Inbox Sync environment
# Fill in MediaFire credentials if using mediafire-inbox-sync.py
MEDIAFIRE_EMAIL=shannonjlove@mac.com
MEDIAFIRE_PASSWORD=
IDRIVE_ENDPOINT=https://p3h2.va.idrivee2-48.com
IDRIVE_ACCESS_KEY=hNOOh0odHmPwKt9xDbll
IDRIVE_SECRET_KEY=w8X3Ubjfp6rnGzjoFjBv1kwpdMpn9MxzbQcjozA6
ENV
    chmod 600 /etc/sjl-inbox-sync.env
    ok "Created /etc/sjl-inbox-sync.env"
fi

# Install systemd units
for unit in sjl-inbox-sync.service sjl-inbox-sync.timer; do
    if curl -fsSL "${REPO_BASE}/scripts/inbox-routing/${unit}" \
        -o "/etc/systemd/system/${unit}" 2>/dev/null; then
        # Fix ExecStart path
        sed -i "s|/opt/sjl-scripts/inbox-routing/inbox-sync.sh|${SCRIPTS_DIR}/inbox-sync.sh|g" \
            "/etc/systemd/system/${unit}"
        ok "Installed: $unit"
    else
        warn "Could not download $unit — writing inline"

        if [[ "$unit" == "sjl-inbox-sync.service" ]]; then
            cat > /etc/systemd/system/sjl-inbox-sync.service << SVC
[Unit]
Description=SJL Inbox Sync — Route all cloud storage to iDrive E2 inbox
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=root
ExecStart=${SCRIPTS_DIR}/inbox-sync.sh
StandardOutput=journal
StandardError=journal
SyslogIdentifier=sjl-inbox-sync
EnvironmentFile=-/etc/sjl-inbox-sync.env
SVC
        else
            cat > /etc/systemd/system/sjl-inbox-sync.timer << TMR
[Unit]
Description=SJL Inbox Sync Timer — every 15 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
AccuracySec=1min
Persistent=true

[Install]
WantedBy=timers.target
TMR
        fi
        ok "Wrote inline: $unit"
    fi
done

if systemctl daemon-reload 2>/dev/null; then
    systemctl enable --now sjl-inbox-sync.timer 2>/dev/null && \
        ok "systemd timer enabled and started (15-min sync)" || \
        warn "Could not enable systemd timer (container may not have systemd)"
else
    warn "systemd not available — set up a cron job instead:"
    echo "  */15 * * * * root ${SCRIPTS_DIR}/inbox-sync.sh >> /var/log/sjl-inbox-sync/cron.log 2>&1"
    crontab -l 2>/dev/null | grep -q inbox-sync || {
        (crontab -l 2>/dev/null; echo "*/15 * * * * ${SCRIPTS_DIR}/inbox-sync.sh >> /var/log/sjl-inbox-sync/cron.log 2>&1") | crontab -
        ok "Added to crontab: 15-min sync"
    }
fi

# ─────────────────────────────────────────────────────────────────────────────
# 7. First sync run
# ─────────────────────────────────────────────────────────────────────────────
log "Step 7/7 — Running first sync"

echo ""
read -p "Run first inbox sync now? (y/N) " first_run
if [[ "${first_run,,}" == "y" ]]; then
    bash "$SCRIPTS_DIR/inbox-sync.sh"
    ok "First sync complete — check inbox-idrive-e2/01001-uploads/"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  SJL Inbox Routing — Deployment Complete${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "  rclone remotes configured:"
rclone listremotes 2>/dev/null | sed 's/^/    /' || echo "    (none)"

echo ""
echo "  Scripts:      $SCRIPTS_DIR/"
echo "  Config:       $RCLONE_CONF"
echo "  Env file:     /etc/sjl-inbox-sync.env"
echo "  Logs:         /var/log/sjl-inbox-sync/"
echo "  Timer status: $(systemctl is-active sjl-inbox-sync.timer 2>/dev/null || echo 'not running')"
echo ""
echo "  Inbox target: inbox-idrive-e2/01001-uploads/"
echo "  ├── dropbox-fcpx/"
echo "  ├── dropbox-sjl/"
echo "  ├── pcloud/"
echo "  └── mediafire/"
echo ""
echo "  Manual sync:  $SCRIPTS_DIR/inbox-sync.sh"
echo "  View timer:   systemctl status sjl-inbox-sync.timer"
echo "  View logs:    journalctl -u sjl-inbox-sync -f"
echo ""
