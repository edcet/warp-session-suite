#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Mentat Dynamic Setup - GitOps Driven Configuration Management
# Leverages: Comtrya -> Mise -> Sheldon with Proactive Intelligence
# ============================================================================

# Advanced logging and telemetry
SETUP_START_TIME=$(date +%s)
SETUP_LOG="/tmp/mentat-setup-$(date +%Y%m%d-%H%M%S).log"
exec 1> >(tee -a "$SETUP_LOG")
exec 2> >(tee -a "$SETUP_LOG" >&2)

echo "🚀 Mentat Dynamic Setup initiated at $(date -Iseconds)"
echo "📊 Session ID: mentat-$(uname -n)-$$"
echo "🔍 Environment analysis starting..."

# ============================================================================
# Dynamic Environment Detection & Intelligence
# ============================================================================

detect_environment_capabilities() {
  local capabilities=()

  # Container detection with enhanced intelligence
  if [[ -f /.dockerenv ]] || grep -q 'docker\|lxc' /proc/1/cgroup 2>/dev/null; then
    capabilities+=("container")
    echo "🐳 Container environment detected"
  fi

  # CI/CD environment detection
  if [[ -n "${CI:-}" ]] || [[ -n "${GITHUB_ACTIONS:-}" ]] || [[ -n "${GITLAB_CI:-}" ]]; then
    capabilities+=("ci")
    echo "🔄 CI/CD environment detected"
  fi

  # Development environment sophistication level
  local dev_tools=(mise comtrya sheldon trunk lefthook)
  local available_tools=0
  for tool in "${dev_tools[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
      ((available_tools++))
      capabilities+=("tool:$tool")
    fi
  done

  if [[ $available_tools -ge 3 ]]; then
    capabilities+=("advanced-dev")
    echo "🎯 Advanced development environment detected ($available_tools/5 tools)"
  fi

  # Architecture and platform detection
  local arch
  arch=$(uname -m)
  local platform
  platform=$(uname -s)
  capabilities+=("arch:$arch" "platform:$platform")

  echo "🧬 Capabilities: ${capabilities[*]}"
  printf '%s\n' "${capabilities[@]}"
}

# ============================================================================
# GitOps Configuration Management via Comtrya
# ============================================================================

bootstrap_comtrya_if_needed() {
  if ! command -v comtrya >/dev/null 2>&1; then
    echo "📦 Bootstrap: Installing Comtrya for configuration management..."

    # Intelligent installation based on environment
    if command -v cargo >/dev/null 2>&1; then
      cargo install comtrya
    elif command -v brew >/dev/null 2>&1; then
      brew install comtrya
    else
      # Fallback: direct installation
      local arch
      arch=$(uname -m)
      local platform
      platform=$(uname -s)
      local comtrya_url="https://github.com/comtrya/comtrya/releases/latest/download/comtrya-${platform,,}-${arch}"

      curl -fsSL "$comtrya_url" -o /usr/local/bin/comtrya
      chmod +x /usr/local/bin/comtrya
    fi

    echo "✅ Comtrya installed and ready"
  else
    echo "✅ Comtrya already available"
  fi
}

create_dynamic_comtrya_manifests() {
  local manifest_dir=".comtrya/manifests"
  mkdir -p "$manifest_dir"

  echo "📝 Generating dynamic Comtrya manifests..."

  # Base development tools manifest
  cat >"$manifest_dir/mentat-base.yaml" <<EOF
manifests:
  - name: mentat-base-tools
    description: "Mentat AI Assistant - Base Development Tools"
    
    actions:
      # Mise tool version manager
      - action: command.run
        command: |
          if ! command -v mise >/dev/null 2>&1; then
            curl https://mise.run | sh
            export PATH="\$HOME/.local/bin:\$PATH"
          fi
        
      # Install tools from .tool-versions via mise
      - action: command.run
        command: mise install
        directory: "{{ env.PWD }}"
        
      # Python development stack
      - action: command.run
        command: |
          # Use mise python, fall back to system python
          PYTHON_CMD=\$(mise which python 2>/dev/null || which python3 || which python)
          \$PYTHON_CMD -m pip install --user --upgrade pip setuptools wheel
          
          # Install from pyproject.toml if available
          if [[ -f pyproject.toml ]]; then
            \$PYTHON_CMD -m pip install --user "typer[all]>=0.9" "duckdb>=1.1.3" "rich>=13.7"
          fi
          
          # Code quality tools
          \$PYTHON_CMD -m pip install --user black isort ruff mypy pylint bandit
        
      # Trunk CLI for unified linting/formatting
      - action: command.run
        command: |
          if ! command -v trunk >/dev/null 2>&1; then
            curl -fsSL https://trunk.io/releases/latest/trunk | bash -s -- -b /usr/local/bin
          fi
          trunk --version || echo "Trunk installation verification failed"
        
    conditions:
      - action: command.run
        command: echo "Installing base tools for platform \$(uname -s)/\$(uname -m)"
EOF

  # Advanced tools and optimizations manifest
  cat >"$manifest_dir/mentat-advanced.yaml" <<EOF
manifests:
  - name: mentat-advanced-optimizations
    description: "Mentat AI Assistant - Advanced Optimizations & Glue"
    
    actions:
      # Shell enhancements via Sheldon
      - action: command.run
        command: |
          if ! command -v sheldon >/dev/null 2>&1; then
            if command -v cargo >/dev/null 2>&1; then
              cargo install sheldon
            elif command -v brew >/dev/null 2>&1; then
              brew install sheldon
            else
              echo "⚠️ Sheldon installation skipped (no cargo/brew available)"
            fi
          fi
        
      # Dynamic shell configuration
      - action: file.template
        source: templates/sheldon-plugins.toml.j2
        target: "{{ env.HOME }}/.config/sheldon/plugins.toml"
        variables:
          enable_fzf: true
          enable_zoxide: true
          enable_starship: true
          
      # Git hooks via lefthook (if configured)
      - action: command.run
        command: |
          if [[ -f lefthook.yml ]] && command -v lefthook >/dev/null 2>&1; then
            lefthook install
            echo "✅ Git hooks installed via lefthook"
          fi
        directory: "{{ env.PWD }}"
        
      # Performance optimizations
      - action: command.run
        command: |
          # Optimize git for large repos
          git config --global core.preloadindex true
          git config --global core.fscache true
          git config --global gc.auto 256
          
          # Enable parallel operations
          git config --global submodule.fetchJobs 4
          git config --global fetch.parallel 4
          
          echo "⚡ Git performance optimizations applied"
        
    conditions:
      - action: command.run
        command: echo "Applying advanced optimizations..."
EOF

  # Proactive enhancements based on detected capabilities
  local capabilities
  mapfile -t capabilities < <(detect_environment_capabilities)

  if printf '%s\n' "${capabilities[@]}" | grep -q "advanced-dev"; then
    cat >"$manifest_dir/mentat-proactive.yaml" <<EOF
manifests:
  - name: mentat-proactive-enhancements
    description: "Mentat AI Assistant - Proactive Intelligence Layer"
    
    actions:
      # AI-powered development enhancements
      - action: command.run
        command: |
          # Setup intelligent command history
          if command -v fzf >/dev/null 2>&1; then
            echo 'export FZF_DEFAULT_OPTS="--height 40% --layout=reverse --border"' >> ~/.bashrc
            echo 'export FZF_CTRL_T_OPTS="--preview '\''bat --color=always --style=numbers --line-range=:500 {}'\'' 2>/dev/null || cat {}"' >> ~/.bashrc
          fi
          
          # Enable mise automatic environment switching
          if command -v mise >/dev/null 2>&1; then
            echo 'eval "\$(mise activate bash)"' >> ~/.bashrc
            echo 'eval "\$(mise activate zsh)"' >> ~/.zshrc 2>/dev/null || true
          fi
          
          # Proactive project detection and optimization
          if [[ -f pyproject.toml ]] || [[ -f setup.py ]]; then
            echo "🐍 Python project detected - enabling enhanced Python tooling"
            mise use python@latest 2>/dev/null || true
          fi
          
          if [[ -f package.json ]]; then
            echo "📦 Node.js project detected - enabling enhanced Node tooling"
            mise use node@lts 2>/dev/null || true
          fi
          
          if [[ -f Cargo.toml ]]; then
            echo "🦀 Rust project detected - enabling enhanced Rust tooling"
            mise use rust@latest 2>/dev/null || true
          fi
          
      # Intelligent caching and performance monitoring
      - action: command.run
        command: |
          # Setup intelligent build caching
          mkdir -p ~/.cache/{mise,trunk,mentat}
          
          # Enable compression for better performance
          export GZIP_LEVEL=6
          export XZ_DEFAULTS="--threads=0"
          
          # Memory optimization for containers
          if [[ -f /.dockerenv ]]; then
            echo "🐳 Container optimizations enabled"
            export PYTHONDONTWRITEBYTECODE=1
            export PYTHONUNBUFFERED=1
          fi
          
    conditions:
      - action: command.run
        command: echo "Proactive enhancements activated"
EOF
  fi

  echo "✅ Dynamic Comtrya manifests generated"
}

# ============================================================================
# Intelligent Glue Layer - Tool Integration & Orchestration
# ============================================================================

setup_intelligent_glue() {
  echo "🔗 Setting up intelligent glue layer..."

  # Create wrapper scripts for seamless tool integration
  local bin_dir="$HOME/.local/bin"
  mkdir -p "$bin_dir"

  # Intelligent mentat command wrapper
  cat >"$bin_dir/mentat-env" <<'EOF'
#!/usr/bin/env bash
# Mentat Environment Intelligence Layer
set -euo pipefail

# Auto-detect and activate best available environment
if command -v mise >/dev/null 2>&1 && [[ -f .tool-versions ]]; then
    eval "$(mise activate bash)"
    echo "🎯 Mise environment activated"
fi

# Proactive optimization based on current directory
if [[ -f trunk.yaml ]] || [[ -f .trunk/trunk.yaml ]]; then
    export MENTAT_FORMATTER="trunk"
elif command -v black >/dev/null 2>&1; then
    export MENTAT_FORMATTER="black+isort+ruff"
else
    export MENTAT_FORMATTER="basic"
fi

# Intelligent resource allocation
if [[ -f /.dockerenv ]]; then
    export MENTAT_PARALLEL_JOBS=2
else
    export MENTAT_PARALLEL_JOBS=$(nproc)
fi

echo "🧬 Mentat environment prepared (formatter: $MENTAT_FORMATTER, jobs: $MENTAT_PARALLEL_JOBS)"
exec "$@"
EOF
  chmod +x "$bin_dir/mentat-env"

  # Integration health check and self-healing
  cat >"$bin_dir/mentat-doctor" <<'EOF'
#!/usr/bin/env bash
# Mentat Environment Doctor - Proactive Health Monitoring
set -euo pipefail

echo "🔍 Mentat Environment Health Check"
echo "=================================="

check_tool() {
    local tool=$1
    local status="❌"
    local version=""
    
    if command -v "$tool" >/dev/null 2>&1; then
        status="✅"
        version=$($tool --version 2>/dev/null | head -n1 || echo "version unknown")
    fi
    
    printf "%-20s %s %s\n" "$tool" "$status" "$version"
}

# Core tools assessment
echo "📊 Core Tools:"
check_tool "mise"
check_tool "comtrya"  
check_tool "sheldon"
check_tool "trunk"
check_tool "python3"
check_tool "node"
check_tool "git"

echo ""
echo "🔧 Environment Status:"
[[ -f .tool-versions ]] && echo "✅ .tool-versions detected" || echo "⚠️ .tool-versions missing"
[[ -f trunk.yaml ]] && echo "✅ trunk.yaml detected" || echo "⚠️ trunk.yaml missing"  
[[ -f lefthook.yml ]] && echo "✅ lefthook.yml detected" || echo "⚠️ lefthook.yml missing"

echo ""
echo "🚀 Performance Metrics:"
echo "CPU cores: $(nproc)"
echo "Memory: $(free -h | awk 'NR==2{printf "%.1fG/%.1fG (%.1f%%)", $3/1024/1024, $2/1024/1024, $3*100/$2}')"
echo "Disk usage: $(df -h . | awk 'NR==2{printf "%s/%s (%s)", $3, $2, $5}')"
EOF
  chmod +x "$bin_dir/mentat-doctor"

  echo "✅ Intelligent glue layer configured"
}

# ============================================================================
# Direct Configuration Fallback (when Comtrya is unavailable)
# ============================================================================

execute_direct_configuration() {
  echo "🔧 Executing direct configuration without Comtrya..."

  # Phase 4.1: Mise Tool Manager
  echo "📦 Phase 4.1: Setting up Mise tool manager..."
  if ! command -v mise >/dev/null 2>&1; then
    echo "📥 Installing mise..."
    curl https://mise.run | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ Mise installed"
  else
    echo "✅ Mise already available"
  fi

  # Install tools from .tool-versions if available
  if [[ -f .tool-versions ]]; then
    echo "🔧 Installing tools from .tool-versions..."
    mise install || echo "⚠️ Some tools failed to install via mise"
  fi

  # Phase 4.2: Python Development Stack
  echo "🐍 Phase 4.2: Setting up Python development stack..."

  # Determine best Python to use
  local python_cmd
  if python_cmd=$(mise which python 2>/dev/null); then
    echo "🎯 Using mise Python: $python_cmd"
  elif command -v python3 >/dev/null 2>&1; then
    python_cmd="python3"
    echo "🎯 Using system Python: $python_cmd"
  elif command -v python >/dev/null 2>&1; then
    python_cmd="python"
    echo "🎯 Using system Python: $python_cmd"
  else
    echo "❌ No Python found, skipping Python setup"
    return 1
  fi

  # Upgrade pip and essential tools
  echo "📦 Upgrading pip and essential Python tools..."
  $python_cmd -m pip install --user --upgrade pip setuptools wheel || echo "⚠️ pip upgrade failed"

  # Install project dependencies if pyproject.toml exists
  if [[ -f pyproject.toml ]]; then
    echo "📦 Installing project dependencies..."
    $python_cmd -m pip install --user "typer[all]>=0.9" "duckdb>=1.1.3" "rich>=13.7" || echo "⚠️ Some project dependencies failed"
  fi

  # Install code quality tools
  echo "🔍 Installing Python code quality tools..."
  $python_cmd -m pip install --user black isort ruff mypy pylint bandit || echo "⚠️ Some code quality tools failed"

  # Phase 4.3: Trunk CLI
  echo "🌳 Phase 4.3: Setting up Trunk CLI..."
  if ! command -v trunk >/dev/null 2>&1; then
    echo "📥 Installing Trunk CLI..."
    if curl -fsSL https://trunk.io/releases/latest/trunk | bash -s -- -b /usr/local/bin; then
      echo "✅ Trunk CLI installed"
      trunk --version || echo "⚠️ Trunk installation verification failed"
    else
      echo "⚠️ Trunk CLI installation failed"
    fi
  else
    echo "✅ Trunk CLI already available"
  fi

  # Phase 4.4: Shell Enhancements (Sheldon)
  echo "🐚 Phase 4.4: Setting up shell enhancements..."
  if ! command -v sheldon >/dev/null 2>&1; then
    if command -v cargo >/dev/null 2>&1; then
      echo "📥 Installing Sheldon via Cargo..."
      cargo install sheldon || echo "⚠️ Sheldon installation via cargo failed"
    elif command -v brew >/dev/null 2>&1; then
      echo "📥 Installing Sheldon via Homebrew..."
      brew install sheldon || echo "⚠️ Sheldon installation via brew failed"
    else
      echo "⚠️ Sheldon installation skipped (no cargo/brew available)"
    fi
  else
    echo "✅ Sheldon already available"
  fi

  # Setup shell configuration if sheldon is available
  if command -v sheldon >/dev/null 2>&1; then
    echo "🔧 Configuring shell enhancements..."
    mkdir -p "$HOME/.config/sheldon"

    # Create basic sheldon config (without template engine)
    cat >"$HOME/.config/sheldon/plugins.toml" <<'SHELDON_EOF'
# Sheldon Plugin Configuration for Mentat AI Assistant
[plugins]

[plugins.fzf]
github = "junegunn/fzf"
apply = ["defer"]

[plugins.zsh-autosuggestions]
github = "zsh-users/zsh-autosuggestions"
apply = ["defer"]

[plugins.zsh-syntax-highlighting]
github = "zsh-users/zsh-syntax-highlighting"
apply = ["defer"]

# Mentat-specific enhancements
[plugins.mentat-aliases]
inline = '''
# Mentat AI Assistant aliases
alias mentat-setup="bash ~/.mentat/setup.sh"
alias mentat-format="bash ~/.mentat/format.sh"
alias mentat-doctor="~/.local/bin/mentat-doctor"

# Development productivity
alias ll="ls -la"
alias gs="git status"
alias ga="git add"
alias gc="git commit"
alias gp="git push"
'''
SHELDON_EOF
    echo "✅ Shell configuration created"
  fi

  # Phase 4.5: Git Hooks (Lefthook)
  echo "🪝 Phase 4.5: Setting up Git hooks..."
  if [[ -f lefthook.yml ]] && command -v lefthook >/dev/null 2>&1; then
    echo "📥 Installing lefthook hooks..."
    lefthook install || echo "⚠️ Lefthook installation failed"
  else
    echo "ℹ️ Lefthook not available or not configured"
  fi

  # Phase 4.6: Git Performance Optimizations
  echo "⚡ Phase 4.6: Applying Git performance optimizations..."
  git config --global core.preloadindex true || true
  git config --global core.fscache true || true
  git config --global gc.auto 256 || true
  git config --global submodule.fetchJobs 4 || true
  git config --global fetch.parallel 4 || true
  echo "✅ Git performance optimizations applied"

  # Phase 4.7: Project-Specific Intelligence
  echo "🧠 Phase 4.7: Applying project-specific optimizations..."

  # Python project detection
  if [[ -f pyproject.toml ]] || [[ -f setup.py ]]; then
    echo "🐍 Python project detected - enabling enhanced Python tooling"
    mise use python@latest 2>/dev/null || echo "ℹ️ Could not set Python version via mise"
  fi

  # Node.js project detection
  if [[ -f package.json ]]; then
    echo "📦 Node.js project detected - enabling enhanced Node tooling"
    mise use node@lts 2>/dev/null || echo "ℹ️ Could not set Node version via mise"
  fi

  # Rust project detection
  if [[ -f Cargo.toml ]]; then
    echo "🦀 Rust project detected - enabling enhanced Rust tooling"
    mise use rust@latest 2>/dev/null || echo "ℹ️ Could not set Rust version via mise"
  fi

  # Phase 4.8: Performance Enhancements
  echo "🚀 Phase 4.8: Setting up performance enhancements..."

  # Setup intelligent build caching
  mkdir -p ~/.cache/{mise,trunk,mentat} || true

  # Container-specific optimizations
  if [[ -f /.dockerenv ]]; then
    echo "🐳 Container optimizations enabled"
    export PYTHONDONTWRITEBYTECODE=1
    export PYTHONUNBUFFERED=1
    echo 'export PYTHONDONTWRITEBYTECODE=1' >>~/.bashrc || true
    echo 'export PYTHONUNBUFFERED=1' >>~/.bashrc || true
  fi

  echo "✅ Direct configuration completed successfully"
}

# ============================================================================
# Main Orchestration with Proactive Intelligence
# ============================================================================

main() {
  echo "🎯 Mentat Dynamic Setup - Advanced GitOps Integration"
  echo "===================================================="

  # Phase 1: Environment Intelligence
  echo "🔍 Phase 1: Environment Analysis & Intelligence"
  local capabilities
  mapfile -t capabilities < <(detect_environment_capabilities)

  # Phase 2: Bootstrap Core Infrastructure
  echo "🏗️ Phase 2: Bootstrap Configuration Management"
  bootstrap_comtrya_if_needed

  # Phase 3: Generate Dynamic Manifests
  echo "📝 Phase 3: Dynamic Manifest Generation"
  create_dynamic_comtrya_manifests

  # Phase 4: Execute GitOps Configuration
  echo "🚀 Phase 4: GitOps Configuration Execution"

  # Try comtrya first, but with robust fallback
  local comtrya_success=false

  if command -v comtrya >/dev/null 2>&1; then
    echo "🎯 Attempting Comtrya-based configuration..."

    # Check if comtrya can apply manifests (newer versions use different syntax)
    if comtrya apply --help >/dev/null 2>&1; then
      # Try modern comtrya syntax
      if comtrya apply --manifests .comtrya/manifests/ 2>/dev/null ||
        comtrya apply -m .comtrya/manifests/ 2>/dev/null ||
        (cd .comtrya && comtrya apply) 2>/dev/null; then
        comtrya_success=true
        echo "✅ Comtrya configuration applied successfully"
      fi
    fi
  fi

  # Fallback to direct execution if comtrya fails
  if [[ "$comtrya_success" == false ]]; then
    echo "🔄 Comtrya failed or unavailable, executing configuration directly..."
    execute_direct_configuration
  fi

  # Phase 5: Intelligent Glue & Integration
  echo "🔗 Phase 5: Intelligent Glue Layer"
  setup_intelligent_glue

  # Phase 6: Health Verification & Optimization
  echo "🔍 Phase 6: Health Verification"
  if [[ -x "$HOME/.local/bin/mentat-doctor" ]]; then
    "$HOME/.local/bin/mentat-doctor"
  fi

  # Performance metrics and completion
  local setup_duration=$(($(date +%s) - SETUP_START_TIME))
  echo ""
  echo "🎉 Mentat Dynamic Setup Complete!"
  echo "================================="
  echo "⏱️ Total time: ${setup_duration}s"
  echo "📊 Log file: $SETUP_LOG"
  echo "🔧 Environment doctor: mentat-doctor"
  echo "🚀 Environment wrapper: mentat-env"
  echo ""
  echo "Next: Run 'mentat-doctor' to verify installation"
}

# Execute main orchestration
main "$@"
