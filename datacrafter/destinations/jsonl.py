"""JSON Lines destination module."""
from json import dumps

from .._registry import register_destination
from ..common.mappers import date_handler
from .base import BaseFileDestination


@register_destination("file-jsonl")
class JSONLinesDestination(BaseFileDestination):
    """JSON Lines destination implementation."""
    def __init__(self, filename, compression=None):
        super().__init__(filename, binary=False, compression=compression)

    def id(self):
        return 'jsonl'

    def write(self, record):
        """Write single JSON lines record"""
        self.fobj.write(dumps(record, ensure_ascii=False, default=date_handler) + '\n')

    def write_bulk(self, records):
        """Write bulk JSON lines records"""
        lines = [dumps(record, ensure_ascii=False, default=date_handler) + '\n'
                 for record in records]
        self.fobj.writelines(lines)
