import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from config import SOURCES
from database.db import init_db, get_connection
from crawler.parser_factory import ParserFactory
from utils.logger import log_info, log_error

import time

# -------------------------
# CONFIG
# -------------------------
TIMEOUT = 20
MAX_DEPTH = 3

visited = set()

MEDIA_EXTENSIONS = (".mkv", ".mp4", ".avi", ".mov", ".wmv")


# -------------------------
# FETCH
# -------------------------
def fetch(url):
    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception as e:
        log_error(f"Fetch failed: {url} -> {e}")
        return None


# -------------------------
# LINK EXTRACTION
# -------------------------
def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href in ("../", "./"):
            continue

        full_url = urljoin(base_url, href)
        links.append(full_url)

    return links


# -------------------------
# TYPE CHECKS
# -------------------------
def is_media_file(url):
    path = urlparse(url).path.lower()
    return path.endswith(MEDIA_EXTENSIONS)


def is_directory(url):
    path = urlparse(url).path
    last_part = path.rstrip("/").split("/")[-1]

    # no extension => directory
    return "." not in last_part


# -------------------------
# SAVE TO DB
# -------------------------
def save_movie(conn, movie):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO movies (title, year, quality, url)
        VALUES (?, ?, ?, ?)
    """, (
        movie.get("title"),
        movie.get("year"),
        movie.get("quality"),
        movie.get("url")
    ))

    conn.commit()


# -------------------------
# CRAWLER CORE
# -------------------------
def crawl(url, conn, depth=0):
    if depth > MAX_DEPTH:
        return

    clean_url = url.rstrip("/")

    if clean_url in visited:
        return

    visited.add(clean_url)

    log_info(f"[CRAWL] depth={depth} url={url}")

    html = fetch(url)
    if not html:
        return

    links = extract_links(html, url)

    for link in links:

        # MEDIA FILE
        if is_media_file(link):

            parser = ParserFactory.get_parser(link)
            movie = parser.parse(link)
            movie["url"] = link

            save_movie(conn, movie)

            log_info(f"[SAVED] {movie.get('title')}")

        # DIRECTORY
        elif is_directory(link):

            crawl(link, conn, depth + 1)


# -------------------------
# MAIN
# -------------------------
def main():
    init_db()
    conn = get_connection()

    for url in SOURCES:
        crawl(url, conn)

    conn.close()


if __name__ == "__main__":
    main()