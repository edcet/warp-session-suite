# Environment, Flags & Paths Guide

This chapter walks you through all important environment variables, command-line flags, and filesystem paths used by **Warp Session Suite**.

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `WARP_DB` | Path to Warp's SQLite database (used by `schema:extract`) | `$HOME/Library/Application Support/dev.warp.Warp-Stable/warp.sqlite` |
| `MISE_DATA_DIR` | Data directory for [mise](https://github.com/jdx/mise) task runner | `~/.local/share/mise` |

Add any of these variables to your shell profile (e.g. `~/.zshrc`) or export them ad-hoc before running tasks.

```bash
export WARP_DB="$HOME/Library/Application Support/dev.warp.Warp-Stable/warp.sqlite"
```

## CLI Flags

The repository defines several _tasks_ via **mise**. Most tasks don’t expose flags directly, but you can pass flags to the underlying commands. Examples:

```bash
# Regenerate schema with verbose output
mise run schema:extract -- --verbose

# Serve documentation on a different port
mise run docs:serve -- -a 0.0.0.0:9000
```

## Important Paths

| Path | Description |
|------|-------------|
| `docs/` | Source markdown for the documentation site |
| `docs/schema/raw/` | Auto-generated raw schema artefacts (SQL/JSON/YAML) |
| `docs/overrides/` | MkDocs-Material overrides (macros, templates, etc.) |
| `site/` | _Generated_ static site (ignored in git) |

---

Need something that isn’t covered? Open an issue or start a discussion!
