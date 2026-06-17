import sqlite3
import os
from collections import defaultdict

DB_PATH = os.path.join("storage", "movies.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def normalize_title(title: str) -> str:
    return (
        title.lower()
        .replace(".", " ")
        .replace("_", " ")
        .replace("%20", " ")
        .strip()
    )


def search_movies(query: str, limit: int = 100):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM movies
        WHERE title LIKE ?
        ORDER BY
            CASE WHEN rating != '' THEN 1 ELSE 2 END,
            CAST(REPLACE(REPLACE(rating, ',', ''), ' ', '0') AS REAL) DESC
        LIMIT ?
    """, (f"%{query}%", limit))

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def group_movies(rows):
    grouped = {}

    for r in rows:
        key = normalize_title(r.get("title", ""))

        if key not in grouped:
            grouped[key] = {
                "title": r.get("title"),
                "year": r.get("year"),
                "imdb_id": r.get("imdb_id"),
                "rating": r.get("rating"),
                "votes": r.get("votes"),
                "versions": [],
            }

        grouped[key]["versions"].append({
            "quality": r.get("quality"),
            "url": r.get("url"),
            "file_size": r.get("file_size"),
            "sub_type": r.get("sub_type"),
            "source": r.get("source"),
            "codec": r.get("codec"),
            "release_group": r.get("release_group"),
            "season": r.get("season"),
            "episode": r.get("episode"),
        })

    return grouped


def search_and_group(query: str, limit: int = 100):
    rows = search_movies(query, limit)
    return group_movies(rows)


def print_results(grouped):
    if not grouped:
        print("\nNo results found")
        return

    print(f"\nFound {len(grouped)} movies:\n")

    for i, (key, data) in enumerate(grouped.items(), 1):
        rating_str = f" ⭐ {data['rating']}" if data.get("rating") else ""
        print(f"{i}. {data['title']} ({data['year']}){rating_str}")

        for v in data["versions"]:
            size_str = f" [{v['file_size']}]" if v.get("file_size") else ""
            sub_str = f" ({v['sub_type']})" if v.get("sub_type") else ""
            src_str = f" {v['source']}" if v.get("source") else ""
            print(f"   ├── {v['quality']}{src_str}{sub_str}{size_str}")
            print(f"   │   {v['url']}")

        print("-" * 50)


def main():
    query = input("Search movie: ").strip()

    rows = search_movies(query)
    grouped = group_movies(rows)
    print_results(grouped)


if __name__ == "__main__":
    main()