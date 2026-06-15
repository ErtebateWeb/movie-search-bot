# This module selects correct parser based on source URL
# English comments only as requested

from crawler.parsers.film9_parser import Film9Parser
from crawler.parsers.donyayeserial_parser import DonyayeSerialParser


class ParserFactory:

    @staticmethod
    def get_parser(url: str):
        # Select parser based on URL pattern

        if "Film9" in url or "Film2Media" in url:
            return Film9Parser()

        if "DonyayeSerial" in url:
            return DonyayeSerialParser()

        # Default fallback parser
        return Film9Parser()