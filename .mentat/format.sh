#!/usr/bin/env bash
# Automatic formatting and linting script for warp-session-suite

echo "🎨 Running automatic code formatting..."

# Format Python code with Black
echo "🐍 Formatting Python code with Black..."
python3 -m black --line-length 100 --quiet .

# Sort imports with isort
echo "📦 Sorting imports with isort..."
python3 -m isort --profile black --quiet .

# Fix Python code issues with ruff
echo "🔧 Fixing Python code issues with ruff..."
python3 -m ruff check --fix --quiet .
python3 -m ruff format --quiet .

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

# Clean up cache files
echo "🧹 Cleaning up cache files..."
rm -rf .trunk/actions .trunk/logs .trunk/notifications .trunk/out .trunk/plugins .trunk/tools 2>/dev/null || true

echo "✅ Formatting completed!"
