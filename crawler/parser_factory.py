from crawler.parsers.film9_parser import Film9Parser
from crawler.parsers.donyayeserial_parser import (
    DonyayeSerialParser,
    DonyayeSerialArchiveParser,
)


class ParserFactory:

    @staticmethod
    def get_parser(url: str):

        if "film9" in url.lower() or "film2media" in url.lower():
            return Film9Parser()

        if "dls2.aparatchi-dlcenter.top" in url:
            # Archive pages (top_5000_movies.html etc.) contain structured movie listings
            if url.endswith(".html"):
                return DonyayeSerialArchiveParser()
            return DonyayeSerialParser()

        return Film9Parser()