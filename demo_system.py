#!/usr/bin/env python3
"""
Unified Terminal Automation System - Complete Demonstration
Showcases the full integration of Warp, Cursor, Windsurf, and AI automation
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n🔧 {description}")
    print("=" * 60)

    try:
        if isinstance(cmd, list):
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)

        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("⏱️ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Complete system demonstration."""

    print("🚀 UNIFIED TERMINAL AUTOMATION SYSTEM")
    print("=====================================")
    print("Revolutionary AI-Native Development Environment with Multi-Tool Integration")
    print(f"Demonstration started: {datetime.now().isoformat()}")

    # Test results tracking
    tests = []

    # 1. System Overview
    print("\n📊 SYSTEM OVERVIEW")
    print("==================")

    # Check plugin registry
    try:
        with open("plugins/registry.json") as f:
            registry = json.load(f)
        plugin_count = len(registry["plugins"])
        print(f"🔌 Plugins registered: {plugin_count}")
        for name, info in registry["plugins"].items():
            entry_path = Path(info["entry"])
            status = "✅" if entry_path.exists() else "❌"
            print(f"   {status} {name}: {info['name']}")
    except Exception as e:
        print(f"❌ Plugin registry error: {e}")

    # 2. Unified CLI Interface
    tests.append(
        (
            "Unified CLI Help",
            run_command("python3 unified_cli.py --help", "Testing unified CLI interface"),
        )
    )

    # 3. Plugin System Tests
    tests.append(
        (
            "Plugin Listing",
            run_command("python3 unified_cli.py plugins", "Testing plugin discovery"),
        )
    )

    # 4. Warp Integration Tests
    tests.append(
        (
            "Warp Plugin Test",
            run_command(
                "python3 plugins/warp/src/main.py test --hours 1",
                "Testing Warp plugin functionality",
            ),
        )
    )

    tests.append(
        (
            "Warp Session Analysis",
            run_command(
                "python3 plugins/warp/src/main.py analyze --hours 24",
                "Testing Warp usage analytics",
            ),
        )
    )

    tests.append(
        (
            "Warp Recovery Script",
            run_command(
                "python3 plugins/warp/src/main.py recover --hours 1",
                "Testing recovery script generation",
            ),
        )
    )

    # 5. Multi-Tool Plugin Tests
    tests.append(
        (
            "Cursor Plugin Test",
            run_command("python3 plugins/cursor/src/main.py test", "Testing Cursor AI integration"),
        )
    )

    tests.append(
        (
            "Windsurf Plugin Test",
            run_command(
                "python3 plugins/windsurf/src/main.py test", "Testing Windsurf context routing"
            ),
        )
    )

    tests.append(
        (
            "Windsurf Command Enhancement",
            run_command(
                "python3 plugins/windsurf/src/main.py enhance --cmd 'git status'",
                "Testing command enhancement",
            ),
        )
    )

    # 6. AI Integration Test
    tests.append(
        (
            "AI Plugin Test",
            run_command(
                "python3 plugins/ai/tgpt/integration.py test", "Testing AI integration framework"
            ),
        )
    )

    # 7. Unified CLI Command Tests
    tests.append(
        (
            "Unified Warp Recovery",
            run_command(
                "python3 unified_cli.py warp recover 1", "Testing Warp recovery via unified CLI"
            ),
        )
    )

    # 8. System Health Check (simulated)
    print("\n🏥 SYSTEM HEALTH CHECK")
    print("======================")

    health_checks = [
        ("Python Environment", sys.version_info >= (3, 8)),
        ("Plugin Directory", Path("plugins").exists()),
        ("Plugin Registry", Path("plugins/registry.json").exists()),
        ("Warp Plugin", Path("plugins/warp/src/main.py").exists()),
        ("Cursor Plugin", Path("plugins/cursor/src/main.py").exists()),
        ("Windsurf Plugin", Path("plugins/windsurf/src/main.py").exists()),
        ("AI Plugin", Path("plugins/ai/tgpt/integration.py").exists()),
        ("Unified CLI", Path("unified_cli.py").exists()),
        ("Mise Configuration", Path("mise.toml").exists()),
    ]

    for check_name, result in health_checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")

    # Summary
    print("\n📈 TEST RESULTS SUMMARY")
    print("=======================")

    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    success_rate = (passed / total) * 100 if total > 0 else 0

    for test_name, result in tests:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")

    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed}/{total})")

    # Generated Files
    print("\n📁 GENERATED FILES")
    print("==================")

    generated_files = [
        "warp_recovery.sh",
        "warp_session_backup.json",
        "obsidian_export/",
        "cursor_session_backup_*.json",
    ]

    for file_pattern in generated_files:
        if "*" in file_pattern:
            # Handle wildcard patterns
            matches = list(Path(".").glob(file_pattern))
            if matches:
                for match in matches:
                    print(f"   ✅ {match}")
            else:
                print(f"   ⚠️ {file_pattern} (not found)")
        else:
            path = Path(file_pattern)
            if path.exists():
                if path.is_dir():
                    file_count = len(list(path.glob("*")))
                    print(f"   ✅ {file_pattern} ({file_count} files)")
                else:
                    size = path.stat().st_size
                    print(f"   ✅ {file_pattern} ({size} bytes)")
            else:
                print(f"   ⚠️ {file_pattern} (not found)")

    # Final Status
    print("\n🏆 SYSTEM STATUS")
    print("================")

    if success_rate >= 80:
        print("🎉 UNIFIED TERMINAL AUTOMATION SYSTEM: FULLY OPERATIONAL")
        print("✨ Ready for production use with multi-tool integration")
    elif success_rate >= 60:
        print("⚡ UNIFIED TERMINAL AUTOMATION SYSTEM: MOSTLY OPERATIONAL")
        print("🔧 Some features may need configuration")
    else:
        print("🚧 UNIFIED TERMINAL AUTOMATION SYSTEM: NEEDS ATTENTION")
        print("🔍 Check failed tests and system requirements")

    print("\n💡 NEXT STEPS:")
    print("   1. Run: python3 unified_cli.py warp recover")
    print("   2. Explore: python3 unified_cli.py plugins")
    print("   3. Integrate: Add your own tool plugins")
    print("   4. Automate: Use mise.toml tasks for GitOps workflow")

    return success_rate >= 80


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
