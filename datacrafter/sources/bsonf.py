"""BSON file source module."""
try:
    import bson
    HAS_BSON = True
except ImportError:
    HAS_BSON = False
    bson = None

from .._registry import register_source
from .base import BaseFileSource


@register_source("bson")
class BSONSource(BaseFileSource):
    """BSON file source implementation."""
    def __init__(self, filename=None, stream=None):
        if not HAS_BSON:
            raise ImportError(
                "bson is required for BSONSource. "
                "Install it with: pip install pymongo"
            )
        super().__init__(filename, stream, binary=True)
        self.reset()
        pass

    def reset(self):
        super().reset()
        self.reader = bson.decode_file_iter(self.fobj)

    def id(self):
        return 'bson'

    def read(self):
        """Write single bson record"""
        return next(self.reader)

    def read_bulk(self, num):
        """Read bulk bson record"""
        chunk = []
        for _ in range(0, num):
            chunk.append(next(self.reader))
        return chunk
