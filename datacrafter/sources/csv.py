from csv import DictReader

from .base import BaseFileSource


class CSVSource(BaseFileSource):
    def __init__(self, filename=None, stream=None, keys=None, delimiter=',', quotechar='"', encoding=None):
        super(CSVSource, self).__init__(filename, stream, binary=False, encoding=encoding)
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.keys = keys
        self.reset()
        pass

    def reset(self):
        super(CSVSource, self).reset()
        if self.keys:
            self.reader = DictReader(self.fobj, fieldnames=self.keys, delimiter=self.delimiter,
                                     quotechar=self.quotechar)
        else:
            self.reader = DictReader(self.fobj, delimiter=self.delimiter, quotechar=self.quotechar)
        #            self.reader = reader(self.fobj, delimiter=self.delimiter, quotechar=self.quotechar)
        self.pos = 0

    def id(self):
        return 'csv'

    def is_flat(self):
        return True

    def read(self, skip_empty=True):
        """Read single CSV record"""
        row = next(self.reader)
        if skip_empty and len(row) == 0:
            return self.read(skip_empty)
        self.pos += 1
        return row

    def read_bulk(self, num):
        """Read bulk CSV records"""
        chunk = []
        for n in range(0, num):
            chunk.append(next(self.reader))
            self.pos += 1
        return chunk
