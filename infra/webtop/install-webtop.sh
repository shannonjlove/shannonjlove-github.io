#!/usr/bin/env bash
# install-webtop.sh — deploy WebTop Podman Quadlet
#
# WebTop provides a full browser-accessible Linux desktop (ubuntu-mate).
# After install it is available at: https://webtop.shannonjlove.cloud
#
# Requires: NPM proxy entry for port 3000 → webtop.shannonjlove.cloud
# Requires: Podman + systemd (Quadlet support in Podman ≥ 4.4)
set -euo pipefail

WEBTOP_CONFIG="/opt/webtop/config"
QUADLET_DIR="/etc/containers/systemd"

echo "==> Creating WebTop config directory..."
mkdir -p "$WEBTOP_CONFIG"

echo "==> Installing Podman Quadlet unit..."
cp "$(dirname "${BASH_SOURCE[0]}")/webtop.container" "$QUADLET_DIR/webtop.container"
chmod 644 "$QUADLET_DIR/webtop.container"

echo "==> Reloading systemd and enabling WebTop..."
systemctl daemon-reload
systemctl enable --now webtop.service

echo ""
echo "Done! WebTop is starting."
echo "  Web UI  : https://webtop.shannonjlove.cloud  (or http://127.0.0.1:3000)"
echo "  Desktop : ubuntu-mate"
echo "  Data    : /data (PARA filesystem fully mounted)"
echo "  Config  : $WEBTOP_CONFIG"
echo ""
echo "Default credentials: abc / abc  — change via WebTop Settings > Users"
echo ""
echo "Add to NPM: forward webtop.shannonjlove.cloud → 127.0.0.1:3000"
echo ""
echo "Check status:   systemctl status webtop.service"
echo "View logs:      journalctl -u webtop.service -f"
