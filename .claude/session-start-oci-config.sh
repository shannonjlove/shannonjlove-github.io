#!/bin/bash
# Sets up OCI credentials from environment variables so the SJL_Oracle MCP server
# can authenticate. Set these env vars in your Claude Code remote environment settings:
#
#   OCI_USER_OCID          - e.g. ocid1.user.oc1..aaa...
#   OCI_FINGERPRINT        - e.g. aa:bb:cc:dd:...
#   OCI_TENANCY_OCID       - e.g. ocid1.tenancy.oc1..aaa...
#   OCI_REGION             - e.g. us-ashburn-1  (defaults to us-ashburn-1)
#   OCI_PRIVATE_KEY_CONTENT - base64-encoded PEM private key

set -euo pipefail

REQUIRED_VARS=(OCI_USER_OCID OCI_FINGERPRINT OCI_TENANCY_OCID OCI_PRIVATE_KEY_CONTENT)

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var:-}" ]; then
    echo "[oci-config] Skipping OCI setup: \$${var} is not set"
    exit 0
  fi
done

OCI_DIR=/opt/secrets/oci
mkdir -p "$OCI_DIR"

KEY_FILE="$OCI_DIR/oci_api_key.pem"
echo "${OCI_PRIVATE_KEY_CONTENT}" | base64 -d > "$KEY_FILE"
chmod 600 "$KEY_FILE"

cat > "$OCI_DIR/config" <<EOF
[DEFAULT]
user=${OCI_USER_OCID}
fingerprint=${OCI_FINGERPRINT}
tenancy=${OCI_TENANCY_OCID}
region=${OCI_REGION:-us-ashburn-1}
key_file=${KEY_FILE}
EOF

chmod 600 "$OCI_DIR/config"
echo "[oci-config] OCI credentials written to ${OCI_DIR}/config"
