from csv import DictWriter
from .base import BaseFileDestination
class CSVDestination(BaseFileDestination):
    def __init__(self, filename, keys=None, delimiter=',', quotechar='"', compression=None):
        super(CSVDestination, self).__init__(filename, binary=False, compression=compression)
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.keys = keys
        self.writer = DictWriter(self.fobj, fieldnames=self.keys, delimiter=delimiter, quotechar=quotechar)
        pass

    def id(self):
        return 'csv'

    def is_flat(self):
        return True

    def write(self, record):
        """Write single CSV record"""
        self.writer.writerow(record)

    def write_bulk(self, records):
        """Write bulk CSV records"""
        self.writer.writerows(records)
