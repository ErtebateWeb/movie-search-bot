import abc
from typing import Optional


class BaseParser(abc.ABC):

    @abc.abstractmethod
    def parse(self, url: str, html: Optional[str] = None):
        pass