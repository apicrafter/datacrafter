#from bson import BSON
import bson
from .base import BaseFileSource
class BSONSource(BaseFileSource):
    def __init__(self, filename=None, stream=None):
        super(BSONSource, self).__init__(filename, stream, binary=True)
        self.reset()
        pass


    def reset(self):
        super(BSONSource, self).reset()
        self.reader = bson.decode_file_iter(self.fobj)


    def id(self):
        return 'bson'

    def read(self):
        """Write single bson record"""
        return next(self.reader)

    def read_bulk(self, num):
        """Read bulk bson record"""
        chunk = []
        for n in range(0, num):
            chunk.append(next(self.reader))
        return chunk
