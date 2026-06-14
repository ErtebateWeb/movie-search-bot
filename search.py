import sqlite3
import os

DB_PATH = os.path.join("storage", "movies.db")


# Connect to database
def get_connection():
    return sqlite3.connect(DB_PATH)


# Search movies by title keyword
def search_movies(query):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, year, quality, url
        FROM movies
        WHERE title LIKE ?
        LIMIT 20
    """, (f"%{query}%",))

    results = cursor.fetchall()
    conn.close()

    return results


def main():
    query = input("Search movie: ").strip()

    results = search_movies(query)

    if not results:
        print("\nNo results found ❌")
        return

    print(f"\nFound {len(results)} results:\n")

    for r in results:
        title, year, quality, url = r
        print(f"{title} ({year}) [{quality}]")
        print(url)
        print("-" * 50)


if __name__ == "__main__":
    main()