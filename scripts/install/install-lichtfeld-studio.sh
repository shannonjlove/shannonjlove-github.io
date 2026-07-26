#!/usr/bin/env bash
# =============================================================================
# LICHTFELD STUDIO INSTALLER — shannonjlove.cloud
# Modular workstation for 3D Gaussian Splatting: train, inspect, edit,
# automate, and export 3DGS scenes. C++23 + CUDA 12.8 + Vulkan renderer.
# Installs shannonjlove/LichtFeld-Studio (fork of MrNeRF/LichtFeld-Studio).
#
# REQUIREMENTS:
#   - NVIDIA GPU (CUDA 12.8+ recommended)
#   - nvidia-docker / NVIDIA Container Toolkit
#   - Docker + Docker Compose v2
#   - For GUI: X11 display (local) or VNC/noVNC (remote)
#
# Usage: bash scripts/install/install-lichtfeld-studio.sh [-b|-u|-c] [cuda-ver]
#   -b    Build Docker image (first run)
#   -u    Start container and enter shell
#   -c    Stop and clean up containers
#   No flags: print status and launch instructions
#
# MCP integration: once the app is running on port 45677, the MCP bridge
# at scripts/lichtfeld_mcp_bridge.py provides tool access for AI agents.
# =============================================================================

set -euo pipefail

REPO="https://github.com/shannonjlove/LichtFeld-Studio.git"
INSTALL_DIR="/opt/lichtfeld-studio"
IMAGE_NAME="lichtfeld-studio:latest"

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
die()  { echo "ERROR: $*" >&2; exit 1; }

# ---- Parse flags -----------------------------------------------------------
BUILD=false; UP=false; CLEAN=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        -b) BUILD=true ;;
        -u) UP=true ;;
        -c) CLEAN=true ;;
        --help|-h) grep '^#' "$0" | grep -v '#!/' | sed 's/^# \{0,3\}//'; exit 0 ;;
        12.*|13.*) CUDA_VERSION_OVERRIDE="$1" ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
    shift
done

# ---- Default: just show status if no flags ---------------------------------
if [[ "$BUILD" == false && "$UP" == false && "$CLEAN" == false ]]; then
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        echo "LichtFeld-Studio is installed at $INSTALL_DIR"
        docker images "$IMAGE_NAME" 2>/dev/null | head -3 || true
        echo ""
        echo "Commands:"
        echo "  Build image:  sudo bash $0 -b"
        echo "  Start shell:  sudo bash $0 -u"
        echo "  Stop/clean:   sudo bash $0 -c"
    else
        echo "Not installed. Run: sudo bash $0 -b"
    fi
    exit 0
fi

# ---- Prerequisites check ---------------------------------------------------
command -v docker &>/dev/null || die "Docker not found. Install Docker first."
command -v docker &>/dev/null && docker compose version &>/dev/null \
    || die "Docker Compose v2 not found (need 'docker compose', not 'docker-compose')."

# ---- NVIDIA Container Toolkit check ----------------------------------------
if ! docker info 2>/dev/null | grep -q "Runtimes.*nvidia\|nvidia"; then
    log "WARN: NVIDIA Docker runtime not detected. Installing nvidia-container-toolkit..."
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
        gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
        > /etc/apt/sources.list.d/nvidia-container-toolkit.list
    apt-get update -qq
    apt-get install -y nvidia-container-toolkit
    nvidia-ctk runtime configure --runtime=docker
    systemctl restart docker
fi

# ---- Clean -----------------------------------------------------------------
if [[ "$CLEAN" == true ]]; then
    log "Stopping and removing LichtFeld-Studio containers..."
    cd "$INSTALL_DIR" 2>/dev/null || true
    docker compose -f docker/docker-compose.yml down --remove-orphans 2>/dev/null || true
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    log "Done."
    exit 0
fi

# ---- Clone or update -------------------------------------------------------
if [[ -d "$INSTALL_DIR/.git" ]]; then
    log "Updating $INSTALL_DIR..."
    git -C "$INSTALL_DIR" pull --ff-only origin main 2>/dev/null \
        || git -C "$INSTALL_DIR" pull --ff-only origin master 2>/dev/null \
        || log "WARN: could not pull — using existing source"
else
    log "Cloning LichtFeld-Studio → $INSTALL_DIR..."
    git clone "$REPO" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ---- Auto-detect CUDA version ----------------------------------------------
if [[ -n "${CUDA_VERSION_OVERRIDE:-}" ]]; then
    CUDA_VERSION="${CUDA_VERSION_OVERRIDE}.0"
elif command -v nvidia-smi &>/dev/null; then
    detected=$(nvidia-smi | grep -oP 'CUDA Version: \K[0-9]+\.[0-9]+' || echo "12.8")
    CUDA_VERSION="${detected}.0"
else
    CUDA_VERSION="12.8.0"
    log "WARN: nvidia-smi not found, defaulting to CUDA $CUDA_VERSION"
fi
log "CUDA version: $CUDA_VERSION"

# ---- Build Docker image ----------------------------------------------------
if [[ "$BUILD" == true ]]; then
    log "Building LichtFeld-Studio Docker image (this takes 20–60 min on first run)..."
    log "Downloading vcpkg + CMake 4 + all C++ deps inside container..."

    export USER_UID="${USER_UID:-$(id -u)}"
    export USER_GID="${USER_GID:-$(id -g)}"
    export USERNAME="${USERNAME:-lichtfeld}"
    export HOSTNAME="${HOSTNAME:-lichtfeld-studio}"
    export USER_PASSWORD="${USER_PASSWORD:-lichtfeld}"
    export CUDA_VERSION="$CUDA_VERSION"
    export DISPLAY="${DISPLAY:-:0}"
    export XAUTHORITY="${XAUTHORITY:-/root/.Xauthority}"
    export SSH_AUTH_SOCK="${SSH_AUTH_SOCK:-}"

    # Ensure Xauthority file exists (even if empty) for volume mount
    touch "${XAUTHORITY:-/root/.Xauthority}"
    mkdir -p "$HOME/.lichtfeld"

    docker compose -f docker/docker-compose.yml build \
        --build-arg CUDA_VERSION="$CUDA_VERSION" \
        --build-arg USER_UID="$USER_UID" \
        --build-arg USER_GID="$USER_GID" \
        --build-arg USERNAME="$USERNAME"

    log "Docker image built: $IMAGE_NAME"
fi

# ---- Start container and enter shell ---------------------------------------
if [[ "$UP" == true ]]; then
    export USER_UID="${USER_UID:-$(id -u)}"
    export USER_GID="${USER_GID:-$(id -g)}"
    export USERNAME="${USERNAME:-lichtfeld}"
    export HOSTNAME="${HOSTNAME:-lichtfeld-studio}"
    export USER_PASSWORD="${USER_PASSWORD:-lichtfeld}"
    export CUDA_VERSION="$CUDA_VERSION"
    export DISPLAY="${DISPLAY:-:0}"
    export XAUTHORITY="${XAUTHORITY:-/root/.Xauthority}"
    export SSH_AUTH_SOCK="${SSH_AUTH_SOCK:-}"

    touch "${XAUTHORITY:-/root/.Xauthority}"
    mkdir -p "$HOME/.lichtfeld"

    # Allow X11 connections from Docker (if display is available)
    xhost +local:docker 2>/dev/null || true

    log "Starting LichtFeld-Studio container..."
    docker compose -f docker/docker-compose.yml up -d
    docker compose -f docker/docker-compose.yml exec lichtfeld-studio bash

    log "Container exited."
fi

# ---- MCP bridge note -------------------------------------------------------
echo ""
echo "================================================================"
echo "LichtFeld-Studio installed at: $INSTALL_DIR"
echo ""
echo "Docker workflow:"
echo "  Build image:    sudo bash $0 -b [cuda-ver]"
echo "  Enter shell:    sudo bash $0 -u"
echo "  Stop/clean:     sudo bash $0 -c"
echo ""
echo "Inside the container, build LichtFeld from source:"
echo "  cd ~/projects/LichtFeld-Studio"
echo "  cmake -B build -G Ninja -DCMAKE_TOOLCHAIN_FILE=~/vcpkg/scripts/buildsystems/vcpkg.cmake"
echo "  cmake --build build --parallel"
echo "  ./build/lichtfeld"
echo ""
echo "MCP integration (when app is running on port 45677):"
echo "  python3 $INSTALL_DIR/scripts/lichtfeld_mcp_bridge.py"
echo "  # or via .mcp.json in $INSTALL_DIR"
echo ""
echo "Headless/remote server notes:"
echo "  LichtFeld requires a display (Vulkan renderer + GUI)."
echo "  Options for shannonjlove.cloud:"
echo "    1. VNC: sudo apt install tigervnc-standalone-server"
echo "            vncserver :1 -geometry 1920x1080 -depth 24"
echo "            export DISPLAY=:1"
echo "    2. noVNC web UI: docker run -p 6080:80 theasp/novnc"
echo "    3. SSH X11 forwarding: ssh -X user@shannonjlove.cloud"
echo "================================================================"
