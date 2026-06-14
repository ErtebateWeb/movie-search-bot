import sqlite3
import os
from collections import defaultdict

DB_PATH = os.path.join("storage", "movies.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def search_movies(query):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, year, quality, url
        FROM movies
        WHERE title LIKE ?
        ORDER BY year DESC
    """, (f"%{query}%",))

    results = cursor.fetchall()
    conn.close()

    return results


# Group movies by title + year
def group_movies(results):
    grouped = defaultdict(list)

    for title, year, quality, url in results:
        key = f"{title} ({year})"
        grouped[key].append({
            "quality": quality,
            "url": url
        })

    return grouped


def print_grouped(grouped):
    if not grouped:
        print("\nNo results found ❌")
        return

    print(f"\nFound {len(grouped)} movies:\n")

    for i, (movie, versions) in enumerate(grouped.items(), 1):

        print(f"{i}. {movie}")

        for v in versions:
            print(f"   ├── [{v['quality']}] {v['url']}")

        print("-" * 50)


def main():
    query = input("Search movie: ").strip().lower()

    results = search_movies(query)
    grouped = group_movies(results)

    print_grouped(grouped)


if __name__ == "__main__":
    main()