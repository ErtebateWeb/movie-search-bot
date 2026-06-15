# English comments only as requested

import re
from urllib.parse import urlparse


class Film9Parser:

    def parse(self, url: str):
        """
        Parse direct file-based movie links (Film9 / Film2Media style)
        Example:
        Zootopia.2016.1080p.Farsi.2Dubbed.Film2Media.mkv
        """

        filename = urlparse(url).path.split("/")[-1]

        # Extract year (4 digits)
        year_match = re.search(r"(19|20)\d{2}", filename)
        year = year_match.group(0) if year_match else None

        # Extract quality
        quality_match = re.search(r"(480p|720p|1080p|2160p)", filename)
        quality = quality_match.group(0) if quality_match else None

        # Detect language / dub
        language = "dubbed" if "dubbed" in filename.lower() else None

        # Clean title (remove dots and technical parts)
        title = filename

        # Remove extension
        title = re.sub(r"\.mkv$|\.mp4$", "", title)

        # Remove quality and extra tags
        title = re.sub(r"(480p|720p|1080p|2160p)", "", title)
        title = re.sub(r"\d{4}", "", title)
        title = title.replace(".", " ").strip()

        return {
            "title": title,
            "year": year,
            "quality": quality,
            "source": "film9",
            "imdb_id": None,
            "content_type": "movie",
            "season": None,
            "episode": None,
            "language": language
        }