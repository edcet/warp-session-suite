#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Mentat Setup - Unified Architecture Integration
# Leverages existing mise-centric workflow for zero configuration drift
# ============================================================================

echo "🤖 Mentat AI Assistant Setup"
echo "============================"

# Delegate to the unified mise-based setup
echo "🔄 Delegating to mise task for setup..."
exec mise run mentat:setup
