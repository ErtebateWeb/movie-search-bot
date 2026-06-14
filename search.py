import sqlite3
import os

DB_PATH = os.path.join("storage", "movies.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def search_movies(query):
    conn = get_connection()
    cursor = conn.cursor()

    # Better search with simple ordering
    cursor.execute("""
        SELECT title, year, quality, url
        FROM movies
        WHERE title LIKE ?
        ORDER BY year DESC, quality DESC
        LIMIT 30
    """, (f"%{query}%",))

    results = cursor.fetchall()
    conn.close()

    return results


def print_results(results):
    if not results:
        print("\nNo results found ❌")
        return

    print(f"\nFound {len(results)} results:\n")

    for i, r in enumerate(results, 1):
        title, year, quality, url = r

        print(f"{i}. {title} ({year}) [{quality}]")
        print(url)
        print("-" * 50)


def main():
    query = input("Search movie: ").strip().lower()

    results = search_movies(query)
    print_results(results)


if __name__ == "__main__":
    main()