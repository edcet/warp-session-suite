#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Mentat Format - Unified Architecture Integration
# Leverages existing mise-centric workflow for zero configuration drift
# ============================================================================

echo "🎨 Mentat AI Assistant Format"
echo "============================="

# Ensure mise configuration is trusted
echo "🔐 Trusting mise configuration..."
mise trust 2>/dev/null || true

# Delegate to the unified mise-based formatting
echo "🔄 Delegating to mise task for formatting..."
exec mise run mentat:format
