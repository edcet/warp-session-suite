#!/usr/bin/env python3
"""Unified session manager for cross-tool coordination."""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class SessionManager:
    """Manages unified sessions across multiple terminal tools."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "unified_sessions.db")
        self.logger = logging.getLogger("session_manager")
        self._init_database()
    
    def _init_database(self):
        """Initialize unified session database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS unified_sessions (
                id INTEGER PRIMARY KEY,
                session_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tools_data TEXT,
                metadata TEXT
            )
        """)
        self.conn.commit()
    
    def create_unified_session(self, tools_data: Dict[str, Any]) -> str:
        """Create a new unified session combining data from multiple tools."""
        session_id = f"unified_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.conn.execute("""
            INSERT INTO unified_sessions (session_id, tools_data, metadata)
            VALUES (?, ?, ?)
        """, (
            session_id,
            json.dumps(tools_data),
            json.dumps({"created_by": "unified_automation_system"})
        ))
        self.conn.commit()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a unified session."""
        cursor = self.conn.execute("""
            SELECT * FROM unified_sessions WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'session_id': row['session_id'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'tools_data': json.loads(row['tools_data']),
                'metadata': json.loads(row['metadata'])
            }
        return None
    
    def update_session(self, session_id: str, tools_data: Dict[str, Any]) -> bool:
        """Update an existing unified session."""
        try:
            self.conn.execute("""
                UPDATE unified_sessions 
                SET tools_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (json.dumps(tools_data), session_id))
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to update session {session_id}: {e}")
            return False
    
    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent unified sessions."""
        cursor = self.conn.execute("""
            SELECT session_id, created_at, updated_at 
            FROM unified_sessions 
            ORDER BY updated_at DESC 
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def cleanup(self):
        """Clean up database resources."""
        if hasattr(self, 'conn'):
            self.conn.close()
