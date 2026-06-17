import sqlite3
import os

DB_PATH = os.path.join("storage", "movies.db")


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            year TEXT,
            quality TEXT,
            url TEXT UNIQUE,
            imdb_id TEXT,
            rating TEXT,
            votes TEXT,
            file_size TEXT,
            sub_type TEXT,
            source TEXT,
            codec TEXT,
            release_group TEXT,
            last_modified TEXT,
            collection TEXT,
            is_series INTEGER DEFAULT 0,
            season TEXT,
            episode TEXT
        )
    """)

    _migrate_schema(conn, cur)

    conn.commit()
    conn.close()


def _migrate_schema(conn, cur):
    existing = [row[1] for row in cur.execute("PRAGMA table_info(movies)")]

    new_columns = {
        "imdb_id": "TEXT",
        "rating": "TEXT",
        "votes": "TEXT",
        "file_size": "TEXT",
        "sub_type": "TEXT",
        "source": "TEXT",
        "codec": "TEXT",
        "release_group": "TEXT",
        "last_modified": "TEXT",
        "collection": "TEXT",
        "is_series": "INTEGER DEFAULT 0",
        "season": "TEXT",
        "episode": "TEXT",
    }

    for col_name, col_type in new_columns.items():
        if col_name not in existing:
            try:
                cur.execute(f"ALTER TABLE movies ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass


def save_movie(conn, movie):

    if not movie:
        return

    if not movie.get("url"):
        return

    url = movie.get("url", "")

    # extra safety filter - archive parser passes video URLs directly
    is_archive = movie.get("imdb_id") is not None

    if not is_archive and not url.lower().endswith((".mkv", ".mp4", ".avi", ".webm", ".m4v")):
        return

    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT OR IGNORE INTO movies (
                title, year, quality, url, imdb_id, rating, votes,
                file_size, sub_type, source, codec, release_group,
                last_modified, collection, is_series, season, episode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            movie.get("title"),
            movie.get("year"),
            movie.get("quality") or movie.get("quality_label"),
            url,
            movie.get("imdb_id"),
            movie.get("rating"),
            movie.get("votes"),
            movie.get("file_size") or movie.get("file_size_str"),
            movie.get("sub_type"),
            movie.get("source"),
            movie.get("codec"),
            movie.get("group") or movie.get("release_group"),
            movie.get("last_modified"),
            movie.get("collection"),
            1 if movie.get("is_series") else 0,
            movie.get("season"),
            movie.get("episode"),
        ))

        conn.commit()

    except Exception as e:
        print(f"[DB ERROR] {e}")