#!/usr/bin/env bash
# Setup script for warp-session-suite
# Installs all necessary dependencies needed to run the project

echo "📦 Installing project dependencies..."

# Install the Python project in development mode
pip3 install -e .

# Install additional Python tools needed by mise tasks and CI
pip3 install \
    sqlite-utils \
    PyYAML \
    black \
    isort \
    ruff \
    mkdocs \
    mkdocs-material

echo "✅ Setup completed successfully!"
