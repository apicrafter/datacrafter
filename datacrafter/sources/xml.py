"""XML source module."""
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    etree = None

from .base import BaseFileSource
from ..common.converters import etree_to_dict


class XMLSource(BaseFileSource):
    """XML source implementation."""
    def __init__(self, filename=None, stream=None, tagname=None, prefix_strip=True):
        if not HAS_LXML:
            raise ImportError(
                "lxml is required for XMLSource. "
                "Install it with: pip install lxml"
            )
        super().__init__(filename, stream, binary=True, encoding='utf8')
        self.tagname = tagname
        self.prefix_strip = prefix_strip
        self.reader = etree.iterparse(self.fobj, recover=True)
        self.pos = 0

    def id(self):
        return 'xml'

    def is_flat(self):
        return False

    def read(self):
        """Read single XML record"""
        row = None
        while not row:
            _, elem = next(self.reader)
            shorttag = elem.tag.rsplit('}', 1)[-1]
            if shorttag == self.tagname:
                if self.prefix_strip:
                    row = etree_to_dict(elem, self.prefix_strip)
                else:
                    row = etree_to_dict(elem)
        self.pos += 1
        return row[self.tagname]

    def read_bulk(self, num):
        """Read bulk XML records"""
        chunk = []
        for _ in range(0, num):
            chunk.append(self.read())
        return chunk
