"""CSV source module."""
import logging
from csv import DictReader

from .._registry import register_source
from .base import BaseFileSource


@register_source("csv")
class CSVSource(BaseFileSource):
    """CSV source implementation."""
    COMPRESSION_MODE = 'text'

    @classmethod
    def from_config(cls, filename=None, stream=None, options=None):
        options = options or {}
        keys = (options['keys'].split(',')
                if options.get('keys') else None)
        logging.debug(
            'Use CSV source with filename %s, keys %s, delimiter "%s", encoding %s',
            filename, keys, options.get('delimiter', ','),
            options.get('encoding'))
        return cls(
            filename=filename, stream=stream, keys=keys,
            delimiter=options.get('delimiter', ','),
            encoding=options.get('encoding'))

    def __init__(
            self, filename=None, stream=None, keys=None, delimiter=',',
            quotechar='"', encoding=None):
        super().__init__(filename, stream, binary=False, encoding=encoding)
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.keys = keys
        self.reset()

    def reset(self):
        super().reset()
        if self.keys:
            self.reader = DictReader(
                self.fobj, fieldnames=self.keys, delimiter=self.delimiter,
                quotechar=self.quotechar)
        else:
            self.reader = DictReader(
                self.fobj, delimiter=self.delimiter, quotechar=self.quotechar)
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
