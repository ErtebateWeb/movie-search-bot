import re
import os

QUALITY = ["480p", "720p", "1080p", "2160p", "4K"]

def parse_movie(url):
    filename = url.split("/")[-1]

    name = os.path.splitext(filename)[0]

    # Extract year
    year_match = re.search(r"(19|20)\d{2}", name)
    year = year_match.group(0) if year_match else None

    # Extract quality
    quality = None
    for q in QUALITY:
        if q in name:
            quality = q
            break

    # Extract release group (last token usually)
    parts = name.split(".")

    release_group = None
    if len(parts) > 1:
        release_group = parts[-1]

    # Clean title (remove metadata)
    title = re.sub(r"(19|20)\d{2}", "", name)
    title = re.sub(r"\b(" + "|".join(QUALITY) + r")\b", "", title)
    title = re.sub(r"\b(Pahe|Ganool|Film9|HDRip|BluRay|WEBRip)\b", "", title, flags=re.IGNORECASE)

    title = title.replace(".", " ")
    title = re.sub(r"\s+", " ", title).strip()

    return {
        "title": title,
        "year": year,
        "quality": quality,
        "release_group": release_group,
        "url": url
    }