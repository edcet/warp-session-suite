#!/bin/bash
# Advanced Warp Session Recovery with AI Analysis
# Integrated from existing warp-recovery.sh with enhancements

set -euo pipefail

echo "🔄 Advanced Warp Session Recovery Starting..."

# Configuration
RECOVERY_DIR="warp-recovery-$(date +%Y%m%d-%H%M%S)"
WARP_DB="$HOME/Library/Application Support/dev.warp.Warp-Stable/warp.sqlite"
BACKUP_DB="$HOME/Library/Application Support/dev.warp.Warp-Stable/warp_backup.sqlite"

# Verify Warp database exists
if [[ ! -f "$WARP_DB" ]]; then
  echo "❌ Warp database not found at: $WARP_DB"
  echo "💡 Checking for backup database..."
  if [[ -f "$BACKUP_DB" ]]; then
    WARP_DB="$BACKUP_DB"
    echo "✅ Using backup database"
  else
    echo "❌ No database found. Exiting."
    exit 1
  fi
fi

# Create enhanced recovery structure
mkdir -p "$RECOVERY_DIR"/{data,obsidian,analysis,exports,ai-context}
cd "$RECOVERY_DIR"

echo "📊 Extracting comprehensive Warp session data..."

# Enhanced data extraction with session types integration
sqlite3 "$WARP_DB" <<EOF >data/comprehensive_export.json
.mode json
SELECT json_object(
    'metadata', json_object(
        'extraction_time', datetime('now'),
        'database_path', '$WARP_DB',
        'total_commands', (SELECT COUNT(*) FROM commands),
        'total_sessions', (SELECT COUNT(*) FROM sessions),
        'total_ai_queries', (SELECT COUNT(*) FROM ai_queries)
    ),
    'recent_commands', (
        SELECT json_group_array(json_object(
            'id', id,
            'command', command,
            'timestamp', start_ts,
            'completed', completed_ts,
            'exit_code', exit_code,
            'pwd', pwd,
            'git_branch', git_branch,
            'session_id', session_id,
            'shell', shell,
            'username', username,
            'hostname', hostname
        ))
        FROM commands 
        WHERE start_ts > datetime('now', '-7 days')
        ORDER BY start_ts DESC
        LIMIT 1000
    ),
    'ai_conversations', (
        SELECT json_group_array(json_object(
            'id', id,
            'conversation_id', conversation_id,
            'exchange_id', exchange_id,
            'timestamp', start_ts,
            'input', input,
            'working_directory', working_directory,
            'model_id', model_id,
            'output_status', output_status
        ))
        FROM ai_queries
        ORDER BY start_ts DESC
        LIMIT 50
    ),
    'terminal_sessions', (
        SELECT json_group_array(json_object(
            'id', id,
            'name', name,
            'created_at', created_at,
            'last_activity', last_activity,
            'status', status,
            'project_path', project_path,
            'metadata', metadata
        ))
        FROM sessions
        ORDER BY last_activity DESC
    ),
    'recent_blocks', (
        SELECT json_group_array(json_object(
            'id', id,
            'stylized_command', stylized_command,
            'stylized_output', stylized_output,
            'pwd', pwd,
            'git_branch', git_branch,
            'exit_code', exit_code,
            'start_ts', start_ts,
            'completed_ts', completed_ts
        ))
        FROM blocks
        WHERE start_ts > datetime('now', '-24 hours')
        ORDER BY start_ts DESC
        LIMIT 200
    )
) as comprehensive_export;
EOF

# Create advanced analysis script with Go types integration
cat >analysis/advanced_analyzer.py <<'PYTHON'
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

print("🤖 Starting advanced session analysis...")

# Load comprehensive data
with open('data/comprehensive_export.json', 'r') as f:
    data = json.loads(f.read())

# Extract metadata
metadata = data['metadata']
commands = data['recent_commands']
ai_conversations = data['ai_conversations']
sessions = data['terminal_sessions']
blocks = data['recent_blocks']

print(f"📈 Analysis scope:")
print(f"  - Commands: {len(commands)}")
print(f"  - AI Conversations: {len(ai_conversations)}")
print(f"  - Sessions: {len(sessions)}")
print(f"  - Blocks: {len(blocks)}")

# Advanced pattern analysis
command_patterns = defaultdict(list)
project_contexts = defaultdict(list)
ai_topics = defaultdict(list)

# Analyze command patterns
for cmd in commands:
    if not cmd['command']:
        continue
    
    # Extract base command
    base_cmd = cmd['command'].split()[0] if cmd['command'].split() else ''
    command_patterns[base_cmd].append(cmd)
    
    # Project context analysis
    if cmd['pwd']:
        project_contexts[cmd['pwd']].append(cmd)
    
    # Git branch context
    if cmd['git_branch']:
        command_patterns[f"git:{cmd['git_branch']}"].append(cmd)

# AI conversation analysis
for conv in ai_conversations:
    if conv['input']:
        # Extract topics using simple keyword analysis
        words = re.findall(r'\b\w+\b', conv['input'].lower())
        for word in words:
            if len(word) > 4:  # Filter out short words
                ai_topics[word].append(conv)

# Session pattern analysis
session_analysis = {
    'active_sessions': len([s for s in sessions if s['status'] == 'active']),
    'total_sessions': len(sessions),
    'project_sessions': len([s for s in sessions if s['project_path']]),
}

# Generate comprehensive markdown report
report = f"""# 🔍 Advanced Warp Session Analysis

Generated: {datetime.now().isoformat()}

## 📊 Executive Summary

- **Analysis Period**: Last 7 days
- **Total Commands Analyzed**: {len(commands)}
- **AI Interactions**: {len(ai_conversations)}
- **Active Sessions**: {session_analysis['active_sessions']}
- **Database**: {metadata['database_path']}

## 🎯 Command Pattern Analysis

### Top Command Categories
"""

# Top commands by frequency
top_commands = Counter([cmd['command'].split()[0] for cmd in commands if cmd['command'] and cmd['command'].split()])
for cmd, count in top_commands.most_common(15):
    report += f"- **{cmd}**: {count} executions\n"

report += "\n### Project Context Analysis\n\n"
for pwd, cmd_list in sorted(project_contexts.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    report += f"- **{pwd}**: {len(cmd_list)} commands\n"

report += "\n## 🤖 AI Interaction Patterns\n\n"
if ai_conversations:
    report += f"### Recent AI Topics\n"
    top_topics = Counter()
    for conv in ai_conversations:
        if conv['input']:
            words = re.findall(r'\b\w+\b', conv['input'].lower())
            for word in words:
                if len(word) > 4:
                    top_topics[word] += 1
    
    for topic, count in top_topics.most_common(10):
        report += f"- **{topic}**: {count} mentions\n"

report += "\n## 📈 Session Health Analysis\n\n"
report += f"- Active Sessions: {session_analysis['active_sessions']}\n"
report += f"- Total Sessions: {session_analysis['total_sessions']}\n"
report += f"- Project-based Sessions: {session_analysis['project_sessions']}\n"

# Error analysis
error_commands = [cmd for cmd in commands if cmd['exit_code'] and cmd['exit_code'] != 0]
report += f"\n### Error Analysis\n"
report += f"- Commands with errors: {len(error_commands)}\n"
report += f"- Success rate: {((len(commands) - len(error_commands)) / len(commands) * 100):.1f}%\n"

if error_commands:
    error_patterns = Counter([cmd['command'].split()[0] for cmd in error_commands if cmd['command'] and cmd['command'].split()])
    report += "\n#### Most Error-Prone Commands\n"
    for cmd, count in error_patterns.most_common(5):
        report += f"- **{cmd}**: {count} errors\n"

report += "\n## 🎮 Session Reconstruction Recommendations\n\n"
report += "Based on the analysis, here are the key session patterns to preserve:\n\n"

# Identify key workflows
workflows = defaultdict(list)
for pwd, cmd_list in project_contexts.items():
    if len(cmd_list) >= 3:  # Significant activity
        workflows[pwd] = cmd_list[-5:]  # Last 5 commands

for project, cmd_list in workflows.items():
    report += f"### {project}\n"
    for cmd in cmd_list:
        report += f"```bash\n{cmd['command']}\n```\n"
        if cmd['exit_code'] != 0:
            report += f"⚠️ Exit code: {cmd['exit_code']}\n"
        report += "\n"

# Save comprehensive analysis
with open('../obsidian/advanced_session_analysis.md', 'w') as f:
    f.write(report)

# Generate quick recovery scripts
recovery_scripts = """# 🔧 Session Recovery Scripts

## Quick Environment Recreation

```bash
# Navigate to key project directories
"""

for pwd in list(project_contexts.keys())[:5]:
    if pwd and Path(pwd).exists():
        recovery_scripts += f"cd {pwd}\n"
        # Add common commands for this directory
        common_cmds = Counter([cmd['command'] for cmd in project_contexts[pwd]])
        for cmd, _ in common_cmds.most_common(3):
            if cmd and not cmd.startswith('cd'):
                recovery_scripts += f"# {cmd}\n"
        recovery_scripts += "\n"

recovery_scripts += "```\n"

with open('../exports/recovery_commands.md', 'w') as f:
    f.write(recovery_scripts)

print("✅ Advanced analysis complete!")
print(f"📁 Generated files:")
print(f"  - obsidian/advanced_session_analysis.md")
print(f"  - exports/recovery_commands.md")
PYTHON

echo "🤖 Running advanced analysis..."
python analysis/advanced_analyzer.py

# Create AI context extraction for local models
echo "🧠 Extracting AI context for local models..."
cat >ai-context/conversation_context.jsonl <<'EOF'
EOF

# Extract AI conversations in JSONL format for model fine-tuning
sqlite3 "$WARP_DB" <<EOF >>ai-context/conversation_context.jsonl
.mode json
SELECT json_object(
    'timestamp', start_ts,
    'input', input,
    'working_directory', working_directory,
    'model_id', model_id,
    'conversation_id', conversation_id
) FROM ai_queries 
WHERE start_ts > datetime('now', '-30 days')
ORDER BY start_ts DESC;
EOF

# Create viewing and export utilities
cat >view_results.sh <<'VIEWER'
#!/bin/bash
echo "📚 Warp Session Recovery Results:"
echo ""
echo "1. 🔍 Advanced Analysis: obsidian/advanced_session_analysis.md"
echo "2. 🔧 Recovery Commands: exports/recovery_commands.md"
echo "3. 🤖 AI Context: ai-context/conversation_context.jsonl"
echo "4. 📊 Raw Data: data/comprehensive_export.json"
echo ""
echo "Choose viewing option:"
echo "[1] Advanced Analysis (glow)"
echo "[2] Recovery Commands"
echo "[3] Open in VS Code"
echo "[4] Export to parent directory"
read -r choice

case $choice in
    1) glow obsidian/advanced_session_analysis.md 2>/dev/null || cat obsidian/advanced_session_analysis.md ;;
    2) glow exports/recovery_commands.md 2>/dev/null || cat exports/recovery_commands.md ;;
    3) code . 2>/dev/null || echo "VS Code not available" ;;
    4) 
        cp -r obsidian exports ai-context ../
        echo "✅ Files exported to parent directory"
        ;;
    *) echo "Opening advanced analysis..."; cat obsidian/advanced_session_analysis.md ;;
esac
VIEWER
chmod +x view_results.sh

# Final summary with actionable insights
echo ""
echo "✅ Advanced Recovery Complete!"
echo ""
echo "📍 Location: $(pwd)"
echo "🎯 Quick Actions:"
echo "  - View Results: ./view_results.sh"
echo "  - Analysis Summary: cat obsidian/advanced_session_analysis.md | head -50"
echo "  - Recovery Scripts: cat exports/recovery_commands.md"
echo ""
echo "🔮 AI Integration Ready:"
echo "  - Context file: ai-context/conversation_context.jsonl"
echo "  - Total conversations extracted: $(wc -l <ai-context/conversation_context.jsonl)"
echo ""
echo "💡 Next Steps:"
echo "  1. Review the advanced analysis for patterns"
echo "  2. Execute recovery commands as needed"
echo "  3. Set up preventive session archiving"
echo "  4. Consider implementing automated backups"

echo ""
echo "🚀 Ready for next-generation session management!"
