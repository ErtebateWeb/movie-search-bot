import sys
import os

# Add project root to path so sibling packages (database, utils) are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

from database.db import init_db, get_connection, save_movie
from crawler.parser_factory import ParserFactory
from utils.logger import logger

VIDEO_EXTENSIONS = (".mkv", ".mp4", ".avi", ".webm", ".m4v")


def fetch(url):
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return r.text
    except Exception as e:
        logger.error(f"[FETCH ERROR] {url} -> {e}")
        return None


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


def is_video(url):
    return url.lower().endswith(VIDEO_EXTENSIONS)


def crawl(url, conn, depth=0, max_depth=7, visited=None):
    if visited is None:
        visited = set()

    if url in visited:
        return

    visited.add(url)

    logger.info(f"[CRAWL] depth={depth} url={url}")

    html = fetch(url)
    if not html:
        return

    links = extract_links(html, url)

    # Check if this page has archive-style movie listings
    has_movie_listings = "IMDb Code" in html or "start_year" in html

    if has_movie_listings:
        parser = ParserFactory.get_parser(url)
        if hasattr(parser, "parse") and "IMDb Code" in html:
            movies = parser.parse(url, html)
            if isinstance(movies, list):
                for movie in movies:
                    if movie and movie.get("versions"):
                        for version in movie["versions"]:
                            save_movie(conn, {
                                "title": movie.get("title"),
                                "year": movie.get("year"),
                                "quality": version.get("quality_label"),
                                "imdb_id": movie.get("imdb_id"),
                                "rating": movie.get("rating"),
                                "votes": movie.get("votes"),
                                "url": version.get("url"),
                                "file_size": version.get("size"),
                                "sub_type": version.get("sub_type"),
                            })
                        logger.info(f"[ARCHIVE] {movie.get('title')} ({len(movie['versions'])} versions)")
                return

    for link in links:

        # جلوگیری از loop و garbage
        if link in visited:
            continue

        # FILE
        if is_video(link):
            parser = ParserFactory.get_parser(link)
            movie = parser.parse(link, html)

            if movie:
                save_movie(conn, movie)
                logger.info(f"[SAVED] {movie['title']}")

        # DIRECTORY
        elif link.endswith("/") and depth < max_depth:
            crawl(link, conn, depth + 1, max_depth, visited)


def main():
    init_db()
    conn = get_connection()

    from config import SOURCES

    for url in SOURCES:
        crawl(url, conn)

    conn.close()


if __name__ == "__main__":
    main()