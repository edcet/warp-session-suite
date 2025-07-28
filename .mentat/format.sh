#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Mentat Format - Unified Architecture Integration
# Leverages existing mise-centric workflow for zero configuration drift
# ============================================================================

echo "🎨 Mentat AI Assistant Format"
echo "============================="

# Delegate to the unified mise-based formatting
echo "🔄 Delegating to mise task for formatting..."
exec mise run mentat:format
