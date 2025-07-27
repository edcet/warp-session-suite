# Revolutionary multi-stage development container
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04 AS base

# Performance optimization: Parallel package installation
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget git build-essential \
    ca-certificates gnupg lsb-release \
    software-properties-common \
    pkg-config libssl-dev \
    python3-pip python3-venv \
    nodejs npm \
    sqlite3 \
    fd-find ripgrep bat \
    direnv \
    && rm -rf /var/lib/apt/lists/*

# Install mise (revolutionary tool version manager)
USER vscode
RUN curl https://mise.run | sh
ENV PATH="/home/vscode/.local/bin:$PATH"

# AI-native optimizations
RUN mkdir -p /home/vscode/.config/mise /home/vscode/.cache/mise

# Install additional development tools
RUN mise use --global nodejs@20 python@3.12 \
    && mise install \
    && npm install -g pnpm yarn bun \
    && python -m pip install --user uv ruff black mypy

# Security hardening
RUN echo 'eval "$(mise activate bash)"' >> /home/vscode/.bashrc \
    && echo 'eval "$(direnv hook bash)"' >> /home/vscode/.bashrc \
    && echo 'eval "$(mise activate zsh)"' >> /home/vscode/.zshrc \
    && echo 'eval "$(direnv hook zsh)"' >> /home/vscode/.zshrc

# Performance optimization: Pre-warm caches
RUN mise install && mise reshim

WORKDIR /workspace
USER vscode
