#!/bin/bash
# Obsidian-optimized session extraction with graph relationships

set -euo pipefail

OBSIDIAN_VAULT="${1:-$HOME/obsidian-vault}"
WARP_DB="$HOME/Library/Application Support/dev.warp.Warp-Stable/warp.sqlite"
OUTPUT_DIR="$OBSIDIAN_VAULT/warp-sessions"

echo "📝 Extracting Warp sessions for Obsidian vault: $OBSIDIAN_VAULT"

# Create obsidian structure
mkdir -p "$OUTPUT_DIR"/{daily,projects,ai-conversations,command-patterns}

# Daily session notes
echo "📅 Creating daily session notes..."
TODAY=$(date +%Y-%m-%d)
sqlite3 "$WARP_DB" <<EOF >"$OUTPUT_DIR/daily/$TODAY.md"
.mode list
.separator " "
SELECT '# Daily Session: $TODAY' as title
UNION ALL
SELECT '' as spacer
UNION ALL
SELECT '## Commands Executed' as section
UNION ALL
SELECT '' as spacer
UNION ALL
SELECT 
    '- **' || substr(start_ts, 12, 8) || '** $(' || 
    CASE 
        WHEN length(command) > 60 THEN substr(command, 1, 60) || '...'
        ELSE command 
    END || ')' ||
    CASE 
        WHEN exit_code != 0 THEN ' ❌ (' || exit_code || ')'
        ELSE ' ✅'
    END ||
    CASE 
        WHEN pwd IS NOT NULL THEN ' in [[' || 
            CASE 
                WHEN pwd LIKE '%/%' THEN substr(pwd, length(pwd) - instr(reverse(pwd), '/') + 2)
                ELSE pwd
            END || ']]'
        ELSE ''
    END
FROM commands 
WHERE date(start_ts) = '$TODAY'
ORDER BY start_ts DESC;
EOF

# Project-based extraction
echo "📁 Creating project-based session notes..."
sqlite3 "$WARP_DB" <<EOF | while IFS='|' read -r project count; do
.mode list
.separator "|"
SELECT DISTINCT 
    CASE 
        WHEN pwd IS NULL THEN 'unknown'
        WHEN pwd LIKE '%/%' THEN substr(pwd, length(pwd) - instr(reverse(pwd), '/') + 2)
        ELSE pwd
    END as project,
    COUNT(*) as cmd_count
FROM commands 
WHERE start_ts > datetime('now', '-7 days')
  AND pwd IS NOT NULL
GROUP BY project
HAVING COUNT(*) >= 5
ORDER BY COUNT(*) DESC
LIMIT 10;
EOF
  if [[ -n "$project" && "$project" != "unknown" ]]; then
    echo "  Creating note for project: $project ($count commands)"

    # Create project note with backlinks
    cat >"$OUTPUT_DIR/projects/${project}.md" <<PROJECTMD
# Project: $project

**Command Activity**: $count commands (last 7 days)

## Recent Commands

PROJECTMD

    # Add recent commands for this project
    sqlite3 "$WARP_DB" <<PROJECTSQL >>"$OUTPUT_DIR/projects/${project}.md"
.mode list
SELECT 
    '### ' || date(start_ts) || ' - ' || substr(start_ts, 12, 8) || '\n' ||
    '$()$(bash\n' || command || '\n)$()\n' ||
    CASE 
        WHEN exit_code != 0 THEN '❌ Exit code: ' || exit_code || '\n'
        ELSE '✅ Success\n'
    END || '\n'
FROM commands 
WHERE pwd LIKE '%$project%'
  AND start_ts > datetime('now', '-7 days')
ORDER BY start_ts DESC
LIMIT 15;
PROJECTSQL
  fi
done

# AI conversation extraction with relationships
echo "🤖 Extracting AI conversations..."
sqlite3 "$WARP_DB" <<EOF >"$OUTPUT_DIR/ai-conversations/recent-conversations.md"
.mode list
SELECT 
    '# Recent AI Conversations\n\n' ||
    'Generated: ' || datetime('now') || '\n\n' ||
    '## Conversations\n\n'
UNION ALL
SELECT 
    '### ' || datetime(start_ts) || '\n' ||
    '**Model**: ' || model_id || '\n' ||
    '**Directory**: [[' || 
    CASE 
        WHEN working_directory IS NOT NULL AND working_directory LIKE '%/%' 
        THEN substr(working_directory, length(working_directory) - instr(reverse(working_directory), '/') + 2)
        ELSE COALESCE(working_directory, 'unknown')
    END || ']]\n\n' ||
    '$()$(\n' || 
    CASE 
        WHEN length(input) > 200 THEN substr(input, 1, 200) || '...'
        ELSE input
    END || '\n)$()\n\n' ||
    '---\n\n'
FROM ai_queries 
WHERE start_ts > datetime('now', '-7 days')
ORDER BY start_ts DESC
LIMIT 20;
EOF

# Command pattern analysis
echo "📊 Creating command pattern analysis..."
sqlite3 "$WARP_DB" <<EOF >"$OUTPUT_DIR/command-patterns/pattern-analysis.md"
.mode list
SELECT 
    '# Command Pattern Analysis\n\n' ||
    'Generated: ' || datetime('now') || '\n\n' ||
    '## Top Commands (Last 7 Days)\n\n'
UNION ALL
SELECT 
    '- **' || 
    CASE 
        WHEN instr(command, ' ') > 0 THEN substr(command, 1, instr(command, ' ') - 1)
        ELSE command
    END || '**: ' || COUNT(*) || ' executions\n'
FROM commands 
WHERE start_ts > datetime('now', '-7 days')
  AND command IS NOT NULL
  AND length(command) > 0
GROUP BY 
    CASE 
        WHEN instr(command, ' ') > 0 THEN substr(command, 1, instr(command, ' ') - 1)
        ELSE command
    END
ORDER BY COUNT(*) DESC
LIMIT 20;
EOF

# Create index file with graph relationships
cat >"$OUTPUT_DIR/index.md" <<INDEXMD
# Warp Session Index

## 📅 Daily Sessions
- [[$(date +%Y-%m-%d)]] (Today)

## 📁 Active Projects
INDEXMD

# Add project links
for project_file in "$OUTPUT_DIR/projects/"*.md; do
  if [[ -f "$project_file" ]]; then
    project_name=$(basename "$project_file" .md)
    echo "- [[$project_name]]" >>"$OUTPUT_DIR/index.md"
  fi
done

cat >>"$OUTPUT_DIR/index.md" <<INDEXMD2

## 🤖 AI Interactions
- [[recent-conversations]]

## 📊 Analysis
- [[pattern-analysis]]

## 🔗 Related
- [[Warp Terminal Setup]]
- [[Development Workflows]]
- [[Command Reference]]

---

*Generated automatically from Warp Terminal session data*
INDEXMD2

echo ""
echo "✅ Obsidian extraction complete!"
echo ""
echo "📍 Vault Location: $OBSIDIAN_VAULT"
echo "📁 Session Data: $OUTPUT_DIR"
echo "🎯 Start with: $OUTPUT_DIR/index.md"
echo ""
echo "💡 Obsidian Features Enabled:"
echo "  - [[Backlinks]] for project relationships"
echo "  - Daily note integration"
echo "  - Command pattern analysis"
echo "  - AI conversation tracking"
echo ""
echo "🔄 To update: Run this script daily or set up automation"
