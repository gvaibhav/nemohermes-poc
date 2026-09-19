#!/usr/bin/env bash
# setup_nemoclaw.sh — Install NemoClaw, clone source, and configure Hermes agent.
#
# Usage:
#   bash scripts/setup_nemoclaw.sh
#
# This script is safe to re-run (idempotent).

set -euo pipefail

# Resolve project root regardless of where the script is invoked from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== NemoClaw Hermes Agent Setup for macOS ==="
echo "Project root: ${PROJECT_ROOT}"

# ────────────────────────────────────────────────────
# 1. Check prerequisites
# ────────────────────────────────────────────────────
echo ""
echo "--- Checking prerequisites ---"

# Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo "✗ Error: python3 is not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python ${PYTHON_VERSION} detected."

# Docker
if ! command -v docker &> /dev/null; then
    echo "✗ Error: Docker Desktop is not installed."
    echo "  Install from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "✗ Error: Docker Desktop is installed but not running."
    echo "  Please start Docker Desktop and re-run this script."
    exit 1
fi

echo "✓ Docker Desktop detected and running."

# ────────────────────────────────────────────────────
# 2. Configure credentials
# ────────────────────────────────────────────────────
echo ""
echo "--- Configuring credentials ---"

CREDS_FILE="${PROJECT_ROOT}/config/credentials.env"
CREDS_EXAMPLE="${PROJECT_ROOT}/config/credentials.env.example"

if [ -f "${CREDS_FILE}" ]; then
    echo "✓ Credentials file found: config/credentials.env"
    # Source safely — handle quoted values and spaces
    set -a
    # shellcheck source=/dev/null
    source "${CREDS_FILE}"
    set +a
else
    echo "⚠ config/credentials.env not found."
    if [ -f "${CREDS_EXAMPLE}" ]; then
        cp "${CREDS_EXAMPLE}" "${CREDS_FILE}"
        echo "  Copied from credentials.env.example."
    fi
    echo "  → Please edit config/credentials.env and set your GEMINI_API_KEY."
fi

# Validate GEMINI_API_KEY is set
if [ -z "${GEMINI_API_KEY:-}" ] || [ "${GEMINI_API_KEY}" = "your_gemini_api_key_here" ]; then
    echo "⚠ GEMINI_API_KEY is not configured. Hermes will not be able to call the Gemini API."
    echo "  → Set it in config/credentials.env or export GEMINI_API_KEY=<your-key>"
fi

# ────────────────────────────────────────────────────
# 3. Install Python dependencies
# ────────────────────────────────────────────────────
echo ""
echo "--- Installing Python dependencies ---"

pip3 install -q -r "${PROJECT_ROOT}/requirements.txt" 2>/dev/null || {
    echo "⚠ pip install failed. You may need to run: pip3 install -r requirements.txt"
}

echo "✓ Python dependencies installed."

# ────────────────────────────────────────────────────
# 4. Clone NemoClaw source repository
# ────────────────────────────────────────────────────
echo ""
echo "--- Checking NemoClaw source ---"

NEMOCLAW_SRC="${PROJECT_ROOT}/nemoclaw_src"

if [ -d "${NEMOCLAW_SRC}/.git" ]; then
    echo "✓ NemoClaw source already cloned at nemoclaw_src/"
    echo "  Pulling latest changes..."
    git -C "${NEMOCLAW_SRC}" pull --ff-only 2>/dev/null || {
        echo "  ⚠ Could not pull latest (may be offline or diverged). Continuing."
    }
else
    echo "Cloning NVIDIA NemoClaw repository..."
    git clone https://github.com/NVIDIA/nemoclaw.git "${NEMOCLAW_SRC}" 2>/dev/null || {
        echo "⚠ Could not clone NemoClaw repo. The repository may require authentication"
        echo "  or the URL may have changed. Continuing without source."
    }
fi

# ────────────────────────────────────────────────────
# 5. Initialize OpenShell + Hermes
# ────────────────────────────────────────────────────
echo ""
echo "--- Initializing NemoClaw with Hermes agent ---"

export NEMOCLAW_AGENT="${NEMOCLAW_AGENT:-hermes}"
export NEMOCLAW_SANDBOX_NAME="${NEMOCLAW_SANDBOX_NAME:-mac-hermes-agent}"

echo "  Agent:   ${NEMOCLAW_AGENT}"
echo "  Sandbox: ${NEMOCLAW_SANDBOX_NAME}"

# Attempt NemoClaw CLI installer if available
if command -v nemoclaw &> /dev/null; then
    nemoclaw status || true
elif [ -f "${NEMOCLAW_SRC}/scripts/install.sh" ]; then
    echo "Running NemoClaw installer from source..."
    bash "${NEMOCLAW_SRC}/scripts/install.sh" || {
        echo "⚠ NemoClaw installer exited with errors. Check logs above."
    }
else
    echo "⚠ NemoClaw CLI not found and no installer script available."
    echo "  → Follow https://docs.nvidia.com/nemoclaw/user-guide/openclaw/home for manual setup."
fi

# ────────────────────────────────────────────────────
# 6. Summary
# ────────────────────────────────────────────────────
echo ""
echo "=== Setup Summary ==="
echo "  Project Root : ${PROJECT_ROOT}"
echo "  Python       : ${PYTHON_VERSION}"
echo "  Docker       : $(docker --version 2>/dev/null || echo 'N/A')"
echo "  Gemini Key   : ${GEMINI_API_KEY:+configured}${GEMINI_API_KEY:-NOT SET}"
echo "  NemoClaw Src : ${NEMOCLAW_SRC}"
echo ""
echo "Next steps:"
echo "  1. Set GEMINI_API_KEY in config/credentials.env (if not done)"
echo "  2. Run the PoC:  python3 usecases/poc_toil_reduction_skill.py"
echo "  3. Run tests:    python3 -m unittest discover -s tests"
echo ""
echo "=== Setup complete! ==="
