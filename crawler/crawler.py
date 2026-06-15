import requests
import sys
import os
from urllib.parse import urljoin
# Fix import path (keep it clean)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from config import SOURCES
from database.db import init_db, get_connection

# NEW: use parser factory instead of old parser
from crawler.parser_factory import ParserFactory


# Fetch HTML page
def fetch(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[ERROR] Fetch failed: {url} -> {e}")
        return None


# Extract links from directory listing
def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href == "../":
            continue

        full_url = urljoin(base_url, href)
        links.append(full_url)

    return links


# Save structured media to database
def save_movie(conn, movie):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO movies (
            title, year, quality, url,
            source, imdb_id, content_type,
            season, episode, language
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        movie.get("title"),
        movie.get("year"),
        movie.get("quality"),
        movie.get("url"),
        movie.get("source"),
        movie.get("imdb_id"),
        movie.get("content_type"),
        movie.get("season"),
        movie.get("episode"),
        movie.get("language"),
    ))

    conn.commit()


# Recursive crawler engine
def crawl(url, conn, depth=0, max_depth=2):
    if depth > max_depth:
        return

    print(f"[CRAWL] {url}")

    html = fetch(url)
    if not html:
        return

    links = extract_links(html, url)

    for link in links:

        # -------------------------
        # FILE DETECTED (movie/episode)
        # -------------------------
        if link.endswith((".mkv", ".mp4", ".avi")):

            # Select correct parser based on source
            parser = ParserFactory.get_parser(link)

            movie = parser.parse(link)

            # Add URL explicitly (important)
            movie["url"] = link

            save_movie(conn, movie)

            print(f"[SAVED] {movie.get('title')}")

        # -------------------------
        # DIRECTORY DETECTED
        # -------------------------
        elif link.endswith("/"):
            crawl(link, conn, depth + 1, max_depth)


# App entry point
def main():
    init_db()
    conn = get_connection()

    for url in SOURCES:
        crawl(url, conn)

    conn.close()


if __name__ == "__main__":
    main()