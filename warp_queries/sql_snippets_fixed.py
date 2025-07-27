"""Fixed SQL snippets that work with actual Warp Terminal schema."""

class WarpSQL:
    """Collection of working SQL snippets against Warp's real SQLite schema.
    
    These queries work with the actual Warp database structure as of 2024.
    """

    # Recent commands with full context - using actual 'commands' table
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
            c.hostname,
            c.session_id
        FROM commands c
        WHERE c.start_ts IS NOT NULL
        ORDER BY c.start_ts DESC
        LIMIT 1000;
    """

    # Recent command blocks with stylized output - using actual 'blocks' table
    recent_blocks = """
        SELECT
            b.id,
            b.stylized_command,
            b.stylized_output,
            b.pwd,
            b.git_branch,
            b.exit_code,
            datetime(b.start_ts) as started_at,
            datetime(b.completed_ts) as completed_at,
            b.shell,
            b.user,
            b.host,
            b.ai_metadata
        FROM blocks b
        WHERE b.start_ts IS NOT NULL
        ORDER BY b.start_ts DESC
        LIMIT 500;
    """

    # AI conversations - using actual 'ai_queries' table
    ai_conversations = """
        SELECT
            aq.id,
            aq.exchange_id,
            aq.conversation_id,
            datetime(aq.start_ts) as started_at,
            aq.input,
            aq.working_directory,
            aq.output_status,
            aq.model_id,
            aq.planning_model_id,
            aq.coding_model_id
        FROM ai_queries aq
        ORDER BY aq.start_ts DESC
        LIMIT 100;
    """

    # AI blocks (responses) - using actual 'ai_blocks' table
    ai_responses = """
        SELECT
            ab.id,
            ab.exchange_id,
            ab.output,
            ab.is_hidden,
            ab.is_passive_code_gen_block,
            aq.input as original_query,
            aq.working_directory,
            aq.model_id
        FROM ai_blocks ab
        JOIN ai_queries aq ON ab.exchange_id = aq.exchange_id
        ORDER BY ab.id DESC
        LIMIT 100;
    """

    # Window and tab structure
    window_tabs = """
        SELECT
            w.id as window_id,
            w.active_tab_index,
            w.window_width,
            w.window_height,
            w.quake_mode,
            t.id as tab_id,
            t.custom_title,
            t.color
        FROM windows w
        LEFT JOIN tabs t ON t.window_id = w.id
        ORDER BY w.id, t.id;
    """

    # Pane structure - shows how terminal panes are organized
    pane_structure = """
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
        ORDER BY pn.tab_id, pn.id;
    """

    # Session reconstruction data - everything needed to rebuild a session
    session_reconstruction = """
        SELECT
            'command' as type,
            c.id,
            c.command,
            c.pwd,
            c.git_branch,
            c.exit_code,
            datetime(c.start_ts) as timestamp,
            c.session_id
        FROM commands c
        WHERE c.start_ts > datetime('now', '-24 hours')
        
        UNION ALL
        
        SELECT
            'ai_query' as type,
            aq.id,
            aq.input as command,
            aq.working_directory as pwd,
            NULL as git_branch,
            CASE WHEN aq.output_status = 'success' THEN 0 ELSE 1 END as exit_code,
            datetime(aq.start_ts) as timestamp,
            NULL as session_id
        FROM ai_queries aq
        WHERE aq.start_ts > datetime('now', '-24 hours')
        
        ORDER BY timestamp DESC;
    """

    # Projects analysis - based on working directories
    project_analysis = """
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
          AND c.start_ts > datetime('now', '-7 days')
        GROUP BY c.pwd
        HAVING COUNT(*) >= 3
        ORDER BY command_count DESC, last_activity DESC;
    """

    # Error analysis
    error_analysis = """
        SELECT
            CASE 
                WHEN c.command LIKE '% %' THEN substr(c.command, 1, instr(c.command, ' ') - 1)
                ELSE c.command
            END as base_command,
            COUNT(*) as total_executions,
            SUM(CASE WHEN c.exit_code != 0 THEN 1 ELSE 0 END) as failures,
            ROUND(100.0 * SUM(CASE WHEN c.exit_code != 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as failure_rate,
            GROUP_CONCAT(DISTINCT c.exit_code) as exit_codes
        FROM commands c
        WHERE c.command IS NOT NULL
          AND c.start_ts > datetime('now', '-7 days')
        GROUP BY base_command
        HAVING COUNT(*) >= 3
        ORDER BY failure_rate DESC, total_executions DESC;
    """

    @classmethod
    def list_queries(cls) -> list[str]:
        """Return list of available SQL snippet names."""
        return [k for k in cls.__dict__.keys() 
                if not k.startswith("__") and k != "list_queries" and isinstance(getattr(cls, k), str)]
