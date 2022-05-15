from json import loads
from .base import BaseFileSource
class JSONLinesSource(BaseFileSource):
    def __init__(self, filename=None, stream=None):
        super(JSONLinesSource, self).__init__(filename, stream, binary=False)
        self.pos = 0
        pass

    def id(self):
        return 'jsonl'

    def read(self, skip_empty=False):
        """Read single JSON lines record"""
        line = next(self.fobj)
        if skip_empty and len(line) == 0:
            return self.read(skip_empty)
        self.pos += 1
        if line:
            return loads(line)
        return None

    def read_bulk(self, num):
        """Read bulk JSON lines records"""
        chunk = []
        for n in range(0, num):
            chunk.append(loads(self.fobj.readline()))
        return chunk
