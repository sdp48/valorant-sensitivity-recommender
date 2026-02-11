import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "requests.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dpi INTEGER,
            aim_style TEXT,
            goal TEXT,
            pad TEXT,
            mid_sens REAL,
            mid_edpi REAL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_request(dpi, aim_style, goal, pad, mid_sens, mid_edpi, created_at):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO requests
        (dpi, aim_style, goal, pad, mid_sens, mid_edpi, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (dpi, aim_style, goal, pad, mid_sens, mid_edpi, created_at))
    conn.commit()
    conn.close()

def fetch_recent(limit: int = 20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, dpi, aim_style, goal, pad, mid_sens, mid_edpi, created_at
        FROM requests
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()

    cols = ["id", "dpi", "aim_style", "goal", "pad", "mid_sens", "mid_edpi", "created_at"]
    return [dict(zip(cols, r)) for r in rows]