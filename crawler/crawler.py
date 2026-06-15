import requests
import sys
import os
import time
from urllib.parse import urljoin, urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from config import SOURCES
from database.db import init_db, get_connection
from crawler.parser_factory import ParserFactory


# ----------------------------
# Global crawl safety controls
# ----------------------------
visited = set()
request_delay = 0.2  # small delay to avoid hammering server


# Fetch HTML page
def fetch(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[ERROR] Fetch failed: {url} -> {e}")
        return None


# Extract links safely using urljoin
def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # Skip parent directory
        if href in ("../", "./"):
            continue

        full_url = urljoin(base_url, href)

        links.append(full_url)

    return links


# Save to DB
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


# Check if URL is file
def is_media_file(url):
    return url.lower().endswith((".mkv", ".mp4", ".avi", ".m4v"))


# Crawl engine
def crawl(url, conn, depth=0, max_depth=3):
    global visited

    # ----------------------------
    # Safety: depth limit
    # ----------------------------
    if depth > max_depth:
        return

    # ----------------------------
    # Safety: avoid duplicates
    # ----------------------------
    if url in visited:
        return

    visited.add(url)

    print(f"[CRAWL] {url}")

    html = fetch(url)

    if not html:
        return

    links = extract_links(html, url)

    for link in links:

        # ----------------------------
        # FILE DETECTED
        # ----------------------------
        if is_media_file(link):

            parser = ParserFactory.get_parser(link)
            movie = parser.parse(link)

            movie["url"] = link

            save_movie(conn, movie)

            print(f"[SAVED] {movie.get('title')}")

        # ----------------------------
        # DIRECTORY DETECTED
        # ----------------------------
        else:
            # Small delay to be polite
            time.sleep(request_delay)

            crawl(link, conn, depth + 1, max_depth)


# Main entry
def main():
    init_db()
    conn = get_connection()

    print("[INFO] Starting crawler...")

    for url in SOURCES:
        crawl(url, conn)

    conn.close()

    print("[INFO] Crawl finished.")


if __name__ == "__main__":
    main()