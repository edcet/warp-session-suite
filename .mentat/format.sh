#!/usr/bin/env bash
# Automatic code formatting script - only auto-fixing formatters
# Tests and validation-only linters are handled by CI workflows

# Use trunk for most formatting if available, otherwise fall back to individual tools
if command -v trunk >/dev/null 2>&1; then
  echo "🎨 Running trunk formatters..."
  trunk fmt --all
else
  echo "🎨 Running individual formatters..."

  # Format Python code with Black (auto-fix)
  if command -v black >/dev/null 2>&1; then
    echo "🐍 Formatting Python code with Black..."
    find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./.trunk/*" -print0 | xargs -0 black --line-length 100 --quiet
  fi

  # Sort Python imports with isort (auto-fix)
  if command -v isort >/dev/null 2>&1; then
    echo "📦 Sorting imports with isort..."
    find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./.trunk/*" -print0 | xargs -0 isort --profile black --quiet
  fi

  # Fix Python issues with ruff (auto-fix only)
  if command -v ruff >/dev/null 2>&1; then
    echo "🔧 Fixing Python issues with ruff..."
    ruff check --fix --quiet . || true
    ruff format --quiet . || true
  fi

  # Format JavaScript/TypeScript/JSON/YAML with prettier (auto-fix)
  if command -v prettier >/dev/null 2>&1; then
    echo "✨ Formatting with prettier..."
    prettier --write "**/*.{js,ts,json,yaml,yml,md}" --ignore-path .gitignore || true
  fi

  # Format shell scripts with shfmt (auto-fix)
  if command -v shfmt >/dev/null 2>&1; then
    echo "🐚 Formatting shell scripts..."
    find . -name "*.sh" -not -path "./.git/*" -not -path "./.trunk/*" -print0 | xargs -0 shfmt -w -i 2 2>/dev/null || true
  fi
fi

echo "✅ Code formatting completed!"
