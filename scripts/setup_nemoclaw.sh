#!/usr/bin/env bash
set -e

echo "=== NemoClaw Hermes Agent Setup for macOS ==="

# 1. Check Prerequisites
if ! command -v docker &> /dev/null; then
    echo "Error: Docker Desktop is not running or not installed."
    exit 1
fi

echo "✓ Docker Desktop detected."

# 2. Check for Credentials
if [ -f "config/credentials.env" ]; then
    echo "✓ Loading credentials from config/credentials.env"
    export $(grep -v '^#' config/credentials.env | xargs)
else
    echo "Warning: config/credentials.env not found. Copying from example..."
    cp config/credentials.env.example config/credentials.env
    echo "Please edit config/credentials.env and insert your GEMINI_API_KEY."
fi

# 3. Clone / Pull NemoClaw Repository if needed
if [ ! -d "nemoclaw_src" ]; then
    echo "Cloning NVIDIA NemoClaw repository..."
    git clone https://github.com/NVIDIA/nemoclaw.git nemoclaw_src
else
    echo "NemoClaw source repository present."
fi

# 4. Initialize OpenShell Container with Hermes Agent
echo "Initializing NemoClaw with Hermes agent..."
export NEMOCLAW_AGENT=hermes
export NEMOCLAW_SANDBOX_NAME=mac-hermes-agent

# Run installer / status check
curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash || true

echo "=== Setup complete! ==="
