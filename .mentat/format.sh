#!/usr/bin/env bash
# Automatic formatting and linting script for CI/CD pipeline
set -euo pipefail

echo "🎨 Running automatic code formatting and quality checks..."

# Install required dependencies if not available
if ! python3 -c "import black" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install --user black isort ruff PyYAML
fi

# Format Python code with Black
echo "🐍 Formatting Python code with Black..."
find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" | xargs python3 -m black --line-length 100 --quiet

# Sort imports with isort
echo "📦 Sorting imports with isort..."
find . -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" | xargs python3 -m isort --profile black --quiet

# Fix common syntax issues
echo "🔧 Fixing common Python syntax issues..."
find . -name "*.py" -not -path "./.git/*" -exec sed -i 's/lefthook_config_content = """/lefthook_config_content = r"""/g' {} \; 2>/dev/null || true

# Format YAML files if yq is available
if command -v yq >/dev/null 2>&1; then
    echo "📝 Formatting YAML files..."
    find . -name "*.yml" -o -name "*.yaml" | grep -v ".git" | while read -r file; do
        yq eval '.' "$file" > "$file.tmp" && mv "$file.tmp" "$file" 2>/dev/null || rm -f "$file.tmp"
    done
fi

# Format shell scripts if shfmt is available
if command -v shfmt >/dev/null 2>&1; then
    echo "🐚 Formatting shell scripts..."
    find . -name "*.sh" -not -path "./.git/*" -exec shfmt -w -i 2 {} \; 2>/dev/null || true
fi

echo "✅ Formatting and quality checks completed!"
