#!/bin/bash
# Revolutionary post-creation setup script

set -euo pipefail

echo "🚀 Initializing Warp Session Suite development environment..."

# Performance optimization: Parallel initialization
{
  # Install and configure tools
  mise install &

  # Setup Git hooks
  git config --global init.defaultBranch main &
  git config --global pull.rebase false &

  # Configure shell enhancements
  if command -v fzf >/dev/null 2>&1; then
    echo 'source <(fzf --zsh)' >>~/.zshrc
  fi &

  wait
}

# AI-native development setup
if [ ! -d "~/.config/continue" ]; then
  mkdir -p ~/.config/continue
  cat >~/.config/continue/config.json <<'EOF'
{
  "models": [
    {
      "title": "Local Ollama",
      "provider": "ollama",
      "model": "codellama:7b",
      "apiBase": "http://ollama:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Local Starcoder",
    "provider": "ollama",
    "model": "starcoder:3b",
    "apiBase": "http://ollama:11434"
  }
}
EOF
fi

# Database setup for development
mkdir -p .cache/sqlite .cache/duckdb

# Performance monitoring setup
echo "export MISE_LOG_LEVEL=warn" >>~/.zshrc
echo "export RUST_LOG=warn" >>~/.zshrc

# Security hardening
chmod 700 ~/.ssh 2>/dev/null || true
chmod 600 ~/.ssh/* 2>/dev/null || true

echo "✅ Development environment initialized successfully!"
echo "🎯 Ready for AI-native development workflows"
