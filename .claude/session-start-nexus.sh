#!/bin/bash
# Nexus bootstrap discovery — runs read-only checks at session start.
# Skips silently if not on the Nexus host (service and ports won't exist).

set -uo pipefail

MCP_PORT=8797

# Only run full bootstrap when the MCP service port is present
if ! ss -lntp 2>/dev/null | grep -q ":${MCP_PORT} "; then
  echo "[nexus-bootstrap] Port ${MCP_PORT} not found — skipping Nexus bootstrap (not on Nexus, or service is down)"
  exit 0
fi

echo "[nexus-bootstrap] === Nexus bootstrap discovery ==="

echo "[nexus-bootstrap] 1. Identity"
id && whoami

echo "[nexus-bootstrap] 2. MCP service status"
systemctl --user status sjl-cloud-access-mcp.service --no-pager -l 2>/dev/null || true

echo "[nexus-bootstrap] 3. Port ${MCP_PORT} listener"
ss -lntp | grep ":${MCP_PORT} "

echo "[nexus-bootstrap] 4. OCI config diff (oci-config vs oci/config)"
if diff /opt/secrets/oci-config /opt/secrets/oci/config > /dev/null 2>&1; then
  echo "[nexus-bootstrap] OCI configs match"
else
  echo "[nexus-bootstrap] WARNING: /opt/secrets/oci-config and /opt/secrets/oci/config DIFFER — ask Shannon which is canonical"
  diff /opt/secrets/oci-config /opt/secrets/oci/config || true
fi

echo "[nexus-bootstrap] 5. BookStack vars presence (not values)"
if grep -qE 'BOOKSTACK_(URL|TOKEN_ID|TOKEN_SECRET)' /opt/secrets/sjl-cloud-integrations.env 2>/dev/null; then
  echo "[nexus-bootstrap] BOOKSTACK vars present"
else
  echo "[nexus-bootstrap] WARNING: BOOKSTACK vars missing from /opt/secrets/sjl-cloud-integrations.env"
fi

echo "[nexus-bootstrap] === Bootstrap complete — run oracle_identity_test before any mutations ==="
