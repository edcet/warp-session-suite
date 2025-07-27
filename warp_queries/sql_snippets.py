"""Opinionated SQL snippets for Warp Terminal session analytics."""

from __future__ import annotations

class SQL:
    """Collection of pre-defined SQL snippets against Warp's SQLite schema.

    These queries are tested with DuckDB instances attached to the original
    `~/Library/Application Support/dev.warp.Warp/stores/main.sqlite` database.
    They are composed as multi-line strings for readability and can be
    imported as constants or accessed via `SQL.<name>` attributes.
    """

    # Last executed commands including timestamp and directory
    last_commands = (
        """
        SELECT
            p.command_text         AS command,
            s.start_time           AS started_at,
            s.end_time             AS ended_at,
            w.working_directory,
            s.exit_code           AS status
        FROM pane_commands p
        JOIN sessions s  ON s.id = p.session_id
        JOIN windows  w  ON w.id = s.window_id
        ORDER BY s.start_time DESC
        LIMIT 100;
        """
    )

    # AI conversation summary (assumes messages table)
    ai_convo_summary = (
        """
        SELECT
            conversation_id,
            GROUP_CONCAT(content, '\n') AS transcript,
            MIN(created_at)             AS started_at,
            MAX(created_at)             AS ended_at
        FROM ai_messages
        GROUP BY conversation_id
        ORDER BY ended_at DESC
        LIMIT 50;
        """
    )

    # Pane genealogy: relationship of panes to windows and tabs
    pane_genealogy = (
        """
        SELECT
            p.id               AS pane_id,
            t.id               AS tab_id,
            w.id               AS window_id,
            p.title            AS pane_title,
            t.title            AS tab_title,
            w.title            AS window_title,
            p.created_at       AS pane_created,
            p.closed_at        AS pane_closed
        FROM panes p
        JOIN tabs   t ON t.id = p.tab_id
        JOIN windows w ON w.id = t.window_id
        ORDER BY pane_created DESC;
        """
    )

    # Sessions started within the last 24 hours with basic metadata
    last_24h_sessions = (
        """
        SELECT
            s.id                AS session_id,
            w.title             AS window_title,
            MIN(s.start_time)   AS started_at,
            MAX(s.end_time)     AS ended_at,
            COUNT(p.id)         AS pane_count
        FROM sessions s
        JOIN windows w ON w.id = s.window_id
        LEFT JOIN panes p  ON p.session_id = s.id
        WHERE s.start_time >= datetime('now', '-1 day')
        GROUP BY s.id, w.title
        ORDER BY started_at DESC;
        """
    )

    @classmethod
    def list_queries(cls) -> list[str]:
        """Return list of available SQL snippet names."""
        return [k for k in cls.__dict__.keys() if not k.startswith("__") and k != "list_queries"]

