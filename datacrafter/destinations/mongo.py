"""MongoDB destination module."""
try:
    from pymongo import MongoClient
    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False
    MongoClient = None

from .._registry import register_destination
from .base import BaseDBDestination


@register_destination("mongodb")
class MongoDBDestination(BaseDBDestination):
    """MongoDB destination implementation."""
    def __init__(self, connstr, dbname, tablename, username=None, password=None):
        """Init destination"""
        if not HAS_PYMONGO:
            raise ImportError(
                "pymongo is required for MongoDBDestination. "
                "Install it with: pip install pymongo"
            )
        super().__init__(
            connstr, dbname, tablename, username=username, password=password)
        self.client = MongoClient(connstr)
        self.coll = self.client[dbname][tablename]  # pylint: disable=invalid-name

    def id(self):
        """Return destination identifier"""
        return 'mongodb'

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()

    def write(self, record):
        """Write single record."""
        self.coll.insert_one(record)

    def write_bulk(self, records):
        """Write bulk"""
        self.coll.insert_many(records)
