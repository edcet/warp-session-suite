"""Fixed DB connector that finds Warp's SQLite file correctly."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Optional
import pandas as pd

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
    
    # If none found, search more broadly
    lib_support = Path.home() / "Library" / "Application Support"
    if lib_support.exists():
        for sqlite_file in lib_support.rglob("*.sqlite"):
            if "warp" in sqlite_file.name.lower() or "warp" in str(sqlite_file.parent).lower():
                return sqlite_file
    
    raise FileNotFoundError(
        f"Could not find Warp database. Searched paths:\n" +
        "\n".join(f"  - {p}" for p in WARP_DB_PATHS) +
        f"\n\nMake sure Warp Terminal is installed and has been used."
    )

class WarpDB:
    """Direct SQLite connection to Warp's database."""
    
    def __init__(self, db_path: Optional[str | os.PathLike[str]] = None):
        if db_path:
            self.db_path = Path(db_path).expanduser().resolve()
        else:
            self.db_path = find_warp_database()
            
        if not self.db_path.exists():
            raise FileNotFoundError(f"Warp database not found at {self.db_path}")
        
        # Open read-only connection to avoid locking issues
        self.conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        self.conn.row_factory = sqlite3.Row  # Allow dict-like access
    
    def query(self, sql: str, params: tuple = ()) -> pd.DataFrame:
        """Execute SQL query and return results as pandas DataFrame."""
        try:
            return pd.read_sql_query(sql, self.conn, params=params)
        except Exception as e:
            print(f"SQL Error: {e}")
            print(f"Query: {sql}")
            raise
    
    def execute(self, sql: str, params: tuple = ()) -> list[dict]:
        """Execute SQL and return raw results as list of dicts."""
        cursor = self.conn.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def list_tables(self) -> list[str]:
        """List all tables in the database."""
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def table_info(self, table_name: str) -> list[dict]:
        """Get column information for a table."""
        cursor = self.conn.execute(f"PRAGMA table_info({table_name})")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
