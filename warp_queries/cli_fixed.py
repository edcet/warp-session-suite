"""Working CLI for Warp session recovery and analysis."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from .db_fixed import WarpDB
from .sql_snippets_fixed import WarpSQL

def print_table(df, max_rows: int = 20):
    """Print DataFrame as a simple table."""
    if not HAS_PANDAS:
        print("pandas not available - showing raw data")
        return
        
    if len(df) == 0:
        print("No results found")
        return
    
    # Truncate long strings for display
    display_df = df.copy()
    for col in display_df.columns:
        if display_df[col].dtype == 'object':
            display_df[col] = display_df[col].astype(str).str[:60] + "..."
    
    print(display_df.head(max_rows).to_string(index=False))
    if len(df) > max_rows:
        print(f"\n... and {len(df) - max_rows} more rows")

def print_json(df):
    """Print DataFrame as JSON lines."""
    for _, row in df.iterrows():
        # Convert pandas types to JSON-serializable types
        row_dict = {}
        for k, v in row.items():
            if pd.isna(v):
                row_dict[k] = None
            elif hasattr(v, 'isoformat'):  # datetime
                row_dict[k] = v.isoformat()
            else:
                row_dict[k] = v
        print(json.dumps(row_dict))

def main():
    """Main CLI function."""
    if len(sys.argv) < 2:
        print("Usage: python -m warp_queries.cli_fixed <command> [options]")
        print("\nCommands:")
        print("  list              - List available queries")
        print("  query <name>      - Run a specific query")
        print("  tables            - List database tables")
        print("  info <table>      - Show table schema")
        print("  recent            - Show recent commands")
        print("  ai                - Show AI conversations")
        print("  projects          - Analyze project activity")
        print("  errors            - Show error analysis")
        return
    
    command = sys.argv[1]
    
    # Handle list command without database connection
    if command == "list":
        queries = WarpSQL.list_queries()
        print("Available queries:")
        for query in queries:
            print(f"  {query}")
        return
    
    # Database path handling
    db_path = None
    if "--db" in sys.argv:
        idx = sys.argv.index("--db")
        if idx + 1 < len(sys.argv):
            db_path = sys.argv[idx + 1]
    
    # For testing in container, use test database
    if db_path is None and Path("test_data/warp_test.sqlite").exists():
        db_path = "test_data/warp_test.sqlite"
        print(f"Using test database: {db_path}")
    
    try:
        with WarpDB(db_path) as db:
            if command == "tables":
                tables = db.list_tables()
                print("Database tables:")
                for table in tables:
                    print(f"  {table}")
            
            elif command == "info":
                if len(sys.argv) < 3:
                    print("Usage: info <table_name>")
                    return
                table_name = sys.argv[2]
                info = db.table_info(table_name)
                print(f"Schema for table '{table_name}':")
                for col in info:
                    print(f"  {col['name']}: {col['type']} {'(PRIMARY KEY)' if col['pk'] else ''}")
            
            elif command == "query":
                if len(sys.argv) < 3:
                    print("Usage: query <query_name>")
                    return
                query_name = sys.argv[2]
                if not hasattr(WarpSQL, query_name):
                    print(f"Unknown query: {query_name}")
                    return
                
                sql = getattr(WarpSQL, query_name)
                df = db.query(sql)
                
                if "--json" in sys.argv:
                    print_json(df)
                else:
                    print(f"Results for {query_name}:")
                    print_table(df)
            
            elif command == "recent":
                df = db.query(WarpSQL.recent_commands)
                print("Recent commands:")
                print_table(df)
            
            elif command == "ai":
                df = db.query(WarpSQL.ai_conversations)
                print("AI conversations:")
                print_table(df)
            
            elif command == "projects":
                df = db.query(WarpSQL.project_analysis)
                print("Project analysis:")
                print_table(df)
            
            elif command == "errors":
                df = db.query(WarpSQL.error_analysis)
                print("Error analysis:")
                print_table(df)
            
            else:
                print(f"Unknown command: {command}")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
