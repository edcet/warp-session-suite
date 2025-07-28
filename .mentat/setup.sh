#!/usr/bin/env bash
# Setup script for warp-session-suite
# Installs all necessary dependencies needed to run the project

echo "📦 Installing project dependencies..."

# Install the Python project in development mode
if ! pip3 install -e .; then
    echo "❌ Error: Failed to install project in development mode"
    exit 1
fi

# Install additional Python tools needed by mise tasks and CI
if ! pip3 install \
    sqlite-utils \
    PyYAML \
    black \
    isort \
    ruff \
    mkdocs \
    mkdocs-material; then
    echo "❌ Error: Failed to install additional Python tools"
    exit 1
fi

echo "✅ Setup completed successfully!"
