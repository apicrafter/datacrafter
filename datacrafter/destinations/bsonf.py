"""BSON file destination module."""
try:
    from bson import BSON
    HAS_BSON = True
except ImportError:
    HAS_BSON = False
    BSON = None

from .base import BaseFileDestination
from .._registry import register_destination


@register_destination("file-bson")
class BSONDestination(BaseFileDestination):
    """BSON file destination implementation."""
    def __init__(self, filename, compression=None):
        if not HAS_BSON:
            raise ImportError(
                "bson is required for BSONDestination. "
                "Install it with: pip install pymongo"
            )
        super().__init__(filename, binary=True, compression=compression)

    def id(self):
        return 'bson'

    def write(self, record):
        """Write single bson record"""
        self.fobj.write(BSON.encode(record))

    def write_bulk(self, records):
        """Write bulk bson record"""
        for record in records:
            self.fobj.write(BSON.encode(record))
