"""CSV destination module."""
from csv import DictWriter

from .base import BaseFileDestination


class CSVDestination(BaseFileDestination):
    """CSV destination implementation."""
    def __init__(
            self, filename, keys=None, delimiter=',', quotechar='"',
            compression=None):
        super().__init__(filename, binary=False, compression=compression)
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.keys = list(keys) if keys is not None else None
        # DictWriter requires concrete fieldnames; when none are provided we defer
        # writer creation until the first record is written, deriving fieldnames
        # from that record (preserving insertion order on Python 3.7+).
        if self.keys is not None:
            self.writer = DictWriter(
                self.fobj, fieldnames=self.keys, delimiter=delimiter,
                quotechar=quotechar)
            self.writer.writeheader()
        else:
            self.writer = None

    def id(self):
        return 'csv'

    def is_flat(self):
        return True

    def write(self, record):
        """Write single CSV record"""
        if self.writer is None:
            self.keys = list(record.keys())
            self.writer = DictWriter(
                self.fobj, fieldnames=self.keys, delimiter=self.delimiter,
                quotechar=self.quotechar)
            self.writer.writeheader()
        self.writer.writerow(record)

    def write_bulk(self, records):
        """Write bulk CSV records"""
        records = list(records)
        if self.writer is None and records:
            self.keys = list(records[0].keys())
            self.writer = DictWriter(
                self.fobj, fieldnames=self.keys, delimiter=self.delimiter,
                quotechar=self.quotechar)
            self.writer.writeheader()
        self.writer.writerows(records)
