#!/usr/bin/env python3
"""
Warp Terminal Plugin for Unified Terminal Automation System
Integrates with existing warp_session_recovery.py functionality
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path to import existing warp functionality
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

try:
    from plugins.core.session.base_plugin import BasePlugin
    from warp_session_recovery import WarpSessionRecovery
except ImportError as e:
    print(f"Import error: {e}")

    # Fallback minimal implementation
    class BasePlugin:
        def __init__(self, name, version, config):
            self.name = name
            self.version = version
            self.config = config


class WarpPlugin(BasePlugin):
    """Warp Terminal integration plugin with enhanced session recovery."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("warp", "1.0.0", config or {})
        self.capabilities = ["session_recovery", "database_access", "ai_integration"]
        self.recovery_instance = None

    def initialize(self) -> bool:
        """Initialize Warp plugin."""
        try:
            self.recovery_instance = WarpSessionRecovery()
            return True
        except Exception as e:
            print(f"Failed to initialize Warp plugin: {e}")
            return False

    def get_session_state(self, hours: int = 24) -> Dict[str, Any]:
        """Extract comprehensive session state with security hardening."""
        if not self.recovery_instance:
            raise RuntimeError("Plugin not initialized")

        # Use existing WarpSessionRecovery functionality
        session_data = self.recovery_instance.get_recent_session_state(hours)

        # Add plugin metadata
        session_data.update(
            {
                "plugin_name": self.name,
                "plugin_version": self.version,
                "capabilities": self.capabilities,
            }
        )

        return session_data

    def create_recovery_script(
        self, session_data: Dict, output_name: str = "warp_recovery.sh"
    ) -> str:
        """Generate recovery script with secure file handling."""
        if not self.recovery_instance:
            raise RuntimeError("Plugin not initialized")

        # Use existing recovery script functionality (compatible API)
        return self.recovery_instance.create_recovery_script(session_data, output_name)

    def export_to_obsidian(self, session_data: Dict) -> str:
        """Export sessions to Obsidian format."""
        if not self.recovery_instance:
            raise RuntimeError("Plugin not initialized")

        return self.recovery_instance.create_obsidian_export(session_data)

    def analyze_patterns(self, session_data: Dict) -> Dict[str, Any]:
        """Analyze session patterns and usage."""
        commands = session_data.get("commands", [])
        projects = session_data.get("projects", [])

        # Command frequency analysis
        cmd_freq = {}
        for cmd in commands:
            base_cmd = cmd.get("command", "").split()[0] if cmd.get("command") else ""
            if base_cmd:
                cmd_freq[base_cmd] = cmd_freq.get(base_cmd, 0) + 1

        # Project activity analysis
        project_activity = {}
        for proj in projects:
            proj_path = proj.get("project_path", "Unknown")
            project_activity[proj_path] = proj.get("command_count", 0)

        return {
            "command_frequency": dict(
                sorted(cmd_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            ),
            "project_activity": dict(
                sorted(project_activity.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "total_commands": len(commands),
            "total_projects": len(projects),
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        if self.recovery_instance and hasattr(self.recovery_instance, "conn"):
            self.recovery_instance.conn.close()


# Plugin factory function
def create_plugin(config: Dict[str, Any] = None) -> WarpPlugin:
    """Create and return a Warp plugin instance."""
    return WarpPlugin(config)


# CLI interface for standalone usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Warp Plugin CLI")
    parser.add_argument(
        "command", choices=["test", "recover", "analyze"], help="Command to execute"
    )
    parser.add_argument(
        "--hours", type=int, default=24, help="Hours of history to process"
    )

    args = parser.parse_args()

    try:
        plugin = create_plugin()

        if plugin.initialize():
            print("✅ Warp plugin initialized successfully")

            if args.command == "test":
                session_data = plugin.get_session_state(args.hours)
                print(f"📊 Extracted {len(session_data.get('commands', []))} commands")
                print(f"📊 Extracted {len(session_data.get('projects', []))} projects")

            elif args.command == "recover":
                session_data = plugin.get_session_state(args.hours)
                script_path = plugin.create_recovery_script(session_data)
                print(f"📝 Recovery script created: {script_path}")

            elif args.command == "analyze":
                session_data = plugin.get_session_state(args.hours)
                analysis = plugin.analyze_patterns(session_data)
                print("📊 Warp Usage Analysis:")
                print(f"  Total Commands: {analysis['total_commands']}")
                print(f"  Total Projects: {analysis['total_projects']}")
                print("\n🔥 Top Commands:")
                for cmd, count in list(analysis["command_frequency"].items())[:10]:
                    print(f"    {cmd:20} {count:3} times")

            plugin.cleanup()
            print("✅ All operations completed successfully!")
        else:
            print("❌ Plugin initialization failed")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Plugin operation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
