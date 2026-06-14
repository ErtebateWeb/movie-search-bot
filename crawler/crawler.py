import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from config import SOURCES

from database.db import init_db, get_connection
from crawler.parser import parse_movie


# Fetch HTML page
def fetch(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


# Extract links from HTML
def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href == "../":
            continue

        links.append(base_url + href)

    return links


# Save movie to database
def save_movie(conn, movie):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO movies (title, year, quality, url)
        VALUES (?, ?, ?, ?)
    """, (
        movie["title"],
        movie["year"],
        movie["quality"],
        movie["url"]
    ))

    conn.commit()


# Recursive crawler
def crawl(url, conn, depth=0, max_depth=2):
    if depth > max_depth:
        return

    print(f"[CRAWL] {url}")

    html = fetch(url)
    if not html:
        return

    links = extract_links(html, url)

    for link in links:

        # File detected
        if link.endswith(".mkv"):
            movie = parse_movie(link)
            save_movie(conn, movie)

            print(f"[SAVED] {movie['title']}")

        # Directory detected
        elif link.endswith("/"):
            crawl(link, conn, depth + 1, max_depth)


def main():
    init_db()
    conn = get_connection()

    for url in SOURCES:
        crawl(url, conn)

    conn.close()


if __name__ == "__main__":
    main()