from json import dumps

from .base import BaseFileDestination
from ..common.mappers import date_handler


class JSONLinesDestination(BaseFileDestination):
    def __init__(self, filename, compression=None):
        super(JSONLinesDestination, self).__init__(filename, binary=False, compression=compression)
        pass

    def id(self):
        return 'jsonl'

    def write(self, record):
        """Write single JSON lines record"""
        self.fobj.write(dumps(record, ensure_ascii=False, default=date_handler) + '\n')

    def write_bulk(self, records):
        """Write bulk JSON lines records"""
        for record in records:
            self.fobj.write(dumps(record, ensure_ascii=False, default=date_handler) + '\n')
