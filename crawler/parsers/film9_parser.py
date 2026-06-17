import re
import urllib.parse
from crawler.parsers.base import BaseParser

KNOWN_JUNK = [
    "1080p", "720p", "480p", "2160p", "360p",
    "BluRay", "WEBRip", "WEB-DL", "WEB\\.DL", "HDRip", "DVDRip", "BRRip",
    "x264", "x265", "10bit", "HEVC", "AVC",
    "YIFY", "YTS", "RARBG", "PSA", "Pahe", "Ganool",
    "MkvCage", "ShAaNiG", "Tigole", "Ozlem", "AvaMovie", "Unknown", "AdiT",
    "SoftSub", "NoSub", "Dubbed",
    "DonyayeSerial", "Film2Media", "Film9", "Farsi",
    "Remastered", "Extended", "Director\\.Cut", "Theatrical",
]

SOURCE_PATTERN = r"(BluRay|WEBRip|WEB-DL|WEB\.DL|HDRip|DVDRip|BRRip)"
CODEC_PATTERN = r"(x264|x265|10bit|HEVC|AVC)"
GROUP_PATTERN = r"(YIFY|YTS|RARBG|PSA|Pahe|Ganool|MkvCage|ShAaNiG|Tigole|Ozlem|AvaMovie|Unknown|AdiT)"


class Film9Parser(BaseParser):

    def parse(self, url: str, html: str = None):

        url = urllib.parse.unquote(url)
        filename = url.split("/")[-1]

        filename = re.sub(r"\.(mkv|mp4|avi|webm|m4v)$", "", filename, flags=re.I)

        year = re.search(r"(19|20)\d{2}", filename)
        year = year.group(0) if year else None

        quality = re.search(r"(2160p|1080p|720p|480p)", filename)
        quality = quality.group(0) if quality else None

        source_match = re.search(SOURCE_PATTERN, filename, re.I)
        source = source_match.group(1) if source_match else None

        codec_match = re.search(CODEC_PATTERN, filename, re.I)
        codec = codec_match.group(1) if codec_match else None

        group_match = re.search(GROUP_PATTERN, filename, re.I)
        group = group_match.group(1) if group_match else None

        title = filename

        for junk in KNOWN_JUNK:
            title = re.sub(junk, "", title, flags=re.I)

        if year and title.endswith(year):
            title = title[: -len(year)]
        else:
            title = re.sub(r"\b(19|20)\d{2}\b", "", title)

        title = re.sub(r"[._\-]+", " ", title).strip()
        title = re.sub(r"\s+", " ", title).strip()

        if len(title) < 2:
            return None

        return {
            "title": title,
            "year": year,
            "quality": quality,
            "source": source,
            "codec": codec,
            "release_group": group,
            "url": url
        }