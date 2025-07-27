CREATE TABLE __diesel_schema_migrations (
       version VARCHAR(50) PRIMARY KEY NOT NULL,
       run_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE windows (
  id INTEGER PRIMARY KEY NOT NULL,
  active_tab_index INTEGER NOT NULL CHECK (active_tab_index >= 0),
  window_width FLOAT CHECK (window_width >= 0),
  window_height FLOAT CHECK (window_height >= 0),
  origin_x FLOAT,
  origin_y FLOAT, quake_mode BOOLEAN NOT NULL DEFAULT FALSE, universal_search_width FLOAT CHECK (universal_search_width >= 0), warp_ai_width FLOAT CHECK (warp_ai_width >= 0), voltron_width FLOAT CHECK (voltron_width >= 0), warp_drive_index_width FLOAT CHECK (warp_drive_index_width >= 0), fullscreen_state INTEGER NOT NULL DEFAULT 0,
  CONSTRAINT Bound_integrity CHECK (
    COALESCE(window_width, window_height, origin_x, origin_y) IS NOT NULL
    OR COALESCE(window_width, window_height, origin_x, origin_y) IS NULL
  )
);
CREATE TABLE tabs (
  id INTEGER PRIMARY KEY NOT NULL,
  window_id INTEGER NOT NULL, custom_title TEXT, color TEXT,
  FOREIGN KEY(window_id) REFERENCES windows(id)
);
CREATE TABLE pane_nodes (
  id INTEGER PRIMARY KEY NOT NULL,
  tab_id INTEGER NOT NULL REFERENCES tabs(id),
  parent_pane_node_id INTEGER REFERENCES pane_nodes(id),
  flex FLOAT,
  is_leaf BOOLEAN NOT NULL,
  CONSTRAINT root_or_has_parent CHECK (
	parent_pane_node_id IS NULL AND flex IS NULL
	OR parent_pane_node_id IS NOT NULL AND flex IS NOT NULL
  )
);
CREATE TABLE pane_branches (
  id INTEGER PRIMARY KEY NOT NULL,
  pane_node_id INTEGER NOT NULL UNIQUE REFERENCES pane_nodes(id),
  horizontal BOOLEAN NOT NULL
);
CREATE TABLE blocks (
    id INTEGER PRIMARY KEY,
    pane_leaf_uuid BLOB NOT NULL,
    stylized_command BLOB NOT NULL,
    stylized_output BLOB NOT NULL,
    pwd TEXT,
    git_branch TEXT,
    virtual_env TEXT,
    conda_env TEXT,
    exit_code INTEGER NOT NULL,
    did_execute BOOLEAN NOT NULL
, completed_ts DATETIME, start_ts DATETIME, ps1 TEXT, honor_ps1 BOOLEAN NOT NULL DEFAULT FALSE, shell TEXT, user TEXT, host TEXT, is_background BOOLEAN NOT NULL DEFAULT false, rprompt TEXT, prompt_snapshot TEXT, block_id TEXT NOT NULL DEFAULT "", ai_metadata TEXT, is_local BOOLEAN);
CREATE TABLE app (
    id INTEGER PRIMARY KEY,
    active_window_id INTEGER REFERENCES windows(id)
);
CREATE TABLE users (
   id INTEGER NOT NULL PRIMARY KEY,
   firebase_uid  TEXT NOT NULL UNIQUE
);
CREATE TABLE workflows (
    id INTEGER NOT NULL PRIMARY KEY,
    -- Diesel does not let you specify JSON as data type
    data TEXT NOT NULL);
CREATE TABLE notebooks (
  id INTEGER NOT NULL PRIMARY KEY,
  title TEXT,
  data TEXT);
CREATE TABLE folders (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    is_open BOOLEAN NOT NULL
, is_warp_pack BOOLEAN NOT NULL DEFAULT FALSE);
CREATE TABLE "object_metadata" (
    id INTEGER NOT NULL PRIMARY KEY,
    is_pending BOOLEAN NOT NULL,
    object_type TEXT NOT NULL,
    revision_ts INTEGER,
    server_id TEXT,
    client_id TEXT,
    shareable_object_id INTEGER NOT NULL,
    author_id INTEGER,
    retry_count INTEGER NOT NULL,
    metadata_last_updated_ts BIGINTEGER,
    trashed_ts BIGINTEGER,
    folder_id TEXT
, is_welcome_object BOOLEAN NOT NULL DEFAULT false, creator_uid TEXT, last_editor_uid TEXT, current_editor TEXT);
CREATE TABLE commands (
    id INTEGER NOT NULL PRIMARY KEY,
    command TEXT NOT NULL,
    exit_code INTEGER,
    start_ts DATETIME,
    completed_ts DATETIME,
    pwd TEXT,
    shell TEXT,
    username TEXT,
    hostname TEXT,
    session_id BIGINTEGER,
    git_branch TEXT,
    cloud_workflow_id TEXT
, workflow_command TEXT);
CREATE TABLE "pane_leaves" (
    pane_node_id INTEGER NOT NULL UNIQUE REFERENCES pane_nodes(id),
    -- This does not have a CHECK constraint because, when we add new kinds of panes in the future,
    -- it's difficult to update the constraint.
    kind TEXT NOT NULL,
    is_focused BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (pane_node_id, kind)
);
CREATE TABLE terminal_panes (
    id INTEGER PRIMARY KEY NOT NULL,
    kind TEXT NOT NULL DEFAULT 'terminal' CHECK (kind = 'terminal'),

    uuid BLOB NOT NULL UNIQUE,
    cwd TEXT,
    is_active BOOLEAN NOT NULL DEFAULT FALSE, shell_launch_data TEXT, input_config TEXT,

    FOREIGN KEY (id, kind) REFERENCES "pane_leaves"(pane_node_id, kind)
);
CREATE TABLE notebook_panes (
  id INTEGER PRIMARY KEY NOT NULL,
  kind TEXT NOT NULL DEFAULT 'notebook' CHECK (kind = 'notebook'),

  -- The sync ID of the notebook. This may be null if the notebook has not yet been saved.
  notebook_id TEXT, local_path BLOB,
  
  FOREIGN KEY (id, kind) REFERENCES pane_leaves (pane_node_id, kind)
);
CREATE TABLE user_profiles (
    firebase_uid TEXT NOT NULL PRIMARY KEY,
    photo_url TEXT NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT
);
CREATE TABLE cloud_objects_refreshes (
  id INTEGER PRIMARY KEY NOT NULL, time_of_next_refresh DATETIME NOT NULL);
CREATE TABLE generic_string_objects (
    id INTEGER NOT NULL PRIMARY KEY,
    data TEXT NOT NULL
);
CREATE TABLE object_actions (
  id INTEGER PRIMARY KEY NOT NULL,
  hashed_object_id TEXT NOT NULL,
  timestamp DATETIME,
  -- An enum here would be overly restrictive for future action types.
  action TEXT NOT NULL,
  data TEXT,
  count INTEGER,
  oldest_timestamp DATETIME,
  latest_timestamp DATETIME,
  pending BOOLEAN
, processed_at_timestamp DATETIME);
CREATE TABLE server_experiments (
    experiment TEXT PRIMARY KEY NOT NULL
);
CREATE TABLE env_var_collection_panes (
  id INTEGER PRIMARY KEY NOT NULL,
  kind TEXT NOT NULL DEFAULT 'env_var_collection' CHECK (kind = 'env_var_collection'),

  -- The sync ID of the EVC. This may be null if the EVC has not yet been saved.
  env_var_collection_id TEXT,
  
  FOREIGN KEY (id, kind) REFERENCES pane_leaves (pane_node_id, kind)
);
CREATE TABLE code_panes (
  id INTEGER PRIMARY KEY NOT NULL,
  kind TEXT NOT NULL DEFAULT 'code' CHECK (kind = 'code'),

  -- The sync ID of the notebook. This may be null if the notebook has not yet been saved.
  local_path BLOB,

  FOREIGN KEY (id, kind) REFERENCES pane_leaves (pane_node_id, kind)
);
CREATE TABLE workflow_panes (
  id INTEGER PRIMARY KEY NOT NULL,
  kind TEXT NOT NULL DEFAULT 'workflow' CHECK (kind = 'workflow'),

  -- The sync ID of the EVC. This may be null if the EVC has not yet been saved.
  workflow_id TEXT,
  
  FOREIGN KEY (id, kind) REFERENCES pane_leaves (pane_node_id, kind)
);
CREATE TABLE "ai_queries" (
  id INTEGER PRIMARY KEY NOT NULL,
  exchange_id TEXT NOT NULL,
  conversation_id TEXT NOT NULL,
  start_ts DATETIME NOT NULL,
  -- FOREIGN KEY REFERENCES pane_leaves(uuid) but we don't mark it as a foreign key because it causes problems with cascading deletes.
  input TEXT NOT NULL,
  working_directory TEXT
, output_status TEXT NOT NULL, model_id TEXT NOT NULL DEFAULT '', planning_model_id TEXT NOT NULL DEFAULT '', coding_model_id TEXT NOT NULL DEFAULT '');
CREATE TABLE ai_blocks (
    id INTEGER PRIMARY KEY NOT NULL,
    exchange_id TEXT NOT NULL,
    -- Would be marked FOREIGN KEY REFERENCES pane_leaves(uuid) but we don't because we can't enforce it properly when handling pane removal.
    pane_leaf_uuid BLOB NOT NULL,
    output TEXT NOT NULL, is_hidden BOOLEAN NOT NULL DEFAULT FALSE, is_passive_code_gen_block BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY(exchange_id) REFERENCES "ai_queries"(exchange_id)
);
CREATE UNIQUE INDEX ux_ai_queries_exchange_id ON ai_queries(exchange_id);
CREATE UNIQUE INDEX ux_ai_blocks_exchange_id ON ai_blocks(exchange_id);
CREATE TABLE current_user_information (
    email TEXT PRIMARY KEY NOT NULL
);
CREATE TABLE "object_permissions" (
  id INTEGER NOT NULL PRIMARY KEY,
  object_metadata_id INTEGER NOT NULL REFERENCES object_metadata(id) ON DELETE CASCADE,
  subject_type TEXT NOT NULL,
  subject_id TEXT,
  subject_uid TEXT NOT NULL,
  permissions_last_updated_at BIGINTEGER,
  object_guests BLOB
, anyone_with_link_access_level TEXT, anyone_with_link_source BLOB);
CREATE TABLE "teams" (
  id integer NOT NULL PRIMARY KEY,
  name TEXT NOT NULL,
  server_uid TEXT NOT NULL UNIQUE
);
CREATE TABLE workspaces (
    id integer NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    server_uid TEXT NOT NULL UNIQUE
, is_selected BOOLEAN NOT NULL DEFAULT FALSE);
CREATE TABLE workspace_teams (
    id integer NOT NULL PRIMARY KEY,
    workspace_server_uid TEXT NOT NULL UNIQUE,
    team_server_uid TEXT NOT NULL UNIQUE,
    FOREIGN KEY (workspace_server_uid) REFERENCES workspaces (server_uid),
    FOREIGN KEY (team_server_uid) REFERENCES teams (server_uid)
);
CREATE TABLE settings_panes (
  id INTEGER PRIMARY KEY NOT NULL,
  kind TEXT NOT NULL DEFAULT 'settings' CHECK (kind = 'settings'),

  current_page TEXT NOT NULL DEFAULT 'Account',

  FOREIGN KEY (id, kind) REFERENCES pane_leaves (pane_node_id, kind)
);
CREATE TABLE ai_memory_panes (
  id INTEGER PRIMARY KEY NOT NULL,
  kind TEXT NOT NULL DEFAULT 'ai_memory' CHECK (kind = 'ai_memory'),

  FOREIGN KEY (id, kind) REFERENCES pane_leaves (pane_node_id, kind)
);
CREATE TABLE mcp_server_panes (
  id INTEGER PRIMARY KEY NOT NULL,
  kind TEXT NOT NULL DEFAULT 'mcp_server' CHECK (kind = 'mcp_server'),

  FOREIGN KEY (id, kind) REFERENCES pane_leaves (pane_node_id, kind)
);
CREATE TABLE last_ai_conversations (
     id INTEGER PRIMARY KEY NOT NULL,
     conversation_id TEXT NOT NULL,
     exchanges TEXT NOT NULL,
     phase TEXT NOT NULL,
     has_dispatched_plan BOOLEAN NOT NULL,
     pane_leaf_uuid BLOB NOT NULL
 );
CREATE TABLE codebase_index_metadata (
    repo_path TEXT NOT NULL PRIMARY KEY,
    navigated_ts DATETIME,
    modified_ts DATETIME,
    queried_ts DATETIME
);
CREATE TABLE mcp_environment_variables (
    mcp_server_uuid BLOB PRIMARY KEY NOT NULL,
    environment_variables TEXT NOT NULL
);
CREATE TABLE agent_conversations (
    id INTEGER PRIMARY KEY NOT NULL,
    conversation_id TEXT NOT NULL,
    active_task_id TEXT,
    conversation_data TEXT NOT NULL,
    last_modified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER update_last_modified_at_for_agent_conversations AFTER
UPDATE ON agent_conversations FOR EACH ROW WHEN NEW.last_modified_at IS OLD.last_modified_at BEGIN
UPDATE agent_conversations
SET
    last_modified_at = CURRENT_TIMESTAMP
WHERE
    id = OLD.id;

END;
CREATE UNIQUE INDEX ux_agent_conversations_conversation_id ON agent_conversations (conversation_id);
CREATE TABLE agent_tasks (
    id INTEGER PRIMARY KEY NOT NULL,
    conversation_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    task BLOB NOT NULL,
    last_modified_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES agent_conversations (conversation_id)
);
CREATE TRIGGER update_last_modified_at_for_agent_tasks AFTER
UPDATE ON agent_tasks FOR EACH ROW WHEN NEW.last_modified_at IS OLD.last_modified_at BEGIN
UPDATE agent_tasks
SET
    last_modified_at = CURRENT_TIMESTAMP
WHERE
    id = OLD.id;

END;
CREATE UNIQUE INDEX ux_agent_tasks_task_id ON agent_tasks (task_id);
CREATE TABLE active_mcp_servers (
    id INTEGER PRIMARY KEY NOT NULL,
    mcp_server_uuid TEXT NOT NULL,
    UNIQUE(mcp_server_uuid)
);
CREATE TABLE team_settings (
    id INTEGER PRIMARY KEY NOT NULL,
    team_id INTEGER NOT NULL UNIQUE,
    settings_json TEXT NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams (id)
);
