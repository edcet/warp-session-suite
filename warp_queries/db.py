"""DB connector that attaches DuckDB to Warp's SQLite file for analytics."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import duckdb
from rich import print

DEFAULT_WARP_DB = (
    Path.home()
    / "Library"
    / "Application Support"
    / "dev.warp.Warp"
    / "stores"
    / "main.sqlite"
)


def _expand_db_path(db_path: Optional[str | os.PathLike[str]] = None) -> Path:
    if db_path is None:
        return DEFAULT_WARP_DB
    return Path(os.path.expanduser(db_path)).resolve()


class DuckDBConnector:
    """Lightweight helper to create DuckDB connection bound to the Warp SQLite file."""

    def __init__(self, db_path: Optional[str | os.PathLike[str]] = None):
        self.sqlite_path = _expand_db_path(db_path)
        if not self.sqlite_path.exists():
            raise FileNotFoundError(f"Warp SQLite file not found at {self.sqlite_path}")

        # The in-memory DuckDB instance will attach the SQLite database virtually.
        self.con = duckdb.connect()
        self.con.execute(
            "ATTACH DATABASE ? AS warp (TYPE sqlite);", [str(self.sqlite_path)]
        )
        # Set search path so tables can be referenced directly
        self.con.execute("SET search_path='warp';")

    def query(self, sql: str, **params):
        """Run SQL and return a DuckDB Relation (can call .df(), .arrow(), etc.)."""
        if params:
            return self.con.execute(sql, params).fetchdf()
        return self.con.execute(sql).fetchdf()

    def list_tables(self):
        return self.con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='warp';"
        ).fetchall()

    def close(self):
        self.con.close()

