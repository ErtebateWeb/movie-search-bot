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
    grouped = {}

    for title, year, quality, url in results:
        key = f"{title} ({year})"

        if key not in grouped:
            grouped[key] = {
                "title": title,
                "year": year,
                "versions": []
            }

        grouped[key]["versions"].append({
            "quality": quality,
            "url": url
        })

    return grouped

def print_grouped(grouped):
    if not grouped:
        print("\nNo results found ❌")
        return

    print(f"\nFound {len(grouped)} movies:\n")

    for i, (key, movie) in enumerate(grouped.items(), 1):

        title = movie["title"]
        year = movie["year"]
        versions = movie["versions"]

        print(f"{i}. {title} ({year})")

        # Print available qualities as selectable options
        qualities = [v["quality"] for v in versions]

        print("   Available qualities:")
        print("   ", " | ".join([f"[{q}]" for q in qualities]))

        print("\n   Versions:")

        for v in versions:
            print(f"   ├── {v['quality']} → {v['url']}")

        print("-" * 50)
def main():
    query = input("Search movie: ").strip().lower()

    results = search_movies(query)
    grouped = group_movies(results)

    print_grouped(grouped)


if __name__ == "__main__":
    main()