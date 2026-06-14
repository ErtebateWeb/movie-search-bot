import sqlite3
import os

DB_PATH = os.path.join("storage", "movies.db")


# Create database connection
def get_connection():
    return sqlite3.connect(DB_PATH)


# Initialize database schema
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            year TEXT,
            quality TEXT,
            url TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()