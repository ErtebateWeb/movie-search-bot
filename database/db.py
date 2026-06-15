import sqlite3
import os

DB_PATH = os.path.join("storage", "movies.db")


def get_connection():
    return sqlite3.connect(DB_PATH)

def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,
            year TEXT,

            quality TEXT,
            url TEXT,

            source TEXT,

            imdb_id TEXT,

            content_type TEXT,

            season INTEGER,
            episode INTEGER,

            language TEXT
        )
    """)

    conn.commit()
    conn.close()