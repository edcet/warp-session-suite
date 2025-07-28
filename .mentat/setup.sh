#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Mentat Setup - Unified Architecture Integration
# Leverages existing mise-centric workflow for zero configuration drift
# ============================================================================

echo "🤖 Mentat AI Assistant Setup"
echo "============================"

# Ensure mise configuration is trusted
echo "🔐 Trusting mise configuration..."
mise trust 2>/dev/null || true

# Delegate to the unified mise-based setup
echo "🔄 Delegating to mise task for setup..."
exec mise run mentat:setup
