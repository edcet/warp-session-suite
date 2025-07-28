#!/usr/bin/env python3
"""
Unified Terminal Automation System - Main CLI Interface
Entry point for all tool integrations and AI-powered automation.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("unified_cli")


class UnifiedCLI:
    """Main CLI interface for the Unified Terminal Automation System."""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.plugin_dir = self.base_dir / "plugins"
        self.registry_file = self.plugin_dir / "registry.json"

    def load_plugin_registry(self) -> Dict[str, Any]:
        """Load the plugin registry."""
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)
        return {"plugins": {}}

    def list_plugins(self) -> None:
        """List all available plugins."""
        registry = self.load_plugin_registry()

        print("🔌 Available Plugins:")
        print("=" * 50)

        for name, info in registry.get("plugins", {}).items():
            entry_path = self.base_dir / info.get("entry", "")
            status = "✅ Active" if entry_path.exists() else "❌ Missing"

            print(f"  {name:15} - {info.get('name', 'No description')}")
            print(f"  {'':15}   Status: {status}")
            print(f"  {'':15}   Capabilities: {', '.join(info.get('capabilities', []))}")
            print()

    def run_warp_command(self, args: List[str]) -> None:
        """Execute Warp-specific commands."""
        if not args or args[0] == "help":
            print("🔄 Warp Session Recovery Commands:")
            print("  recover [hours]     - Extract and create recovery script")
            print("  export [format]     - Export sessions (obsidian, json)")
            print("  backup             - Create session backup")
            print("  analyze            - Analyze session patterns")
            return

        command = args[0]

        if command == "recover":
            hours = int(args[1]) if len(args) > 1 else 24
            print(f"🔄 Running Warp session recovery for last {hours} hours...")

            # Use existing recovery tool with enhanced integration
            result = subprocess.run([sys.executable, "warp_session_recovery.py"], cwd=self.base_dir)

            if result.returncode == 0:
                print("✅ Warp session recovery completed successfully!")
            else:
                print("❌ Warp session recovery failed!")
                sys.exit(1)

        elif command == "export":
            export_format = args[1] if len(args) > 1 else "obsidian"
            print(f"📤 Exporting Warp sessions in {export_format} format...")
            self._export_warp_sessions(export_format)

        elif command == "backup":
            print("💾 Creating Warp session backup...")
            self._backup_warp_sessions()

        elif command == "analyze":
            print("📊 Analyzing Warp session patterns...")
            self._analyze_warp_patterns()

        else:
            print(f"❌ Unknown Warp command: {command}")
            sys.exit(1)

    def _export_warp_sessions(self, format_type: str) -> None:
        """Export Warp sessions in specified format."""
        try:
            from warp_session_recovery import WarpSessionRecovery

            recovery = WarpSessionRecovery()
            session_data = recovery.get_recent_session_state(24)

            if format_type == "obsidian":
                recovery.create_obsidian_export(session_data)
                print("✅ Obsidian export completed!")
            elif format_type == "json":
                output_file = f"warp_export_{session_data['extraction_time'][:10]}.json"
                with open(output_file, "w") as f:
                    json.dump(session_data, f, indent=2)
                print(f"✅ JSON export saved to {output_file}")
            else:
                print(f"❌ Unsupported export format: {format_type}")

        except Exception as e:
            logger.error(f"Export failed: {e}")
            print(f"❌ Export failed: {e}")

    def _backup_warp_sessions(self) -> None:
        """Create comprehensive Warp session backup."""
        try:
            from warp_session_recovery import WarpSessionRecovery

            recovery = WarpSessionRecovery()
            session_data = recovery.get_recent_session_state(168)  # 1 week

            backup_file = f"warp_backup_{session_data['extraction_time'][:10]}.json"
            with open(backup_file, "w") as f:
                json.dump(session_data, f, indent=2)

            print(f"✅ Warp backup created: {backup_file}")

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            print(f"❌ Backup failed: {e}")

    def _analyze_warp_patterns(self) -> None:
        """Analyze Warp usage patterns."""
        try:
            from warp_session_recovery import WarpSessionRecovery

            recovery = WarpSessionRecovery()
            session_data = recovery.get_recent_session_state(168)  # 1 week

            # Basic analytics
            commands = session_data.get("commands", [])
            projects = session_data.get("projects", [])

            print("📊 Warp Usage Analytics:")
            print(f"  Total Commands: {len(commands)}")
            print(f"  Active Projects: {len(projects)}")

            if commands:
                # Most used commands
                cmd_freq = {}
                for cmd in commands:
                    base_cmd = cmd.get("command", "").split()[0] if cmd.get("command") else ""
                    if base_cmd:
                        cmd_freq[base_cmd] = cmd_freq.get(base_cmd, 0) + 1

                print("\n🔥 Top Commands:")
                for cmd, count in sorted(cmd_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"    {cmd:20} {count:3} times")

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            print(f"❌ Analysis failed: {e}")

    def run_ai_command(self, args: List[str]) -> None:
        """Execute AI-powered automation commands."""
        if not args or args[0] == "help":
            print("🤖 AI-Powered Automation Commands:")
            print("  chat [query]        - Interactive AI chat")
            print("  generate-plugin     - Create new plugin with AI")
            print("  code-review        - AI code review of changes")
            print("  suggest-command    - Get command suggestions")
            return

        command = args[0]

        if command == "chat":
            query = " ".join(args[1:]) if len(args) > 1 else ""
            if query:
                subprocess.run(["tgpt", query])
            else:
                subprocess.run(["tgpt"])

        elif command == "generate-plugin":
            subprocess.run(["mise", "run", "ai:generate-plugin"])

        elif command == "code-review":
            subprocess.run(["mise", "run", "ai:code-review"])

        elif command == "suggest-command":
            query = " ".join(args[1:])
            if not query:
                query = input("💭 Describe what you want to do: ")

            print("🤖 Generating command suggestions...")
            subprocess.run(["tgpt", "--shell", query])

        else:
            print(f"❌ Unknown AI command: {command}")
            sys.exit(1)

    def run_system_command(self, args: List[str]) -> None:
        """Execute system management commands."""
        if not args or args[0] == "help":
            print("⚙️ System Management Commands:")
            print("  status             - System health check")
            print("  bootstrap          - Initialize system")
            print("  sync               - GitOps configuration sync")
            print("  backup             - Create system backup")
            return

        command = args[0]

        if command == "status":
            subprocess.run(["mise", "run", "system:health-check"])
        elif command == "bootstrap":
            subprocess.run(["mise", "run", "system:bootstrap"])
        elif command == "sync":
            subprocess.run(["mise", "run", "gitops:sync"])
        else:
            print(f"❌ Unknown system command: {command}")
            sys.exit(1)

    def main(self) -> None:
        """Main CLI entry point."""
        parser = argparse.ArgumentParser(
            description="Unified Terminal Automation System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  unified_cli.py warp recover 24          # Recover last 24 hours of Warp sessions
  unified_cli.py ai chat "help with git"  # AI-powered assistance
  unified_cli.py system status            # System health check
  unified_cli.py plugins                  # List available plugins
            """,
        )

        parser.add_argument(
            "command",
            nargs="?",
            default="help",
            help="Command to execute (warp, ai, system, plugins)",
        )
        parser.add_argument("args", nargs="*", help="Command arguments")
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

        args = parser.parse_args()

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Welcome message
        if args.command == "help":
            print("🚀 Unified Terminal Automation System")
            print("═" * 50)
            print("Available commands:")
            print("  warp      - Warp Terminal session management")
            print("  ai        - AI-powered automation and assistance")
            print("  system    - System management and configuration")
            print("  plugins   - Plugin management and development")
            print("")
            print("Use '<command> help' for command-specific help")
            return

        # Route commands
        if args.command == "warp":
            self.run_warp_command(args.args)
        elif args.command == "ai":
            self.run_ai_command(args.args)
        elif args.command == "system":
            self.run_system_command(args.args)
        elif args.command == "plugins":
            self.list_plugins()
        else:
            print(f"❌ Unknown command: {args.command}")
            print("Use 'unified_cli.py help' for available commands")
            sys.exit(1)


if __name__ == "__main__":
    cli = UnifiedCLI()
    cli.main()
