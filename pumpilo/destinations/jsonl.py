from json import dumps
from ..common.mappers import date_handler
from .base import BaseFileDestination
class JSONLinesDestination(BaseFileDestination):
    def __init__(self, filename):
        super(JSONLinesDestination, self).__init__(filename, binary=False)
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
