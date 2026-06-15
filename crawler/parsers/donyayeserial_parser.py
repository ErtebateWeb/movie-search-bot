# English comments only as requested

import re


class DonyayeSerialParser:

    def parse(self, url: str):
        """
        Parse DonyayeSerial directory structure
        and extract structured media info
        """

        parts = url.split("/")

        # Find imdb id in URL
        imdb_id = None
        for p in parts:
            if p.startswith("tt") and p[2:].isdigit() is False:
                imdb_id = p
                break

        # Detect content type
        content_type = "series" if imdb_id else "unknown"

        return {
            "imdb_id": imdb_id,
            "content_type": content_type
        }