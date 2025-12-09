"""ZIP file source wrapper module."""
from zipfile import ZipFile

from .base import BaseSource


class ZIPSourceWrapper(BaseSource):
    """ZIP file source wrapper implementation."""
    def __init__(self, filename, binary=False):
        super().__init__()
        self.fobj = ZipFile(filename, mode='r')
        self.filenames = self.fobj.namelist()
        self.filenum = 0
        self.filepos = 0
        self.globalpos = 0
        self.mode = 'rb' if binary else 'r'
        self.current_file = self.fobj.open(self.filenames[self.filenum], mode=self.mode)

    def close(self):
        """Close current file and ZIP archive."""
        if self.current_file:
            self.current_file.close()
            self.current_file = None
        self.fobj.close()

    def iterfile(self):
        """Move to next file in ZIP archive."""
        if self.current_file:
            self.current_file.close()
        if self.filenum < len(self.filenames) - 1:
            self.filenum += 1
            filename = self.filenames[self.filenum]
            self.current_file = self.fobj.open(filename, mode=self.mode)
            self.filepos = 0
            return True
        return False

    def read(self):
        """Read single record"""
        try:
            row = self.read_single()
            return row
        except StopIteration as e:
            if self.iterfile():
                row = self.read_single()
                return row
            raise StopIteration from e

    def __iter__(self):
        self.filenum = 0
        filename = self.filenames[self.filenum]
        self.current_file = self.fobj.open(filename, mode=self.mode)
        return self

    def read_single(self):
        """Not implemented single record read"""
        raise NotImplementedError

    def read_bulk(self, num):
        """Read bulk records"""
        chunk = []
        n = 0
        while n < num:
            n += 1
            try:
                chunk.append(self.read())
            except StopIteration:
                return chunk
        return chunk
