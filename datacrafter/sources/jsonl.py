"""JSON Lines source module."""
from json import loads

from .._registry import register_source
from .base import BaseFileSource


@register_source("jsonl")
class JSONLinesSource(BaseFileSource):
    """JSON Lines source implementation."""
    COMPRESSION_MODE = 'text'

    @classmethod
    def from_config(cls, filename=None, stream=None, options=None):
        return cls(filename=filename, stream=stream)

    def __init__(self, filename=None, stream=None):
        super().__init__(filename, stream, binary=False)
        self.pos = 0

    def id(self):
        return 'jsonl'

    def read(self, skip_empty=False):
        """Read single JSON lines record"""
        line = next(self.fobj)
        if skip_empty and len(line) == 0:
            return self.read(skip_empty)
        self.pos += 1
        if line:
            return loads(line)
        return None
