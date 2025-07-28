#!/usr/bin/env bash
# Setup script for Warp Session Suite
# Installs all necessary dependencies for development and testing

# Install Python dependencies from pyproject.toml
pip3 install -e .

# Install trunk CLI for code formatting and linting
curl -fsSL https://trunk.io/releases/latest/trunk | bash -s -- -b /usr/local/bin

# Install additional Python tools used by the format script
pip3 install black isort ruff PyYAML

# Install yq for YAML processing (used in mise tasks)
if ! command -v yq >/dev/null 2>&1; then
    curl -fsSL https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -o /usr/local/bin/yq
    chmod +x /usr/local/bin/yq
fi

# Install shfmt for shell script formatting
if ! command -v shfmt >/dev/null 2>&1; then
    curl -fsSL https://github.com/mvdan/sh/releases/latest/download/shfmt_v3.7.0_linux_amd64 -o /usr/local/bin/shfmt
    chmod +x /usr/local/bin/shfmt
fi

# Ensure mise is available and tools are installed if .tool-versions exists
if [ -f .tool-versions ] && command -v mise >/dev/null 2>&1; then
    mise install
fi
