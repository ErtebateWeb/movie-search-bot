import re
import urllib.parse
from crawler.parsers.base import BaseParser


class Film9Parser(BaseParser):

    def parse(self, url: str, html: str = None):

        url = urllib.parse.unquote(url)
        filename = url.split("/")[-1]

        filename = re.sub(r"\.(mkv|mp4|avi|webm|m4v)$", "", filename, flags=re.I)

        year = re.search(r"(19|20)\d{2}", filename)
        year = year.group(0) if year else None

        quality = re.search(r"(2160p|1080p|720p|480p)", filename)
        quality = quality.group(0) if quality else None

        title = filename

        junk = [
            "1080p","720p","480p","BluRay","Web-DL","HDRip",
            "Farsi","Dubbed","Film9","Film2Media","YIFY","Pahe","Ganool"
        ]

        for j in junk:
            title = re.sub(j, "", title, flags=re.I)

        title = re.sub(r"[._\-]+", " ", title).strip()

        if len(title) < 2:
            return None

        return {
            "title": title,
            "year": year,
            "quality": quality,
            "url": url
        }