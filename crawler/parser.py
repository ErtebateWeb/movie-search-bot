import re
import urllib.parse

VIDEO_EXTENSIONS = (".mkv", ".mp4", ".avi", ".webm", ".m4v")


def is_valid_file(url: str) -> bool:
    url = url.lower()
    return url.endswith(VIDEO_EXTENSIONS)


def clean_url(url: str) -> str:
    return urllib.parse.unquote(url)


def extract_info_from_url(url: str):
    """
    Extract:
    - title
    - year
    - quality
    """

    url = clean_url(url)

    filename = url.split("/")[-1]

    # remove extension
    filename = re.sub(r"\.(mkv|mp4|avi|webm|m4v)$", "", filename, flags=re.I)

    # YEAR
    year_match = re.search(r"(19|20)\d{2}", filename)
    year = year_match.group(0) if year_match else None

    # QUALITY
    quality_match = re.search(r"(2160p|1080p|720p|480p|360p)", filename, re.I)
    quality = quality_match.group(0) if quality_match else None

    # CLEAN TITLE
    title = filename

    # remove quality + source tags
    junk_patterns = [
        r"\b1080p\b", r"\b720p\b", r"\b480p\b", r"\b2160p\b",
        r"\bBluRay\b", r"\bWeb[- ]DL\b", r"\bHDRip\b",
        r"\bFarsi\b", r"\bDubbed\b", r"\bx265\b",
        r"\bYIFY\b", r"\bGanool\b", r"\bPahe\b", r"\bFilm9\b",
        r"\bFilm2Media\b", r"\bShAaNiG\b", r"\bTigole\b"
    ]

    for pattern in junk_patterns:
        title = re.sub(pattern, "", title, flags=re.I)

    # clean separators
    title = re.sub(r"[._%\-]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip()

    return {
        "title": title if title else None,
        "year": year,
        "quality": quality,
        "url": url
    }


def parse_movie(url: str):
    """
    Main parser entry
    """

    if not is_valid_file(url):
        return None

    info = extract_info_from_url(url)

    # skip garbage titles like empty or "New Server"
    if not info["title"] or len(info["title"]) < 2:
        return None

    return info