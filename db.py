# db.py
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "botdata.sqlite"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            user_id INTEGER PRIMARY KEY,
            count INTEGER DEFAULT 0,
            last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            muted_until TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_warning_count(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT count FROM warnings WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def add_warning(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT count FROM warnings WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        new_count = row[0] + 1
        cur.execute("UPDATE warnings SET count = ?, last_reset = CURRENT_TIMESTAMP WHERE user_id = ?", (new_count, user_id))
    else:
        new_count = 1
        cur.execute("INSERT INTO warnings (user_id, count) VALUES (?, ?)", (user_id, new_count))
    conn.commit()
    conn.close()
    return new_count

def remove_warning(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT count FROM warnings WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        new_count = max(row[0] - 1, 0)
        cur.execute("UPDATE warnings SET count = ? WHERE user_id = ?", (new_count, user_id))
        conn.commit()
    else:
        new_count = 0
    conn.close()
    return new_count

def reset_warnings(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM warnings WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def set_muted(user_id: int, hours: int = 24):
    until = datetime.utcnow() + timedelta(hours=hours)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE warnings SET muted_until = ? WHERE user_id = ?", (until.isoformat(), user_id))
    conn.commit()
    conn.close()

def is_muted(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT muted_until FROM warnings WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row or not row[0]:
        return False
    return datetime.fromisoformat(row[0]) > datetime.utcnow()
