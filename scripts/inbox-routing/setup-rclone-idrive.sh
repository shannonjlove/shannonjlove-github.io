#!/bin/bash
# setup-rclone-idrive.sh — Add iDrive E2 primary remote to rclone config
# Run ONCE on the VPS (not needed on local Mac for OAuth flows)
#
# Usage: bash setup-rclone-idrive.sh

set -euo pipefail

RCLONE_CONF="${RCLONE_CONFIG:-$HOME/.config/rclone/rclone.conf}"
mkdir -p "$(dirname "$RCLONE_CONF")"

# Check if already configured
if grep -q '^\[idrive-primary\]' "$RCLONE_CONF" 2>/dev/null; then
    echo "idrive-primary already in rclone config — skipping"
    exit 0
fi

cat >> "$RCLONE_CONF" << 'EOF'

[idrive-primary]
type = s3
provider = Other
env_auth = false
access_key_id = hNOOh0odHmPwKt9xDbll
secret_access_key = w8X3Ubjfp6rnGzjoFjBv1kwpdMpn9MxzbQcjozA6
endpoint = https://p3h2.va.idrivee2-48.com
region = us-east-1
EOF

echo "Added [idrive-primary] to $RCLONE_CONF"

# Verify connectivity
if rclone lsd idrive-primary: 2>/dev/null | grep -q inbox-idrive-e2; then
    echo "Verified: inbox-idrive-e2 bucket is accessible"
else
    echo "Warning: Could not verify bucket access — check credentials and endpoint"
fi
