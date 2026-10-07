"""BSON file source module."""
try:
    import bson
    HAS_BSON = True
except ImportError:
    HAS_BSON = False
    bson = None  # type: ignore[assignment]

from .._registry import register_source
from .base import BaseFileSource


@register_source("bson")
class BSONSource(BaseFileSource):
    """BSON file source implementation."""
    COMPRESSION_MODE = 'binary'

    @classmethod
    def from_config(cls, filename=None, stream=None, options=None):
        return cls(filename=filename, stream=stream)

    def __init__(self, filename=None, stream=None):
        if not HAS_BSON:
            raise ImportError(
                "bson is required for BSONSource. "
                "Install it with: pip install pymongo"
            )
        super().__init__(filename, stream, binary=True)
        self.reset()

    def reset(self):
        super().reset()
        self.reader = bson.decode_file_iter(self.fobj)

    def id(self):
        return 'bson'

    def read(self):
        """Read single bson record"""
        return next(self.reader)
