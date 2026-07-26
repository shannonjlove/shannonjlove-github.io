#!/usr/bin/env bash
# =============================================================================
# VIEWPORT EXPORT PLUGIN INSTALLER — shannonjlove.cloud
# Installs shannonjlove/viewport-export-lichtfeld into LichtFeld Studio.
#
# This plugin adds viewport export at 1080p–32K resolution (JPG/PNG) with
# optional BW2A alpha extraction (RGBA transparency via dual-background capture).
# Requires LichtFeld Studio >= 0.5.1.
#
# INSTALLATION PATHS:
#   Host (bare metal):    ~/.lichtfeld/plugins/viewport_export
#   Docker container:     /home/lichtfeld/.lichtfeld/plugins/viewport_export
#                         (auto-installs if container is running)
#
# Usage: bash scripts/install/install-viewport-export-lichtfeld.sh
#        bash scripts/install/install-viewport-export-lichtfeld.sh --docker
#        bash scripts/install/install-viewport-export-lichtfeld.sh --host
# =============================================================================

set -euo pipefail

REPO="https://github.com/shannonjlove/viewport-export-lichtfeld.git"
HOST_PLUGIN_DIR="${LICHTFELD_PLUGIN_DIR:-$HOME/.lichtfeld/plugins/viewport_export}"
CONTAINER_PLUGIN_DIR="/home/lichtfeld/.lichtfeld/plugins/viewport_export"
CONTAINER_NAME="lichtfeld-studio"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# ---- Parse flags -----------------------------------------------------------
TARGET_HOST=false
TARGET_DOCKER=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --host)   TARGET_HOST=true ;;
        --docker) TARGET_DOCKER=true ;;
        --help|-h)
            grep '^#' "$0" | grep -v '#!/' | sed 's/^# \{0,3\}//'
            exit 0 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
    shift
done

# Default: install wherever LichtFeld is running
if [[ "$TARGET_HOST" == false && "$TARGET_DOCKER" == false ]]; then
    TARGET_HOST=true
    TARGET_DOCKER=true
fi

# ---- Install on host -------------------------------------------------------
install_host() {
    log "Installing viewport-export plugin to: $HOST_PLUGIN_DIR"
    mkdir -p "$(dirname "$HOST_PLUGIN_DIR")"

    if [[ -d "$HOST_PLUGIN_DIR/.git" ]]; then
        log "Updating existing plugin source..."
        git -C "$HOST_PLUGIN_DIR" pull --ff-only origin main 2>/dev/null \
            || log "WARN: could not pull — using existing source"
    else
        log "Cloning viewport-export-lichtfeld → $HOST_PLUGIN_DIR..."
        git clone --depth=1 "$REPO" "$HOST_PLUGIN_DIR"
    fi

    log "Source: $HOST_PLUGIN_DIR ($(git -C "$HOST_PLUGIN_DIR" log --oneline -1))"

    # Install Python deps — try known LichtFeld venv paths first
    INSTALLED=false
    for PIP in \
        "/opt/lichtfeld-studio/venv/bin/pip" \
        "$HOME/.lichtfeld/venv/bin/pip" \
        "/opt/lichtfeld-studio/.venv/bin/pip"
    do
        if [[ -x "$PIP" ]]; then
            log "Installing Pillow + numpy into LichtFeld venv: $PIP"
            "$PIP" install --quiet Pillow numpy
            INSTALLED=true
            break
        fi
    done

    if [[ "$INSTALLED" == false ]]; then
        if command -v pip3 &>/dev/null; then
            log "LichtFeld venv not found — installing Pillow + numpy into system pip3"
            pip3 install --quiet Pillow numpy
        elif command -v pip &>/dev/null; then
            log "LichtFeld venv not found — installing Pillow + numpy into system pip"
            pip install --quiet Pillow numpy
        else
            log "WARN: pip not found — install Pillow and numpy manually before using the plugin"
        fi
    fi

    log "Host install complete."
}

# ---- Install inside running Docker container -------------------------------
install_docker() {
    if ! docker ps 2>/dev/null | grep -q "$CONTAINER_NAME"; then
        log "SKIP: Docker container '$CONTAINER_NAME' is not running."
        log "      Start it with: sudo bash scripts/install/install-lichtfeld-studio.sh -u"
        return
    fi

    log "Installing viewport-export plugin inside container '$CONTAINER_NAME'..."
    docker exec "$CONTAINER_NAME" bash -c "
        set -e
        PLUGIN_DIR='$CONTAINER_PLUGIN_DIR'
        mkdir -p \"\$(dirname \"\$PLUGIN_DIR\")\"
        if [[ -d \"\$PLUGIN_DIR/.git\" ]]; then
            git -C \"\$PLUGIN_DIR\" pull --ff-only origin main 2>/dev/null || true
        else
            git clone --depth=1 '$REPO' \"\$PLUGIN_DIR\"
        fi
        pip install --quiet Pillow numpy
        echo 'Container install: OK'
    "
    log "Docker install complete."
}

# ---- Run -------------------------------------------------------------------
[[ "$TARGET_HOST"   == true ]] && install_host
[[ "$TARGET_DOCKER" == true ]] && install_docker

# ---- Usage summary ---------------------------------------------------------
echo ""
echo "================================================================"
echo "Viewport Export plugin installed for LichtFeld Studio"
echo ""
echo "Host plugin dir: $HOST_PLUGIN_DIR"
echo ""
echo "Usage in LichtFeld Studio:"
echo "  1. Open LichtFeld Studio (or restart if already open)"
echo "  2. The 'Viewport Export' tab appears in the right-side panel"
echo "  3. Select resolution (Viewport / 1080p / 4K / 8K / … / 32K)"
echo "  4. Select format (JPG with quality, PNG with compression)"
echo "  5. For PNG: enable Transparency (RGBA) for BW2A alpha extraction"
echo "  6. Click Export → choose save location"
echo ""
echo "Via Plugin Manager (alternative):"
echo "  Tools → Plugin Manager → search 'Viewport Export' → Install"
echo ""
echo "Requires: LichtFeld Studio >= 0.5.1"
echo "================================================================"
