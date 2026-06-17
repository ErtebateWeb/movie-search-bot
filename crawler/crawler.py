import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import concurrent.futures
import threading

from database.db import init_db, get_connection, save_movie
from crawler.parser_factory import ParserFactory
from utils.logger import logger

VIDEO_EXTENSIONS = (".mkv", ".mp4", ".avi", ".webm", ".m4v")
MAX_WORKERS = 10
MAX_DEPTH = 7

lock = threading.Lock()


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
        links.append(urljoin(base_url, href))
    return links


def is_video(url):
    return url.lower().endswith(VIDEO_EXTENSIONS)


def process_url(url, conn, visited, depth):
    with lock:
        if url in visited or depth > MAX_DEPTH:
            return []
        visited.add(url)

    logger.info(f"[CRAWL] depth={depth} url={url}")

    html = fetch(url)
    if not html:
        return []

    links = extract_links(html, url)
    new_links = []

    has_movie_listings = "IMDb Code" in html or "start_year" in html

    if has_movie_listings:
        parser = ParserFactory.get_parser(url)
        if hasattr(parser, "parse") and "IMDb Code" in html:
            movies = parser.parse(url, html)
            if isinstance(movies, list):
                for movie in movies:
                    if movie and movie.get("versions"):
                        for version in movie["versions"]:
                            with lock:
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
                return []

    for link in links:
        if is_video(link):
            parser = ParserFactory.get_parser(link)
            movie = parser.parse(link, html)
            if movie:
                with lock:
                    save_movie(conn, movie)
                logger.info(f"[SAVED] {movie['title']}")
        elif link.endswith("/"):
            with lock:
                if link not in visited:
                    new_links.append((link, depth + 1))

    return new_links


def main():
    init_db()
    conn = get_connection()
    visited = set()

    from config import SOURCES

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        active = {}
        for url in SOURCES:
            future = executor.submit(process_url, url, conn, visited, 0)
            active[future] = url

        while active:
            done, _ = concurrent.futures.wait(
                active, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for future in done:
                url = active.pop(future)
                try:
                    new_links = future.result()
                    if new_links:
                        for link, depth in new_links:
                            f = executor.submit(process_url, link, conn, visited, depth)
                            active[f] = link
                except Exception as e:
                    logger.error(f"[ERROR] {url} -> {e}")

    conn.close()


if __name__ == "__main__":
    main()
