#!/usr/bin/env python3
"""
Convert sqlite-utils JSONL output to proper JSON schema format
"""
import json
import sys
from pathlib import Path

def convert_jsonl_to_json(jsonl_file, json_file):
    """Convert JSONL to properly formatted JSON"""
    tables = []
    
    with open(jsonl_file, 'r') as f:
        for line in f:
            if line.strip():
                tables.append(json.loads(line))
    
    schema_data = {
        "database_schema": {
            "tables": tables,
            "metadata": {
                "extraction_tool": "sqlite-utils",
                "format_version": "1.0",
                "total_tables": len(tables)
            }
        }
    }
    
    with open(json_file, 'w') as f:
        json.dump(schema_data, f, indent=2, sort_keys=True)
    
    print(f"✅ Converted {len(tables)} tables to JSON format")
    return schema_data

if __name__ == "__main__":
    jsonl_file = Path("docs/schema/raw/tables.jsonl")
    json_file = Path("docs/schema/raw/schema.json")
    
    if jsonl_file.exists():
        convert_jsonl_to_json(jsonl_file, json_file)
    else:
        print(f"❌ JSONL file not found: {jsonl_file}")
        sys.exit(1)
