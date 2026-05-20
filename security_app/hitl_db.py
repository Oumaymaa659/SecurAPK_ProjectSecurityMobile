import sqlite3
import os
from datetime import datetime

DB_PATH = "hitl_feedback.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT,
            finding_id TEXT,
            original_verdict TEXT,
            corrected_verdict TEXT,
            justification TEXT,
            timestamp TEXT,
            file_name TEXT,
            finding_type TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_feedback(scan_id, finding_id, original_verdict, corrected_verdict, justification, file_name, finding_type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO feedback (scan_id, finding_id, original_verdict, corrected_verdict, justification, timestamp, file_name, finding_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (scan_id, finding_id, original_verdict, corrected_verdict, justification, datetime.now().isoformat(), file_name, finding_type))
    conn.commit()
    conn.close()

def get_recent_feedback(limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM feedback ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_feedback_by_type(finding_type, limit=3):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT corrected_verdict, justification FROM feedback WHERE finding_type = ? ORDER BY timestamp DESC LIMIT ?", (finding_type, limit))
    rows = c.fetchall()
    conn.close()
    return rows