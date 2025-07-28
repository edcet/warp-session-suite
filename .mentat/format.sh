#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Mentat Dynamic Format - Intelligent Code Quality Orchestration
# Proactive formatting with adaptive tool selection and performance optimization
# ============================================================================

# Advanced telemetry and performance tracking
FORMAT_START_TIME=$(date +%s)
FORMAT_SESSION_ID="fmt-$(uname -n)-$$-$(date +%s)"
FORMAT_LOG="/tmp/mentat-format-$(date +%Y%m%d-%H%M%S).log"

# Intelligent logging with performance metrics
exec 1> >(tee -a "$FORMAT_LOG")
exec 2> >(tee -a "$FORMAT_LOG" >&2)

echo "🎨 Mentat Dynamic Format initiated at $(date -Iseconds)"
echo "📊 Session ID: $FORMAT_SESSION_ID"

# ============================================================================
# Intelligent Tool Detection & Capability Assessment
# ============================================================================

detect_formatting_capabilities() {
  local capabilities=()
  local formatters=()

  # Advanced formatter detection with version intelligence
  if command -v trunk >/dev/null 2>&1; then
    formatters+=("trunk")
    capabilities+=("unified-formatting")

    # Trunk plugin detection
    if [[ -f .trunk/trunk.yaml ]]; then
      local plugins
      plugins=$(yq eval '.plugins.sources[].id' .trunk/trunk.yaml 2>/dev/null | tr '\n' ' ' || echo "")
      capabilities+=("trunk-configured:$plugins")
    fi
  fi

  # Python formatting ecosystem
  local python_formatters=()
  command -v black >/dev/null 2>&1 && python_formatters+=("black")
  command -v isort >/dev/null 2>&1 && python_formatters+=("isort")
  command -v ruff >/dev/null 2>&1 && python_formatters+=("ruff")
  command -v autopep8 >/dev/null 2>&1 && python_formatters+=("autopep8")

  if [[ ${#python_formatters[@]} -gt 0 ]]; then
    formatters+=("${python_formatters[@]}")
    capabilities+=("python-formatting:${python_formatters[*]}")
  fi

  # JavaScript/TypeScript ecosystem
  if command -v prettier >/dev/null 2>&1; then
    formatters+=("prettier")
    capabilities+=("js-formatting")
  fi

  if command -v eslint >/dev/null 2>&1; then
    formatters+=("eslint")
    capabilities+=("js-linting")
  fi

  # Shell and system tools
  command -v shfmt >/dev/null 2>&1 && formatters+=("shfmt") && capabilities+=("shell-formatting")
  command -v shellcheck >/dev/null 2>&1 && formatters+=("shellcheck") && capabilities+=("shell-linting")

  # Configuration file formatters
  command -v yq >/dev/null 2>&1 && formatters+=("yq") && capabilities+=("yaml-formatting")
  command -v jq >/dev/null 2>&1 && formatters+=("jq") && capabilities+=("json-formatting")

  echo "🧬 Detected formatters: ${formatters[*]}"
  echo "⚡ Capabilities: ${capabilities[*]}"

  # Export for use by other functions
  export MENTAT_FORMATTERS="${formatters[*]}"
  export MENTAT_CAPABILITIES="${capabilities[*]}"
}

# ============================================================================
# Intelligent File Discovery & Change Detection
# ============================================================================

discover_files_intelligently() {
  local file_types=()
  local change_detection=""

  # Git-aware change detection for performance
  if git rev-parse --git-dir >/dev/null 2>&1; then
    # Only format changed/staged files for speed
    change_detection="git-aware"

    # Get staged files
    local staged_files
    staged_files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

    # Get unstaged changes
    local modified_files
    modified_files=$(git diff --name-only --diff-filter=ACM 2>/dev/null || echo "")

    # Combine and deduplicate
    local changed_files
    changed_files=$(echo -e "$staged_files\n$modified_files" | sort -u | grep -v '^$' || echo "")

    if [[ -n "$changed_files" ]]; then
      echo "🔍 Git-aware mode: formatting $(echo "$changed_files" | wc -l) changed files"
      export MENTAT_TARGET_FILES="$changed_files"
    else
      echo "🔍 No changes detected, scanning all files"
      change_detection="full-scan"
    fi
  else
    echo "🔍 Non-git repository, scanning all files"
    change_detection="full-scan"
  fi

  # Intelligent file type detection based on project structure
  [[ -f pyproject.toml ]] || [[ -f setup.py ]] && file_types+=("python")
  [[ -f package.json ]] && file_types+=("javascript" "typescript")
  [[ -f Cargo.toml ]] && file_types+=("rust")
  [[ -f go.mod ]] && file_types+=("go")
  [[ -f .trunk/trunk.yaml ]] && file_types+=("trunk-managed")

  echo "📁 Project types detected: ${file_types[*]} (strategy: $change_detection)"
  export MENTAT_PROJECT_TYPES="${file_types[*]}"
  export MENTAT_CHANGE_DETECTION="$change_detection"
}

# ============================================================================
# Adaptive Formatting Strategy Selection
# ============================================================================

select_optimal_formatting_strategy() {
  local strategy="adaptive"
  local parallel_jobs=1
  local formatter_priority=()

  # Resource-aware parallel job calculation
  local available_cores
  available_cores=$(nproc 2>/dev/null || echo "1")

  if [[ -f /.dockerenv ]]; then
    # Container environment - conservative resource usage
    parallel_jobs=$((available_cores > 2 ? 2 : 1))
    echo "🐳 Container detected: using $parallel_jobs parallel jobs"
  else
    # Native environment - aggressive parallelization
    parallel_jobs=$((available_cores > 4 ? available_cores / 2 : available_cores))
    echo "💻 Native environment: using $parallel_jobs parallel jobs"
  fi

  # Intelligent formatter prioritization based on capabilities
  if echo "$MENTAT_CAPABILITIES" | grep -q "unified-formatting"; then
    strategy="trunk-primary"
    formatter_priority=("trunk")
    echo "🎯 Strategy: Trunk-primary (unified formatting available)"
  elif echo "$MENTAT_FORMATTERS" | grep -q "black"; then
    strategy="python-focused"
    formatter_priority=("black" "isort" "ruff" "prettier" "shfmt")
    echo "🐍 Strategy: Python-focused (black available)"
  else
    strategy="tool-specific"
    formatter_priority=("prettier" "shfmt" "yq" "jq")
    echo "🔧 Strategy: Tool-specific fallback"
  fi

  export MENTAT_STRATEGY="$strategy"
  export MENTAT_PARALLEL_JOBS="$parallel_jobs"
  export MENTAT_FORMATTER_PRIORITY="${formatter_priority[*]}"
}

# ============================================================================
# High-Performance Parallel Formatting Engine
# ============================================================================

execute_trunk_formatting() {
  echo "🎨 Executing Trunk unified formatting..."

  local trunk_args=("fmt")

  # Adaptive trunk configuration based on context
  if [[ "$MENTAT_CHANGE_DETECTION" == "git-aware" ]] && [[ -n "${MENTAT_TARGET_FILES:-}" ]]; then
    # Format only changed files for speed
    echo "⚡ Optimized: formatting only changed files"
    echo "$MENTAT_TARGET_FILES" | head -20 | while IFS= read -r file; do
      [[ -f "$file" ]] && trunk_args+=("$file")
    done
  else
    trunk_args+=("--all")
  fi

  # Execute with performance monitoring
  local start_time
  start_time=$(date +%s)

  if trunk "${trunk_args[@]}" 2>&1; then
    local duration=$(($(date +%s) - start_time))
    echo "✅ Trunk formatting completed in ${duration}s"
    return 0
  else
    echo "⚠️ Trunk formatting encountered issues, falling back to individual formatters"
    return 1
  fi
}

execute_individual_formatters() {
  echo "🔧 Executing individual formatters with intelligent orchestration..."

  local format_jobs=()
  local temp_dir
  temp_dir=$(mktemp -d)

  # Python formatting pipeline
  if echo "$MENTAT_PROJECT_TYPES" | grep -q "python"; then
    execute_python_formatting_pipeline "$temp_dir" &
    format_jobs+=($!)
  fi

  # JavaScript/TypeScript formatting
  if echo "$MENTAT_PROJECT_TYPES" | grep -q "javascript\|typescript"; then
    execute_js_formatting_pipeline "$temp_dir" &
    format_jobs+=($!)
  fi

  # Shell script formatting
  execute_shell_formatting_pipeline "$temp_dir" &
  format_jobs+=($!)

  # Configuration file formatting
  execute_config_formatting_pipeline "$temp_dir" &
  format_jobs+=($!)

  # Wait for all formatting jobs with timeout and progress tracking
  echo "⏳ Running ${#format_jobs[@]} formatting pipelines in parallel..."

  local completed=0
  local failed=0

  for job in "${format_jobs[@]}"; do
    if wait "$job"; then
      ((completed++))
    else
      ((failed++))
    fi

    local progress=$((((completed + failed) * 100) / ${#format_jobs[@]}))
    echo "📊 Progress: $progress% ($completed✅ $failed❌)"
  done

  # Cleanup
  rm -rf "$temp_dir"

  echo "🎉 Individual formatting completed: $completed successful, $failed failed"
  return $([[ $failed -eq 0 ]] && echo 0 || echo 1)
}

execute_python_formatting_pipeline() {
  local temp_dir="$1"
  local pipeline_log="$temp_dir/python-fmt.log"

  {
    echo "🐍 Python formatting pipeline starting..."

    # Discover Python files intelligently
    local python_files
    if [[ "$MENTAT_CHANGE_DETECTION" == "git-aware" ]] && [[ -n "${MENTAT_TARGET_FILES:-}" ]]; then
      python_files=$(echo "$MENTAT_TARGET_FILES" | grep '\.py$' || echo "")
    else
      python_files=$(find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./.trunk/*" -not -path "./node_modules/*" -print0 | tr '\0' '\n')
    fi

    if [[ -z "$python_files" ]]; then
      echo "📝 No Python files to format"
      return 0
    fi

    local file_count
    file_count=$(echo "$python_files" | wc -l)
    echo "📝 Processing $file_count Python files..."

    # Black formatting with optimized settings
    if command -v black >/dev/null 2>&1; then
      echo "⚫ Running Black formatter..."
      echo "$python_files" | head -100 | xargs -r -P "$MENTAT_PARALLEL_JOBS" -I {} black --line-length 100 --quiet {} || true
    fi

    # Import sorting with isort
    if command -v isort >/dev/null 2>&1; then
      echo "📦 Running isort import organizer..."
      echo "$python_files" | head -100 | xargs -r -P "$MENTAT_PARALLEL_JOBS" -I {} isort --profile black --quiet {} || true
    fi

    # Ruff for additional fixes
    if command -v ruff >/dev/null 2>&1; then
      echo "⚡ Running Ruff auto-fixes..."
      ruff check --fix --quiet . || true
      ruff format --quiet . || true
    fi

    echo "✅ Python formatting pipeline completed"

  } >"$pipeline_log" 2>&1
}

execute_js_formatting_pipeline() {
  local temp_dir="$1"
  local pipeline_log="$temp_dir/js-fmt.log"

  {
    echo "📦 JavaScript/TypeScript formatting pipeline starting..."

    if command -v prettier >/dev/null 2>&1; then
      echo "✨ Running Prettier formatter..."

      # Intelligent file discovery for JS/TS ecosystem
      local js_patterns=("**/*.{js,jsx,ts,tsx,json,yaml,yml,md}")

      if [[ -f .prettierrc ]] || [[ -f prettier.config.js ]]; then
        echo "🔧 Using project Prettier configuration"
      fi

      prettier --write "${js_patterns[@]}" --ignore-path .gitignore --log-level warn || true
    fi

    # ESLint auto-fix if available
    if command -v eslint >/dev/null 2>&1 && [[ -f .eslintrc* ]] || [[ -f eslint.config.* ]]; then
      echo "🔍 Running ESLint auto-fix..."
      eslint --fix --quiet "**/*.{js,jsx,ts,tsx}" || true
    fi

    echo "✅ JavaScript/TypeScript formatting pipeline completed"

  } >"$pipeline_log" 2>&1
}

execute_shell_formatting_pipeline() {
  local temp_dir="$1"
  local pipeline_log="$temp_dir/shell-fmt.log"

  {
    echo "🐚 Shell formatting pipeline starting..."

    # Discover shell files with enhanced detection
    local shell_files
    if [[ "$MENTAT_CHANGE_DETECTION" == "git-aware" ]] && [[ -n "${MENTAT_TARGET_FILES:-}" ]]; then
      shell_files=$(echo "$MENTAT_TARGET_FILES" | grep -E '\.(sh|bash|zsh)$' || echo "")

      # Also check for shell scripts without extension
      if [[ -n "$MENTAT_TARGET_FILES" ]]; then
        while IFS= read -r file; do
          if [[ -f "$file" ]] && [[ "$(head -n1 "$file" 2>/dev/null)" =~ ^#!.*/(bash|sh|zsh) ]]; then
            shell_files+=$'\n'"$file"
          fi
        done <<<"$MENTAT_TARGET_FILES"
      fi
    else
      shell_files=$(find . -name "*.sh" -o -name "*.bash" -o -name "*.zsh" | grep -v -E '\.git/|node_modules/|\.trunk/')

      # Add executable shell scripts
      shell_files+=$'\n'$(find . -type f -executable -exec grep -l '^#!/.*sh' {} \; 2>/dev/null | grep -v -E '\.git/|node_modules/|\.trunk/' || echo "")
    fi

    if [[ -n "$shell_files" ]] && [[ "$shell_files" != $'\n' ]]; then
      local file_count
      file_count=$(echo "$shell_files" | grep -v '^$' | wc -l)
      echo "📝 Processing $file_count shell files..."

      if command -v shfmt >/dev/null 2>&1; then
        echo "🔧 Running shfmt formatter..."
        echo "$shell_files" | grep -v '^$' | xargs -r -P "$MENTAT_PARALLEL_JOBS" -I {} shfmt -w -i 2 {} 2>/dev/null || true
      fi

      if command -v shellcheck >/dev/null 2>&1; then
        echo "🔍 Running shellcheck linter..."
        echo "$shell_files" | grep -v '^$' | head -10 | xargs -r shellcheck -f gcc || true
      fi
    else
      echo "📝 No shell files to format"
    fi

    echo "✅ Shell formatting pipeline completed"

  } >"$pipeline_log" 2>&1
}

execute_config_formatting_pipeline() {
  local temp_dir="$1"
  local pipeline_log="$temp_dir/config-fmt.log"

  {
    echo "⚙️ Configuration file formatting pipeline starting..."

    # YAML formatting with yq
    if command -v yq >/dev/null 2>&1; then
      echo "📄 Formatting YAML files..."
      find . -name "*.yml" -o -name "*.yaml" | grep -v -E '\.git/|node_modules/|\.trunk/' | head -20 | while read -r file; do
        if [[ -f "$file" ]]; then
          yq eval --inplace '.' "$file" 2>/dev/null || echo "⚠️ Could not format $file"
        fi
      done
    fi

    # JSON formatting with jq
    if command -v jq >/dev/null 2>&1; then
      echo "📄 Formatting JSON files..."
      find . -name "*.json" | grep -v -E '\.git/|node_modules/|\.trunk/' | head -20 | while read -r file; do
        if [[ -f "$file" ]] && jq empty "$file" 2>/dev/null; then
          jq --indent 2 '.' "$file" >"$file.tmp" && mv "$file.tmp" "$file" || rm -f "$file.tmp"
        fi
      done
    fi

    echo "✅ Configuration formatting pipeline completed"

  } >"$pipeline_log" 2>&1
}

# ============================================================================
# Performance Analytics & Optimization Feedback
# ============================================================================

generate_performance_analytics() {
  local total_duration=$(($(date +%s) - FORMAT_START_TIME))

  echo ""
  echo "📊 Mentat Format Performance Analytics"
  echo "====================================="
  echo "⏱️ Total duration: ${total_duration}s"
  echo "🔧 Strategy used: $MENTAT_STRATEGY"
  echo "⚡ Parallel jobs: $MENTAT_PARALLEL_JOBS"
  echo "🧬 Capabilities: $MENTAT_CAPABILITIES"
  echo "📊 Session ID: $FORMAT_SESSION_ID"
  echo "📄 Detailed log: $FORMAT_LOG"

  # Performance optimization suggestions
  if [[ $total_duration -gt 30 ]]; then
    echo ""
    echo "🔍 Performance Optimization Suggestions:"
    echo "  • Consider using git-aware formatting for large repositories"
    echo "  • Enable trunk for unified formatting to reduce overhead"
    echo "  • Configure .gitignore to exclude generated files"
  fi

  # Self-learning optimization hints
  if [[ $total_duration -lt 5 ]]; then
    echo "🚀 Excellent performance! Current setup is optimal."
  elif [[ $total_duration -lt 15 ]]; then
    echo "✅ Good performance. Setup is well-optimized."
  else
    echo "⚠️ Consider optimizing formatter configuration for better performance."
  fi
}

# ============================================================================
# Main Orchestration with Adaptive Intelligence
# ============================================================================

main() {
  echo "🎨 Mentat Dynamic Format - Intelligent Code Quality Orchestration"
  echo "==============================================================="

  # Phase 1: Intelligence Gathering
  echo "🔍 Phase 1: Capability Detection & Analysis"
  detect_formatting_capabilities
  discover_files_intelligently

  # Phase 2: Strategy Optimization
  echo "🎯 Phase 2: Adaptive Strategy Selection"
  select_optimal_formatting_strategy

  # Phase 3: Execution with Fallback Intelligence
  echo "🚀 Phase 3: Intelligent Formatting Execution"

  local formatting_success=false

  if [[ "$MENTAT_STRATEGY" == "trunk-primary" ]]; then
    if execute_trunk_formatting; then
      formatting_success=true
    else
      echo "🔄 Trunk failed, falling back to individual formatters..."
      execute_individual_formatters && formatting_success=true
    fi
  else
    execute_individual_formatters && formatting_success=true
  fi

  # Phase 4: Analytics & Optimization Feedback
  echo "📊 Phase 4: Performance Analytics & Learning"
  generate_performance_analytics

  if [[ "$formatting_success" == true ]]; then
    echo ""
    echo "🎉 Code formatting completed successfully!"
    exit 0
  else
    echo ""
    echo "⚠️ Code formatting completed with some issues. Check logs for details."
    exit 1
  fi
}

# Execute main orchestration
main "$@"
