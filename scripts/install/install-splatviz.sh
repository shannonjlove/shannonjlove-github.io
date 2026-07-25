#!/usr/bin/env bash
# =============================================================================
# SPLATVIZ INSTALLER — shannonjlove.cloud
# Interactive 3D Gaussian Splatting viewer and editor.
# Installs shannonjlove/splatviz (fork of Florian-Barthel/splatviz).
#
# REQUIREMENTS:
#   - NVIDIA GPU with CUDA support
#   - CUDA Toolkit 11.8, 12.6, 12.8, or 13.0 installed
#   - Python 3.10.x (strict — 3.11+ NOT supported)
#   - OpenGL 3.3+ capable driver
#
# Usage: bash scripts/install/install-splatviz.sh [cuda-version]
#        cuda-version: cu118 | cu126 | cu128 | cu130 (default: cu128)
#
# After install:
#   cd /opt/splatviz && uv run python run_main.py
# =============================================================================

set -euo pipefail

REPO="https://github.com/shannonjlove/splatviz.git"
INSTALL_DIR="/opt/splatviz"
CUDA_EXTRA="${1:-cu128}"     # cu118 | cu126 | cu128 | cu130
RASTERIZER="git+https://github.com/ashawkey/diff-gaussian-rasterization.git"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

# ---- Validate cuda extra ---------------------------------------------------
case "$CUDA_EXTRA" in
    cu118|cu126|cu128|cu130) ;;
    *) die "Invalid CUDA extra '$CUDA_EXTRA'. Use: cu118 | cu126 | cu128 | cu130" ;;
esac

# ---- GPU check -------------------------------------------------------------
if command -v nvidia-smi &>/dev/null; then
    log "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)"
    log "CUDA: $(nvidia-smi | grep 'CUDA Version' | awk '{print $9}' 2>/dev/null || echo 'unknown')"
else
    echo "WARNING: nvidia-smi not found — GPU/CUDA required for splatviz to run."
    echo "         Installing anyway; will fail at runtime without GPU."
fi

# ---- System dependencies ---------------------------------------------------
if command -v apt-get &>/dev/null; then
    log "Installing system dependencies..."
    apt-get update -qq
    apt-get install -y \
        git curl \
        python3.10 python3.10-dev python3.10-venv \
        libgl1-mesa-dev libglfw3-dev \
        build-essential ninja-build \
        libglib2.0-0 libsm6 libxrender1 libxext6 2>/dev/null | tail -5
fi

# ---- uv (fast Python package manager) -------------------------------------
if ! command -v uv &>/dev/null; then
    log "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
log "uv: $(uv --version)"

# ---- Clone or update -------------------------------------------------------
if [[ -d "$INSTALL_DIR/.git" ]]; then
    log "Updating existing source at $INSTALL_DIR..."
    git -C "$INSTALL_DIR" pull --ff-only origin main 2>/dev/null \
        || git -C "$INSTALL_DIR" pull --ff-only origin master 2>/dev/null \
        || log "WARN: could not pull — using existing source"
else
    log "Cloning splatviz → $INSTALL_DIR..."
    git clone "$REPO" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
log "Source: $INSTALL_DIR ($(git log --oneline -1))"

# ---- Sync Python environment -----------------------------------------------
log "Syncing Python environment with CUDA extra: $CUDA_EXTRA ..."
uv sync --extra "$CUDA_EXTRA"

# ---- Install CUDA rasterizer (requires CUDA + C++ compiler) ----------------
log "Installing diff-gaussian-rasterization CUDA extension..."
log "(This compiles CUDA kernels — takes 5–20 minutes on first run)"
uv pip install --no-build-isolation "$RASTERIZER"

# ---- Mesa OpenGL override (for headless/wrong-version environments) ---------
LAUNCH_WRAPPER="$INSTALL_DIR/launch-splatviz.sh"
cat > "$LAUNCH_WRAPPER" <<'LAUNCH'
#!/usr/bin/env bash
# Launch splatviz — set OpenGL override if needed
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Uncomment if OpenGL picks the wrong version:
# export MESA_GL_VERSION_OVERRIDE=3.3

exec uv run python run_main.py "$@"
LAUNCH
chmod +x "$LAUNCH_WRAPPER"

# ---- Symlink for easy access -----------------------------------------------
ln -sf "$LAUNCH_WRAPPER" /usr/local/bin/splatviz 2>/dev/null \
    || log "WARN: could not symlink to /usr/local/bin/splatviz (need root?)"

log "splatviz installed"

# ---- Usage summary ---------------------------------------------------------
echo ""
echo "================================================================"
echo "splatviz installed at: $INSTALL_DIR"
echo ""
echo "Usage:"
echo ""
echo "  # Open a .ply / .splat file"
echo "  cd $INSTALL_DIR"
echo "  uv run python run_main.py"
echo ""
echo "  # Or via shortcut (if symlink succeeded):"
echo "  splatviz"
echo ""
echo "  # Attach to a running 3DGS training process (port 6007)"
echo "  uv run python run_main.py --mode=attach"
echo "  uv run python run_main.py --mode=attach --host=0.0.0.0 --port=6007"
echo ""
echo "  # If OpenGL version error:"
echo "  export MESA_GL_VERSION_OVERRIDE=3.3 && uv run python run_main.py"
echo ""
echo "CUDA extra synced: $CUDA_EXTRA"
echo "================================================================"
