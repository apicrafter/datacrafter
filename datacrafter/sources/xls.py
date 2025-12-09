"""XLS source module."""
import datetime

try:
    import xlrd
    from xlrd import open_workbook
    HAS_XLRD = True
except ImportError:
    HAS_XLRD = False
    xlrd = None
    open_workbook = None

from .base import BaseFileSource


def read_single_row(rownum, ncols, datemode, keys, sheet):
    """Read single row by row num"""
    tmp = []
    for i in range(0, ncols):
        ct = sheet.cell_type(rownum, i)
        cell_value = sheet.cell_value(rownum, i)
        if ct == xlrd.XL_CELL_DATE:
            # Returns a tuple.
            dt_tuple = xlrd.xldate_as_tuple(cell_value, datemode)
            # Create datetime object from this tuple.
            get_col = str(datetime.datetime(
                dt_tuple[0], dt_tuple[1], dt_tuple[2],
                dt_tuple[3], dt_tuple[4], dt_tuple[5]
            ))
        elif ct == xlrd.XL_CELL_NUMBER:
            get_col = int(cell_value)
        else:
            get_col = str(cell_value)
        tmp.append(get_col)
    row = dict(zip(keys, tmp))
    return row



class XLSSource(BaseFileSource):
    """XLS source implementation."""
    def __init__(self, filename=None, stream=None, keys=None, page=0, start_line=1):
        if not HAS_XLRD:
            raise ImportError(
                "xlrd is required for XLSSource. "
                "Install it with: pip install xlrd"
            )
        super().__init__(filename, stream, binary=False, noopen=True)
        self.keys = keys
        self.page = page
        self.start_line = start_line
        self.pos = start_line
        self.reset()

    def reset(self):
        """Reopen file and open sheet"""
        super().reset()
        self.pos = self.start_line
        self.workbook = open_workbook(self.filename)
        self.sheet = self.workbook.sheet_by_index(self.page)

    def id(self):
        """ID of the data source type"""
        return 'xls'

    def is_flat(self):
        """Flag that data is flat"""
        return True

    def read(self):
        """Read single XLS record"""
        if self.pos >= self.sheet.nrows:
            raise StopIteration
        row = read_single_row(
            self.pos, self.sheet.ncols, self.workbook.datemode,
            self.keys, self.sheet)
        self.pos += 1
        return row

    def read_bulk(self, num):
        """Read bulk XLS records"""
        chunk = []
        ncols = self.sheet.ncols
        datemode = self.workbook.datemode
        for _ in range(0, num):
            if self.pos >= self.sheet.nrows:
                raise StopIteration
            row = read_single_row(self.pos, ncols, datemode, self.keys, self.sheet)
            chunk.append(row)
            self.pos += 1
        return chunk
