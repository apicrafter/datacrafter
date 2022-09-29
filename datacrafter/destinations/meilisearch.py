from arango import ArangoClient

from .base import BaseDBDestination


class ArangoDBDestination(BaseDBDestination):
    """ArangoDB Destination"""
    def __init__(self, connstr, dbname, tablename, username=None, password=None):
        """Init destination"""
        super(ArangoDBDestination, self).__init__(connstr, dbname, tablename, username, password)
        self.client = ArangoClient(connstr)
        self.db = self.client.db(dbname, username, password)
        self.coll = self.db.collection(tablename)
        pass

    def id(self):
        """Return destination identifier"""
        return 'arango'
    
    def write(self, record):
        """Write single record"""
        self.coll.insert(record)

    def write_bulk(self, records):
        """Write bulk"""
        self.coll.insert_many(records)
