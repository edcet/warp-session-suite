#!/usr/bin/env python3
"""Standalone test script for Warp session recovery."""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Optional

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Known Warp database locations (in order of preference)
WARP_DB_PATHS = [
    "~/Library/Application Support/dev.warp.Warp-Stable/warp.sqlite",
    "~/Library/Application Support/dev.warp.Warp/warp.sqlite",
    "~/Library/Application Support/dev.warp.Warp/stores/main.sqlite",
    "~/Library/Application Support/Warp/warp.sqlite",
]


def find_warp_database() -> Path:
    """Find the Warp SQLite database on the system."""
    for path_str in WARP_DB_PATHS:
        path = Path(path_str).expanduser().resolve()
        if path.exists():
            return path

    # For testing in container, use test database
    test_db = Path("test_data/warp_test.sqlite")
    if test_db.exists():
        return test_db

    raise FileNotFoundError(
        f"Could not find Warp database. Searched paths:\n"
        + "\n".join(f"  - {p}" for p in WARP_DB_PATHS)
        + f"\n\nMake sure Warp Terminal is installed and has been used."
    )


class WarpDB:
    """Direct SQLite connection to Warp's database."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path).expanduser().resolve()
        else:
            self.db_path = find_warp_database()

        if not self.db_path.exists():
            raise FileNotFoundError(f"Warp database not found at {self.db_path}")

        # Open read-only connection to avoid locking issues
        self.conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        self.conn.row_factory = sqlite3.Row  # Allow dict-like access

    def query(self, sql: str, params: tuple = ()):
        """Execute SQL query and return results."""
        try:
            if HAS_PANDAS:
                return pd.read_sql_query(sql, self.conn, params=params)
            else:
                cursor = self.conn.execute(sql, params)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"SQL Error: {e}")
            print(f"Query: {sql}")
            raise

    def list_tables(self) -> list[str]:
        """List all tables in the database."""
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        self.conn.close()


# SQL Queries for Warp
class WarpSQL:
    recent_commands = """
        SELECT
            c.id,
            c.command,
            datetime(c.start_ts) as started_at,
            datetime(c.completed_ts) as completed_at,
            c.exit_code,
            c.pwd as working_directory,
            c.git_branch,
            c.shell,
            c.username,
            c.hostname
        FROM commands c
        WHERE c.start_ts IS NOT NULL
        ORDER BY c.start_ts DESC
        LIMIT 20;
    """

    ai_conversations = """
        SELECT
            aq.id,
            aq.exchange_id,
            aq.conversation_id,
            datetime(aq.start_ts) as started_at,
            substr(aq.input, 1, 100) || '...' as input_preview,
            aq.working_directory,
            aq.model_id
        FROM ai_queries aq
        ORDER BY aq.start_ts DESC
        LIMIT 10;
    """

    project_analysis = """
        SELECT
            c.pwd as project_path,
            COUNT(*) as command_count,
            COUNT(DISTINCT c.git_branch) as branch_count,
            MIN(datetime(c.start_ts)) as first_activity,
            MAX(datetime(c.start_ts)) as last_activity
        FROM commands c
        WHERE c.pwd IS NOT NULL
          AND c.start_ts > datetime('now', '-7 days')
        GROUP BY c.pwd
        HAVING COUNT(*) >= 3
        ORDER BY command_count DESC
        LIMIT 10;
    """


def print_results(results, title: str):
    """Print query results in a readable format."""
    print(f"\n=== {title} ===")

    if HAS_PANDAS and hasattr(results, "empty"):
        if results.empty:
            print("No results found")
            return
        print(results.to_string(index=False, max_colwidth=50))
    elif isinstance(results, list):
        if not results:
            print("No results found")
            return
        for i, row in enumerate(results[:10]):  # Limit to 10 rows for display
            print(f"Row {i+1}:")
            for key, value in row.items():
                print(f"  {key}: {str(value)[:100]}")
            print()
    else:
        print(results)


def main():
    """Main CLI function."""
    print("🚀 Warp Session Recovery Tool")

    try:
        db = WarpDB()
        print(f"📊 Connected to database: {db.db_path}")

        # List tables
        tables = db.list_tables()
        print(f"\n📋 Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")

        # Test queries
        if "commands" in tables:
            results = db.query(WarpSQL.recent_commands)
            print_results(results, "Recent Commands")

        if "ai_queries" in tables:
            results = db.query(WarpSQL.ai_conversations)
            print_results(results, "AI Conversations")

        if "commands" in tables:
            results = db.query(WarpSQL.project_analysis)
            print_results(results, "Project Analysis")

        db.close()
        print("\n✅ Test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
