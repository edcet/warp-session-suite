"""Typer CLI for warp_queries exposing reusable analytics commands.

Example usage:

$ warps list          # list predefined SQL snippets
$ warps preview last_commands --limit 10
$ warps run pane_genealogy --open

The CLI leverages DuckDB for high-performance analytics on Warp's SQLite
session database.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .db import DuckDBConnector
from .sql_snippets import SQL

app = typer.Typer(add_completion=False)
console = Console()


def _connect(database: Optional[str]) -> DuckDBConnector:
    try:
        return DuckDBConnector(database)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def list() -> None:  # noqa: D401
    """List available SQL snippet names."""

    names = SQL.list_queries()
    table = Table(title="Available SQL snippets")
    table.add_column("Name", style="cyan")
    for name in names:
        table.add_row(name)
    console.print(table)


@app.command()
def preview(
    name: str = typer.Argument(..., help="Name of SQL snippet"),
    limit: int = typer.Option(20, help="Limit rows for preview"),
    db: Optional[str] = typer.Option(None, "--db", help="Path to Warp SQLite"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table|json"),
) -> None:
    """Preview results of a SQL snippet with row limit.

    The default *table* format pretty prints using Rich. Use *json* to emit newline
    separated JSON records suitable for piping into tools like `jq` or `fzf`.
    """
    if not hasattr(SQL, name):
        console.print(f"[red]Unknown snippet:[/red] {name}")
        raise typer.Exit(1)

    conn = _connect(db)
    sql = getattr(SQL, name)
    if "LIMIT" not in sql.upper():
        sql += f"\nLIMIT {limit}"
    df = conn.query(sql)

    if format == "json":
        import json

        for row in df.to_dict(orient="records"):
            # Ensure all values are JSON serialisable (e.g. pandas Timestamp -> str)
            serialised = {
                k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()
            }
            print(json.dumps(serialised, default=str))
    else:
        console.print(df)

    conn.close()


@app.command()
def run(
    name: str = typer.Argument(..., help="SQL snippet name"),
    db: Optional[str] = typer.Option(None, "--db", help="Path to Warp SQLite"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write results to CSV"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table|json"),
) -> None:
    """Run a SQL snippet and optionally save to CSV or emit JSON lines."""

    if not hasattr(SQL, name):
        console.print(f"[red]Unknown snippet:[/red] {name}")
        raise typer.Exit(1)

    conn = _connect(db)
    sql = getattr(SQL, name)
    df = conn.query(sql)

    if output:
        output = Path(output).with_suffix(".csv")
        df.to_csv(output, index=False)
        console.print(f"[green]Saved to {output}")
    else:
        if format == "json":
            import json

            for row in df.to_dict(orient="records"):
                serialised = {
                    k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()
                }
                print(json.dumps(serialised, default=str))
        else:
            console.print(df)

    conn.close()


@app.command("cli:install")
def cli_install() -> None:
    """Install warps CLI via pipx shim."""
    import shutil
    import subprocess

    if shutil.which("pipx") is None:
        console.print("[red]pipx is not installed. Please install pipx first.[/red]")
        raise typer.Exit(1)

    package = Path(__file__).resolve().parent.parent
    console.print(f"Installing {package} via pipx...")
    try:
        subprocess.run(["pipx", "install", str(package)], check=True)
    except subprocess.CalledProcessError as exc:
        console.print(f"[red]pipx failed:[/red] {exc}")
        raise typer.Exit(1)
    console.print("[green]warps CLI installed successfully![/green]")


if __name__ == "__main__":
    app()
