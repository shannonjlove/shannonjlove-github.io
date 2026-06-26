# ═══════════════════════════════════════════════════════════════════════════
# DEPLOY ALL THREE TOOLS — FileWarden · HookVault · DiffForge
# For Nexus (Hostinger VPS, Ubuntu 24.04, rootless Podman + systemd quadlets)
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# 1. SHARED requirements.txt  (used by all three images)
# ─────────────────────────────────────────────────────────────────────────────
# requirements-filewarden.txt
watchdog==4.0.1
pyyaml==6.0.1
click==8.1.7

# requirements-hookvault.txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.1
click==8.1.7

# requirements-diffforge.txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.1
python-multipart==0.0.9


# ─────────────────────────────────────────────────────────────────────────────
# 2. Containerfile — FileWarden
# /opt/filewarden/Containerfile
# ─────────────────────────────────────────────────────────────────────────────
# FROM python:3.12-slim
# WORKDIR /app
# RUN pip install --no-cache-dir watchdog pyyaml click
# COPY filewarden.py .
# RUN mkdir -p /var/log/filewarden /var/lib/filewarden /etc/filewarden
# CMD ["python", "filewarden.py", "--config", "/etc/filewarden/config.yaml"]

# ─────────────────────────────────────────────────────────────────────────────
# 3. Containerfile — HookVault
# /opt/hookvault/Containerfile
# ─────────────────────────────────────────────────────────────────────────────
# FROM python:3.12-slim
# WORKDIR /app
# RUN pip install --no-cache-dir fastapi uvicorn pydantic click
# COPY hookvault.py .
# RUN mkdir -p /data/hookvault
# ENV HV_DB=/data/hookvault/vault.db
# ENV HV_PORT=8080
# EXPOSE 8080
# CMD ["python", "hookvault.py", "--host", "0.0.0.0", "--port", "8080"]

# ─────────────────────────────────────────────────────────────────────────────
# 4. Containerfile — DiffForge
# /opt/diffforge/Containerfile
# ─────────────────────────────────────────────────────────────────────────────
# FROM python:3.12-slim
# WORKDIR /app
# RUN pip install --no-cache-dir fastapi uvicorn pydantic python-multipart
# COPY diffforge.py .
# ENV DF_PORT=8082
# ENV DF_ALLOW_PATHS=/data
# EXPOSE 8082
# CMD ["python", "diffforge.py", "--host", "0.0.0.0", "--port", "8082"]


# ═══════════════════════════════════════════════════════════════════════════
# QUADLET FILES  → ~/.config/containers/systemd/
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────
# filewarden.container
# ─────────────────────────────────────────────────────────────────────────
# [Unit]
# Description=FileWarden – Hazel-style file automation daemon
# After=network-online.target
#
# [Container]
# Image=localhost/filewarden:latest
# ContainerName=filewarden
# AutoUpdate=local
# Network=sjl-infra.network
#
# # Config & log volumes
# Volume=/opt/filewarden/config.yaml:/etc/filewarden/config.yaml:ro,z
# Volume=/var/log/filewarden:/var/log/filewarden:z
# Volume=/var/lib/filewarden:/var/lib/filewarden:z
#
# # Data volumes (adjust to your PARA layout)
# Volume=/data/inbox:/data/inbox:z
# Volume=/data/documents:/data/documents:z
# Volume=/data/media:/data/media:z
# Volume=/data/downloads:/data/downloads:z
# Volume=/data/tagback:/data/tagback:z
# Volume=/data/unsorted:/data/unsorted:z
#
# [Service]
# Restart=always
# RestartSec=10
#
# [Install]
# WantedBy=default.target


# ─────────────────────────────────────────────────────────────────────────
# hookvault.container
# ─────────────────────────────────────────────────────────────────────────
# [Unit]
# Description=HookVault – Hookmark-style bidirectional linking API
# After=network-online.target
#
# [Container]
# Image=localhost/hookvault:latest
# ContainerName=hookvault
# AutoUpdate=local
# Network=sjl-infra.network
#
# PublishPort=127.0.0.1:8086:8080
#
# Volume=/data/hookvault:/data/hookvault:z
#
# Environment=HV_DB=/data/hookvault/vault.db
# Environment=HV_BASE_URL=https://admin.shannonjlove.cloud/hooks
# Environment=HV_PORT=8080
#
# [Service]
# Restart=always
# RestartSec=5
#
# [Install]
# WantedBy=default.target


# ─────────────────────────────────────────────────────────────────────────
# diffforge.container
# ─────────────────────────────────────────────────────────────────────────
# [Unit]
# Description=DiffForge – DeltaWalker-style web diff tool
# After=network-online.target
#
# [Container]
# Image=localhost/diffforge:latest
# ContainerName=diffforge
# AutoUpdate=local
# Network=sjl-infra.network
#
# PublishPort=127.0.0.1:8087:8082
#
# # Mount data read-only so the diff tool can access server files
# Volume=/data:/data:ro,z
#
# Environment=DF_PORT=8082
# Environment=DF_ALLOW_PATHS=/data
#
# [Service]
# Restart=always
# RestartSec=5
#
# [Install]
# WantedBy=default.target


# ═══════════════════════════════════════════════════════════════════════════
# NPM PROXY CONFIGS
# (add these as Proxy Hosts in your NPM admin at :81)
# ═══════════════════════════════════════════════════════════════════════════
#
# hooks.shannonjlove.cloud    → http://localhost:8086  (HookVault API + UI)
# diff.shannonjlove.cloud     → http://localhost:8087  (DiffForge UI)
# FileWarden has no web UI — it's a background daemon only.
#
# All three: enable "Block Common Exploits", force SSL, 
# add "Access List" to restrict to Tailscale IPs only:
#   100.115.66.75, 100.67.229.94


# ═══════════════════════════════════════════════════════════════════════════
# ONE-SHOT BUILD + DEPLOY (base64-encode and run on Nexus via NeoServer)
# ═══════════════════════════════════════════════════════════════════════════
#
# Paste this into NeoServer as a single command:
#
# bash -c "$(echo BASE64_BELOW | base64 -d)"
#
# The raw script (encode before pasting):
# ─────────────────────────────────────────────────────────────────────────
# set -euo pipefail
# echo '── FileWarden ──'
# mkdir -p /opt/filewarden
# cp ~/filewarden/filewarden.py /opt/filewarden/
# cp ~/filewarden/config.yaml   /opt/filewarden/
# cat > /opt/filewarden/Containerfile <<'CEOF'
# FROM python:3.12-slim
# WORKDIR /app
# RUN pip install --no-cache-dir watchdog pyyaml click
# COPY filewarden.py .
# RUN mkdir -p /var/log/filewarden /var/lib/filewarden
# CMD ["python","filewarden.py","--config","/etc/filewarden/config.yaml"]
# CEOF
# podman build -t localhost/filewarden:latest /opt/filewarden
#
# echo '── HookVault ──'
# mkdir -p /opt/hookvault /data/hookvault
# cp ~/hookvault/hookvault.py /opt/hookvault/
# cat > /opt/hookvault/Containerfile <<'CEOF'
# FROM python:3.12-slim
# WORKDIR /app
# RUN pip install --no-cache-dir fastapi "uvicorn[standard]" pydantic click
# COPY hookvault.py .
# EXPOSE 8080
# CMD ["python","hookvault.py"]
# CEOF
# podman build -t localhost/hookvault:latest /opt/hookvault
#
# echo '── DiffForge ──'
# mkdir -p /opt/diffforge
# cp ~/diffforge/diffforge.py /opt/diffforge/
# cat > /opt/diffforge/Containerfile <<'CEOF'
# FROM python:3.12-slim
# WORKDIR /app
# RUN pip install --no-cache-dir fastapi "uvicorn[standard]" pydantic python-multipart
# COPY diffforge.py .
# EXPOSE 8082
# CMD ["python","diffforge.py"]
# CEOF
# podman build -t localhost/diffforge:latest /opt/diffforge
#
# echo '── Quadlets ──'
# QDIR="${XDG_CONFIG_HOME:-$HOME/.config}/containers/systemd"
# mkdir -p "$QDIR"
# # (copy quadlet content from above into $QDIR/filewarden.container etc.)
# systemctl --user daemon-reload
# systemctl --user enable --now filewarden hookvault diffforge
# echo '── Done ──'
