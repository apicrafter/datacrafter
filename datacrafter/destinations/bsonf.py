from bson import BSON

from .base import BaseFileDestination


class BSONDestination(BaseFileDestination):
    def __init__(self, filename, compression=None):
        super(BSONDestination, self).__init__(filename, binary=True, compression=compression)
        pass

    def id(self):
        return 'bson'

    def write(self, record):
        """Write single bson record"""
        self.fobj.write(BSON.encode(record))

    def write_bulk(self, records):
        """Write bulk bson record"""
        for record in records:
            self.fobj.write(BSON.encode(record))
