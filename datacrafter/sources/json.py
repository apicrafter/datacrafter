import json

from .base import BaseFileSource


class JSONSource(BaseFileSource):
    def __init__(self, filename=None, stream=None, tagname=None):
        super(JSONSource, self).__init__(filename, stream, binary=False)
        self.tagname = tagname
        self.pos = 0
        self.data = json.load(self.fobj)
        if tagname:
            self.data = self.data[tagname]
        self.total = len(self.data)
        pass

    def id(self):
        return 'json'

    def read(self, skip_empty=False):
        """Read single JSON record"""
        if self.pos >= self.total:
            raise StopIteration

        row = self.data[self.pos]
        self.pos += 1
        return row

    def read_bulk(self, num):
        """Read bulk JSON records"""
        chunk = []
        for n in range(0, num):
            chunk.append(self.read())
        return chunk
