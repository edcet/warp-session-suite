#!/usr/bin/env bash
# Mentat AI Assistant - Unified Shell Environment
# Single-file configuration with aliases, fzf integration, and tool management
# Consolidates all shell configurations to prevent drift

set -euo pipefail

# ============================================================================
# Environment Intelligence & Integration
# ============================================================================

# Ensure mise is active
if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate bash)" 2>/dev/null || true
fi

# ============================================================================
# Core Mentat Aliases - Simple & Effective
# ============================================================================

# Mentat operations
alias mentat-setup='mise run mentat:setup'
alias mentat-format='mise run mentat:format'
alias mentat-doctor='mise run mentat:doctor'
alias mentat-clean='mise run mentat:clean'

# Warp integration (leveraging existing scripts)
alias ws-commands='mise run ws-commands'
alias ws-blocks='mise run ws-blocks'
alias ws-ai='mise run ws-ai'

# Development productivity
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'

# Git workflow (simple and fast)
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gd='git diff'
alias gb='git branch'
alias gco='git checkout'

# Database operations
alias schema-backup='mise run schema:vacuum'
alias schema-extract='mise run schema:extract'
alias docs-serve='mise run docs:serve'

# ============================================================================
# Intelligent Functions - FZF Integration
# ============================================================================

# Smart commit with automatic formatting
smart-commit() {
    local message="${1:-chore: automated improvements}"
    echo "🎨 Formatting code..."
    mise run mentat:format
    
    echo "📦 Staging changes..."
    git add .
    
    echo "💾 Committing..."
    git commit -m "$message"
    
    echo "✅ Smart commit complete!"
}

# Interactive tool selector using fzf
mentat-tool() {
    local tool
    tool=$(cat << EOF | fzf --height 40% --border --prompt "Select tool: "
mentat:setup    Setup development environment
mentat:format   Format code with intelligent detection
mentat:doctor   Health check environment
mentat:clean    Clean caches and temp files
ws-commands     Browse Warp command history
ws-blocks       Navigate Warp blocks/panes
ws-ai           Browse AI conversations
schema:extract  Extract database schema
docs:serve      Start documentation server
EOF
)
    
    if [[ -n "$tool" ]]; then
        local task=$(echo "$tool" | cut -d' ' -f1)
        echo "🚀 Running: $task"
        mise run "$task"
    fi
}

# Project initialization with intelligent detection
mentat-init() {
    echo "🤖 Initializing Mentat-enhanced project..."
    
    # Health check first
    mise run mentat:doctor
    
    # Setup development environment
    mise run mentat:setup
    
    # Format existing code
    echo "🎨 Initial code formatting..."
    mise run mentat:format
    
    # Git hooks setup if lefthook is configured
    if [[ -f lefthook.yml ]] && command -v lefthook >/dev/null 2>&1; then
        echo "🪝 Installing git hooks..."
        lefthook install
    fi
    
    echo "✅ Project initialized with Mentat AI Assistant!"
    echo "💡 Try: mentat-tool, ws-commands, or smart-commit"
}

# Interactive mise task runner with fzf
mise-run() {
    local task
    task=$(mise tasks --no-header | fzf --height 40% --border --prompt "Select task: ")
    
    if [[ -n "$task" ]]; then
        local task_name=$(echo "$task" | awk '{print $1}')
        echo "🚀 Running: $task_name"
        mise run "$task_name"
    fi
}

# ============================================================================
# FZF Enhanced Navigation (leveraging .envrc config)
# ============================================================================

# Quick file finder with preview
ff() {
    local file
    file=$(fzf --preview 'bat --style=numbers --color=always --line-range :500 {}' \
              --preview-window=right:50%:wrap \
              --height 60% --border)
    
    if [[ -n "$file" ]]; then
        ${EDITOR:-code} "$file"
    fi
}

# Directory navigator with zoxide integration
cd() {
    if command -v zoxide >/dev/null 2>&1; then
        z "$@"
    else
        builtin cd "$@"
    fi
}

# ============================================================================
# Tool Integration & Environment Setup
# ============================================================================

# Python environment optimization
if command -v python3 >/dev/null 2>&1; then
    # Ensure user bin is in PATH for pip installs
    export PATH="$HOME/.local/bin:$PATH"
    
    # Python development helpers
    alias pip-upgrade='python3 -m pip install --user --upgrade pip setuptools wheel'
    alias venv-create='python3 -m venv .venv && source .venv/bin/activate'
    alias venv-activate='source .venv/bin/activate'
fi

# Node.js integration
if command -v node >/dev/null 2>&1; then
    alias npm-fresh='rm -rf node_modules package-lock.json && npm install'
    alias yarn-fresh='rm -rf node_modules yarn.lock && yarn install'
fi

# Rust integration
if command -v cargo >/dev/null 2>&1; then
    alias cargo-update='cargo install-update -a'
    alias cargo-clean-all='cargo clean && rm -rf target'
fi

# ============================================================================
# Performance & Monitoring
# ============================================================================

# System resource monitoring
mentat-status() {
    echo "🔍 Mentat Environment Status"
    echo "============================"
    echo "📊 CPU: $(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 'unknown') cores"
    echo "💾 Memory: $(free -h 2>/dev/null | awk 'NR==2{print $3"/"$2}' || echo 'unknown')"
    echo "💽 Disk: $(df -h . 2>/dev/null | awk 'NR==2{print $3"/"$2" ("$5")"}' || echo 'unknown')"
    echo "🐍 Python: $(python3 --version 2>/dev/null || echo 'not found')"
    echo "📦 Node: $(node --version 2>/dev/null || echo 'not found')"
    echo "🔧 Mise: $(mise --version 2>/dev/null || echo 'not found')"
    
    if [[ -f .tool-versions ]]; then
        echo ""
        echo "🛠️ Tool Versions:"
        cat .tool-versions | sed 's/^/   /'
    fi
}

# Quick performance test
mentat-bench() {
    echo "⚡ Quick Performance Benchmark"
    echo "============================="
    
    echo -n "🐍 Python startup: "
    time python3 -c "print('Ready')" 2>&1 | grep real | awk '{print $2}'
    
    echo -n "📦 Node startup: "
    time node -e "console.log('Ready')" 2>&1 | grep real | awk '{print $2}' || echo "N/A"
    
    echo -n "🔧 Mise activation: "
    time mise activate bash >/dev/null 2>&1 && echo "Fast" || echo "Slow"
}

# ============================================================================
# Help & Documentation
# ============================================================================

mentat-help() {
    cat << 'EOF'
🤖 Mentat AI Assistant - Command Reference
=========================================

## Core Commands
  mentat-setup      Setup development environment
  mentat-format     Intelligent code formatting
  mentat-doctor     Environment health check
  mentat-clean      Clean caches and temporary files
  mentat-init       Initialize project with Mentat
  mentat-tool       Interactive tool selector (fzf)
  mentat-status     System status and tool versions
  mentat-bench      Quick performance benchmark

## Warp Integration
  ws-commands       Browse command history with fzf
  ws-blocks         Navigate panes/blocks
  ws-ai             Browse AI conversations

## Development Workflow
  smart-commit      Format, stage, and commit with message
  mise-run          Interactive mise task runner
  ff                Fuzzy file finder with preview

## Database Operations
  schema-backup     Backup Warp database
  schema-extract    Extract schema to JSON/YAML
  docs-serve        Start documentation server

## Git Shortcuts
  gs, ga, gc, gp, gl, gd, gb, gco

## Navigation
  ll, la, l         Enhanced ls commands
  cd                Smart directory change (with zoxide)

💡 All commands integrate with your existing mise/FZF/tool configuration
🔗 Run 'mentat-doctor' to verify everything is working correctly
EOF
}

# ============================================================================
# Auto-initialization
# ============================================================================

# Show brief welcome message when sourced interactively
if [[ "${BASH_SOURCE[0]}" != "${0}" ]] && [[ -t 1 ]]; then
    echo "🤖 Mentat AI Assistant loaded"
    echo "💡 Type 'mentat-help' for commands or 'mentat-tool' for interactive mode"
fi

# Export key functions for sub-shells
export -f smart-commit mentat-tool mentat-init mise-run mentat-status mentat-bench mentat-help
