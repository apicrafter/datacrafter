# -*- coding: utf8 -*-
"""CouchDB destination module."""
try:
    import pycouchdb
    HAS_PYCOUCHDB = True
except ImportError:
    HAS_PYCOUCHDB = False
    pycouchdb = None

from .base import BaseDBDestination


class CouchDBDestination(BaseDBDestination):
    """CouchDB Destination"""
    def __init__(self, connstr, dbname, tablename, username=None, password=None):
        """Init destination"""
        if not HAS_PYCOUCHDB:
            raise ImportError(
                "pycouchdb is required for CouchDBDestination. "
                "Install it with: pip install pycouchdb"
            )
        super().__init__(connstr, dbname, tablename, username, password)
        self.client = pycouchdb.Server(connstr)
        self.coll = self.client.database(dbname)
#        self.coll = self.db.collection(tablename)

    def id(self):
        """Return destination identifier"""
        return 'couchdb'

    def close(self):
        """Close CouchDB connection."""
        # pycouchdb doesn't have explicit close, but we can clean up references
        self.client = None
        self.coll = None

    def write(self, record):
        """Write single record"""
        self.coll.save(record)

    def write_bulk(self, records):
        """Write bulk"""
        for row in records:
            self.coll.save(row)
