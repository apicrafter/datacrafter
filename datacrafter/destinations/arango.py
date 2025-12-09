# -*- coding: utf8 -*-
"""ArangoDB destination module."""
try:
    from arango import ArangoClient
    HAS_ARANGO = True
except ImportError:
    HAS_ARANGO = False
    ArangoClient = None

from .base import BaseDBDestination


class ArangoDBDestination(BaseDBDestination):
    """ArangoDB Destination"""
    def __init__(self, connstr, dbname, tablename, username=None, password=None):
        """Init destination"""
        if not HAS_ARANGO:
            raise ImportError(
                "python-arango is required for ArangoDBDestination. "
                "Install it with: pip install python-arango"
            )
        super().__init__(connstr, dbname, tablename, username, password)
        self.client = ArangoClient(connstr)
        self.db = self.client.db(dbname, username, password)
        self.coll = self.db.collection(tablename)

    def id(self):
        """Return destination identifier"""
        return 'arango'

    def close(self):
        """Close ArangoDB connection."""
        if self.client:
            # ArangoDB client doesn't have explicit close, but we can clean up
            self.client = None
            self.db = None
            self.coll = None

    def write(self, record):
        """Write single record"""
        self.coll.insert(record)

    def write_bulk(self, records):
        """Write bulk"""
        self.coll.insert_many(records)
