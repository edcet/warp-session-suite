#!/usr/bin/env python3
"""schema_diagrams.py
Generate ERD diagrams (PNG and SVG) and Mermaid markdown snippet from the
Warp SQLite schema JSON that was extracted earlier.

This script is the implementation of the `schema:diagrams` build step.

Usage (from repository root):
    python docs/schema/generate_diagrams.py

The script expects:
* docs/schema/raw/schema.json – produced by the previous extraction step
* `schemadiagram` – a CLI ( https://pypi.org/project/schemadiagram/ ) available
  on $PATH.  If the binary is missing the script exits with an explanation.

Artefacts are written to:
    docs/schema/img/erd.svg
    docs/schema/img/erd.png
    docs/schema/img/schema.mmd  (Mermaid markdown)

Those artefacts are referenced by MkDocs and other documentation tooling.
"""
from __future__ import annotations

import subprocess
import shutil
from pathlib import Path
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # project root
RAW_DIR = REPO_ROOT / "docs" / "schema" / "raw"
SCHEMA_JSON = RAW_DIR / "schema.json"
IMG_DIR = REPO_ROOT / "docs" / "schema" / "img"

# Desired output files
SVG_OUT = IMG_DIR / "erd.svg"
PNG_OUT = IMG_DIR / "erd.png"
MERMAID_OUT = IMG_DIR / "schema.mmd"


def run(cmd: list[str], description: str) -> None:
    """Helper executing a command while printing understandable status."""
    print(f"📡 Running {description} ...", flush=True)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"❌ Failed to {description}. See output above.")
    print(f"✅ {description} completed.")


def ensure_prerequisites() -> None:
    if not SCHEMA_JSON.exists():
        raise SystemExit(f"❌ Expected schema JSON at {SCHEMA_JSON} – run the extraction first.")
    if shutil.which("schemadiagram") is None:
        raise SystemExit(
            "❌ 'schemadiagram' CLI not found on $PATH. Install it with\n"
            "   pip install schemadiagram\n"
            "or ensure it is available inside your environment."
        )


def main() -> None:
    ensure_prerequisites()

    # Ensure output directory exists
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # ERD: SVG and PNG
    # ------------------------------------------------------------------
    run([
        "schemadiagram",
        "erd",
        str(SCHEMA_JSON),
        str(SVG_OUT),
        "--format",
        "svg",
    ], "generate SVG ERD")

    run([
        "schemadiagram",
        "erd",
        str(SCHEMA_JSON),
        str(PNG_OUT),
        "--format",
        "png",
    ], "generate PNG ERD")

    # ------------------------------------------------------------------
    # Mermaid
    # ------------------------------------------------------------------
    run([
        "schemadiagram",
        "mermaid",
        str(SCHEMA_JSON),
        "--output",
        str(MERMAID_OUT),
    ], "generate Mermaid markdown")

    print("\n🎉 All diagrams generated successfully in docs/schema/img/")


if __name__ == "__main__":
    main()

