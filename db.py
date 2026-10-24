import sqlite3
from pathlib import Path

DB_PATH = Path("data/qr.db")


def get_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS vcards (
                id TEXT PRIMARY KEY,
                naam TEXT NOT NULL,
                vcf_data TEXT NOT NULL,
                foto_b64 TEXT,
                aangemaakt_op TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)
