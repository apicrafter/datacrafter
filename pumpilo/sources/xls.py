from xlrd import open_workbook
from .base import BaseFileSource


class XLSSource(BaseFileSource):
    def __init__(self, filename=None, stream=None, keys=None, page=0, start_line=1):
        super(XLSSource, self).__init__(filename, stream, binary=False, noopen=True)
        self.keys = keys
        self.page = page
        self.start_line = start_line
        self.pos = start_line
        self.reset()
        pass


    def reset(self):
        super(XLSSource, self).reset()
        self.pos = self.start_line
        self.workbook = open_workbook(self.filename)
        self.sheet = self.workbook.sheet_by_index(self.page)

    def id(self):
        return 'xls'

    def is_flat(self):
        return True

    def read(self):
        """Read single XLS record"""
        if self.pos >= self.sheet.nrows:
            raise StopIteration
        tmp = list()
        for i in range(0, self.sheet.ncols):
            tmp.append(self.sheet.row_values(self.pos)[i])
        row = dict(zip(self.keys, tmp))
        self.pos += 1
        return row

    def read_bulk(self, num):
        """Read bulk XLS records"""
        chunk = []
        for n in range(0, num):
            if self.pos >= self.sheet.nrows:
                raise StopIteration
            tmp = list()
            for i in range(0, self.sheet.ncols):
                tmp.append(self.sheet.row_values(self.pos)[i])
            row = dict(zip(self.keys, tmp))
            chunk.append(row)
            self.pos += 1
        return chunk
