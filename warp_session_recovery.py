#!/usr/bin/env python3
"""
Warp Session Recovery Tool - Unified Terminal Automation System Integration
Enhanced for modular plugin architecture and GitOps workflow.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class WarpSessionRecovery:
    """Warp-native session recovery that preserves blocks, AI context, and workflows."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = self._find_warp_database(db_path)
        self.conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        self.conn.row_factory = sqlite3.Row

    def _find_warp_database(self, db_path: Optional[str] = None) -> Path:
        """Find Warp's SQLite database."""
        if db_path:
            # Validate and sanitize the database path
            path = Path(db_path).expanduser().resolve()
            # Ensure the path doesn't contain traversal attempts
            if ".." in str(path) or not str(path).startswith(str(Path.home())):
                raise ValueError("Invalid database path - potential path traversal detected")
            return path

        # Real Warp paths
        paths = [
            "~/Library/Application Support/dev.warp.Warp-Stable/warp.sqlite",
            "~/Library/Application Support/dev.warp.Warp/warp.sqlite",
            "~/Library/Application Support/dev.warp.Warp/stores/main.sqlite",
            "~/Library/Application Support/Warp/warp.sqlite",
        ]

        for path_str in paths:
            path = Path(path_str).expanduser().resolve()
            if path.exists():
                return path

        # Fallback to test database for development
        test_db = Path("test_data/warp_test.sqlite")
        if test_db.exists():
            return test_db

        raise FileNotFoundError("Warp database not found")

    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results as list of dicts."""
        cursor = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_recent_session_state(self, hours: int = 24) -> Dict:
        """Extract comprehensive session state from the last N hours."""
        print(f"🔍 Extracting session state from last {hours} hours...")

        # Get recent commands with full context
        commands = self.query(
            """
            SELECT 
                c.id,
                c.command,
                c.pwd as working_directory,
                c.git_branch,
                c.exit_code,
                datetime(c.start_ts) as started_at,
                datetime(c.completed_ts) as completed_at,
                c.shell,
                c.username,
                c.hostname,
                c.session_id
            FROM commands c 
            WHERE c.start_ts > datetime('now', ? || ' hours')
            ORDER BY c.start_ts DESC
        """,
            (f"-{hours}",),
        )

        # Get command blocks with outputs
        blocks = self.query(
            """
            SELECT 
                b.id,
                b.stylized_command as command,
                b.stylized_output as output,
                b.pwd as working_directory,
                b.git_branch,
                b.exit_code,
                datetime(b.start_ts) as started_at,
                datetime(b.completed_ts) as completed_at,
                b.ai_metadata
            FROM blocks b 
            WHERE b.start_ts > datetime('now', ? || ' hours')
            ORDER BY b.start_ts DESC
        """,
            (f"-{hours}",),
        )

        # Get AI conversations
        ai_conversations = self.query(
            """
            SELECT 
                aq.id,
                aq.exchange_id,
                aq.conversation_id,
                datetime(aq.start_ts) as started_at,
                aq.input,
                aq.working_directory,
                aq.model_id,
                aq.output_status,
                ab.output as ai_response
            FROM ai_queries aq
            LEFT JOIN ai_blocks ab ON ab.exchange_id = aq.exchange_id
            WHERE aq.start_ts > datetime('now', ? || ' hours')
            ORDER BY aq.start_ts DESC
        """,
            (f"-{hours}",),
        )

        # Get window and tab structure
        windows = self.query(
            """
            SELECT 
                w.id as window_id,
                w.active_tab_index,
                w.window_width,
                w.window_height,
                w.quake_mode,
                t.id as tab_id,
                t.custom_title as tab_title,
                t.color as tab_color
            FROM windows w
            LEFT JOIN tabs t ON t.window_id = w.id
            ORDER BY w.id, t.id
        """
        )

        # Get pane structure
        panes = self.query(
            """
            SELECT 
                pn.id as node_id,
                pn.tab_id,
                pn.parent_pane_node_id,
                pn.is_leaf,
                pl.kind as pane_type,
                pl.is_focused,
                tp.uuid as terminal_uuid,
                tp.cwd as current_directory,
                tp.is_active
            FROM pane_nodes pn
            LEFT JOIN pane_leaves pl ON pl.pane_node_id = pn.id
            LEFT JOIN terminal_panes tp ON tp.id = pn.id AND pl.kind = 'terminal'
            ORDER BY pn.tab_id, pn.id
        """
        )

        # Analyze projects
        projects = self.query(
            """
            SELECT 
                c.pwd as project_path,
                COUNT(*) as command_count,
                COUNT(DISTINCT c.git_branch) as branch_count,
                MIN(datetime(c.start_ts)) as first_activity,
                MAX(datetime(c.start_ts)) as last_activity,
                GROUP_CONCAT(DISTINCT c.git_branch) as branches,
                AVG(CASE WHEN c.exit_code = 0 THEN 1.0 ELSE 0.0 END) as success_rate
            FROM commands c 
            WHERE c.pwd IS NOT NULL 
              AND c.start_ts > datetime('now', ? || ' hours')
            GROUP BY c.pwd
            HAVING COUNT(*) >= 1
            ORDER BY command_count DESC, last_activity DESC
        """,
            (f"-{hours}",),
        )

        return {
            "extraction_time": datetime.now().isoformat(),
            "database_path": str(self.db_path),
            "time_range_hours": hours,
            "commands": commands,
            "blocks": blocks,
            "ai_conversations": ai_conversations,
            "windows": windows,
            "panes": panes,
            "projects": projects,
            "stats": {
                "total_commands": len(commands),
                "total_blocks": len(blocks),
                "total_ai_conversations": len(ai_conversations),
                "total_windows": len(set(w["window_id"] for w in windows if w["window_id"])),
                "total_projects": len(projects),
            },
        }

    def create_recovery_script(self, session_data: Dict, output_file: str = "warp_recovery.sh"):
        """Generate a shell script to recreate the session environment."""
        print(f"📝 Creating recovery script: {output_file}")

        script_lines = [
            "#!/bin/bash",
            "# Warp Session Recovery Script",
            f"# Generated: {session_data['extraction_time']}",
            f"# From database: {session_data['database_path']}",
            "",
            "echo '🚀 Starting Warp session recovery...'",
            "",
        ]

        # Add project directory recreation
        for project in session_data["projects"]:
            if project["project_path"] and project["project_path"] != "/Users/test":
                script_lines.extend(
                    [
                        f"echo '📁 Setting up project: {project['project_path']}'",
                        f"cd '{project['project_path']}' 2>/dev/null || echo 'Warning: Directory not found'",
                        "",
                    ]
                )

                # Add git branch checkout if applicable
                if project["branches"] and project["branches"] != "None":
                    branches = project["branches"].split(",")
                    if len(branches) == 1 and branches[0]:
                        script_lines.extend(
                            [
                                f"git checkout {branches[0]} 2>/dev/null || echo 'Warning: Branch {branches[0]} not found'",
                                "",
                            ]
                        )

        # Add key commands for context
        script_lines.extend(["echo '📋 Key commands from your session:'", ""])

        for cmd in session_data["commands"][:10]:  # Last 10 commands
            if cmd["working_directory"]:
                script_lines.append(f"# {cmd['started_at']} in {cmd['working_directory']}")
            script_lines.append(f"# {cmd['command']}")
            if cmd["exit_code"] != 0:
                script_lines.append(f"# ❌ Exit code: {cmd['exit_code']}")
            script_lines.append("")

        # Add AI conversation context
        if session_data["ai_conversations"]:
            script_lines.extend(["echo '🤖 AI conversation context:'", ""])
            for conv in session_data["ai_conversations"][:5]:  # Top 5 conversations
                script_lines.extend(
                    [
                        f"# {conv['started_at']} - {conv['model_id']}",
                        f"# Q: {conv['input'][:80]}{'...' if len(conv['input']) > 80 else ''}",
                        "",
                    ]
                )

        script_lines.extend(
            [
                "echo '✅ Recovery context loaded!'",
                "echo 'You can now continue your work where you left off.'",
            ]
        )

        # Secure the output file path to prevent path traversal
        safe_output_file = os.path.join(os.getcwd(), os.path.basename(output_file))
        with open(safe_output_file, "w") as f:
            f.write("\n".join(script_lines))

        # Make executable
        Path(safe_output_file).chmod(0o755)
        print(f"✅ Recovery script created: {safe_output_file}")

    def create_obsidian_export(self, session_data: Dict, output_dir: str = "obsidian_export"):
        """Create Obsidian-compatible markdown files."""
        # Secure the output directory path to prevent path traversal
        safe_output_dir = os.path.join(os.getcwd(), os.path.basename(output_dir))
        output_path = Path(safe_output_dir)
        output_path.mkdir(exist_ok=True)

        print(f"📝 Creating Obsidian export in: {output_path}")

        # Main session note
        session_note = [
            f"# Warp Session Recovery - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"**Database**: `{session_data['database_path']}`",
            f"**Time Range**: Last {session_data['time_range_hours']} hours",
            f"**Extracted**: {session_data['extraction_time']}",
            "",
        ]

        # Stats summary
        stats = session_data["stats"]
        session_note.extend(
            [
                "## 📊 Session Stats",
                "",
                f"- **Commands**: {stats['total_commands']}",
                f"- **Blocks**: {stats['total_blocks']}",
                f"- **AI Conversations**: {stats['total_ai_conversations']}",
                f"- **Windows**: {stats['total_windows']}",
                f"- **Projects**: {stats['total_projects']}",
                "",
            ]
        )

        # Recent commands
        if session_data["commands"]:
            session_note.extend(
                [
                    "## 📋 Recent Commands",
                    "",
                ]
            )
            for cmd in session_data["commands"][:15]:
                session_note.extend(
                    [
                        f"### {cmd['started_at']}",
                        f"**Directory**: `{cmd['working_directory'] or 'Unknown'}`",
                        f"**Branch**: `{cmd['git_branch'] or 'None'}`",
                        "",
                        "```bash",
                        cmd["command"],
                        "```",
                        "",
                        f"Exit code: {'✅ 0' if cmd['exit_code'] == 0 else f'❌ {cmd['exit_code']}'}",
                        "",
                    ]
                )

        # AI conversations
        if session_data["ai_conversations"]:
            session_note.extend(
                [
                    "## 🤖 AI Conversations",
                    "",
                ]
            )
            for conv in session_data["ai_conversations"]:
                session_note.extend(
                    [
                        f"### {conv['started_at']} - {conv['model_id']}",
                        f"**Directory**: `{conv['working_directory'] or 'Unknown'}`",
                        "",
                        "**Query**:",
                        f"> {conv['input']}",
                        "",
                    ]
                )
                if conv["ai_response"]:
                    session_note.extend(
                        [
                            "**Response**:",
                            f"```",
                            conv["ai_response"][:500]
                            + ("..." if len(conv["ai_response"]) > 500 else ""),
                            f"```",
                            "",
                        ]
                    )

        # Projects
        if session_data["projects"]:
            session_note.extend(
                [
                    "## 📁 Project Activity",
                    "",
                ]
            )
            for project in session_data["projects"]:
                # Secure path handling to prevent path traversal
                safe_project_name = os.path.basename(os.path.normpath(project["project_path"]))
                session_note.extend(
                    [
                        f"### [[{safe_project_name}]]",
                        f"**Path**: `{project['project_path']}`",
                        f"**Commands**: {project['command_count']}",
                        f"**Branches**: {project['branches'] or 'None'}",
                        f"**Success Rate**: {project['success_rate']:.1%}",
                        f"**Activity**: {project['first_activity']} → {project['last_activity']}",
                        "",
                    ]
                )

        # Write main session file
        with open(output_path / "warp_session.md", "w") as f:
            f.write("\n".join(session_note))

        print(f"✅ Obsidian export created in: {output_path}")

    def close(self):
        self.conn.close()


def main():
    """Main CLI interface."""
    print("🚀 Warp Session Recovery Tool - WORKING VERSION")
    print("Extracts Warp-specific state: blocks, AI conversations, workflows")
    print()

    try:
        # Initialize recovery tool
        recovery = WarpSessionRecovery()
        print(f"📊 Connected to: {recovery.db_path}")

        # Extract session state
        session_data = recovery.get_recent_session_state(hours=24)

        # Display summary
        stats = session_data["stats"]
        print(
            f"""
📈 Session Summary:
   Commands: {stats['total_commands']}
   Blocks: {stats['total_blocks']}
   AI Conversations: {stats['total_ai_conversations']}
   Windows: {stats['total_windows']}
   Projects: {stats['total_projects']}
        """
        )

        # Create recovery outputs
        recovery.create_recovery_script(session_data)
        recovery.create_obsidian_export(session_data)

        # Save raw data
        with open("warp_session_backup.json", "w") as f:
            json.dump(session_data, f, indent=2, default=str)
        print("✅ Raw session data saved: warp_session_backup.json")

        recovery.close()

        print(
            """
🎯 Recovery files created:
   - warp_recovery.sh (executable recovery script)
   - obsidian_export/ (Obsidian-compatible notes)
   - warp_session_backup.json (raw data)

💡 Next steps:
   1. Review the recovery script
   2. Import obsidian_export/ into your Obsidian vault
   3. Run ./warp_recovery.sh to restore context
        """
        )

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
