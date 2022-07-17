from pymongo import MongoClient

from .base import BaseDBDestination


class MongoDBDestination(BaseDBDestination):
    def __init__(self, connstr, dbname, tablename, username=None, password=None):
        """Init destination"""
        super(MongoDBDestination, self).__init__(connstr, dbname, tablename, username=username, password=password)
        self.client = MongoClient(connstr)
        self.coll = self.client[dbname][tablename]
        pass

    def id(self):
        """Return destination identifier"""
        return 'mongodb'
    
    def write(self, record):
        """Write single record"""
        self.coll.insert_one(record)

    def write_bulk(self, records):
        """Write bulk"""
        self.coll.insert_many(records)
