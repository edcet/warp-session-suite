#!/usr/bin/env bash
set -e  # Exit immediately if a command exits with a non-zero status

# Setup script for Warp Session Suite
# Installs all necessary dependencies for development and testing

# Tool versions and URLs
SHFMT_VERSION="v3.7.0"
YQ_URL="https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64"
TRUNK_URL="https://trunk.io/releases/latest/trunk"

echo "📦 Installing Python dependencies from pyproject.toml..."
pip3 install -e . || { echo "Failed to install Python dependencies"; exit 1; }

echo "🛠️ Installing trunk CLI for code formatting and linting..."
curl -fsSL "$TRUNK_URL" | bash -s -- -b /usr/local/bin || { echo "Failed to install trunk CLI"; exit 1; }

echo "🐍 Installing additional Python tools used by the format script..."
pip3 install black isort ruff PyYAML || { echo "Failed to install additional Python tools"; exit 1; }

# Install yq for YAML processing (used in mise tasks)
if ! command -v yq >/dev/null 2>&1; then
    echo "📄 Installing yq for YAML processing..."
    curl -fsSL "$YQ_URL" -o /usr/local/bin/yq || { echo "Failed to download yq"; exit 1; }
    chmod +x /usr/local/bin/yq || { echo "Failed to set executable permissions for yq"; exit 1; }
fi

# Install shfmt for shell script formatting (get latest release URL dynamically)
if ! command -v shfmt >/dev/null 2>&1; then
    echo "🐚 Installing shfmt for shell script formatting..."
    SHFMT_URL=$(curl -s https://api.github.com/repos/mvdan/sh/releases/latest | grep "browser_download_url.*linux_amd64" | cut -d '"' -f 4)
    if [ -n "$SHFMT_URL" ]; then
        curl -fsSL "$SHFMT_URL" -o /usr/local/bin/shfmt || { echo "Failed to download shfmt"; exit 1; }
        chmod +x /usr/local/bin/shfmt || { echo "Failed to set executable permissions for shfmt"; exit 1; }
    else
        echo "Warning: Could not determine latest shfmt URL, skipping installation"
    fi
fi

# Ensure mise is available and tools are installed if .tool-versions exists
if [ -f .tool-versions ] && command -v mise >/dev/null 2>&1; then
    echo "🔧 Installing mise tools from .tool-versions..."
    mise install || { echo "Failed to install tools with mise"; exit 1; }
fi

echo "✅ Setup completed successfully!"
