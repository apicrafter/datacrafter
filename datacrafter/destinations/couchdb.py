# -*- coding: utf8 -*-
from .base import BaseDBDestination


class CouchDBDestination(BaseDBDestination):
    """CouchDB Destination"""
    def __init__(self, connstr, dbname, tablename, username=None, password=None):
        """Init destination"""
        import pycouchdb
        super(CouchDBDestination, self).__init__(connstr, dbname, tablename, username, password)
        self.client = pycouchdb.Server(connstr)
        self.coll = self.client.database(dbname)
#        self.coll = self.db.collection(tablename)
        pass

    def id(self):
        """Return destination identifier"""
        return 'couchdb'
    
    def write(self, record):
        """Write single record"""
        self.coll.save(record)

    def write_bulk(self, records):
        """Write bulk"""
        for row in records:
            self.coll.save(row)
