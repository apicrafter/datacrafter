"""XML source module."""
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    etree = None

from .._registry import register_source
from ..common.converters import etree_to_dict
from .base import BaseFileSource


@register_source("xml")
class XMLSource(BaseFileSource):
    """XML source implementation."""
    COMPRESSION_MODE = 'binary'

    @classmethod
    def from_config(cls, filename=None, stream=None, options=None):
        options = options or {}
        if 'tagname' not in options:
            raise ValueError(
                f"XML source requires the 'tagname' option; "
                f"got: {sorted(options)}")
        return cls(
            filename=filename, stream=stream, tagname=options['tagname'])

    def __init__(self, filename=None, stream=None, tagname=None, prefix_strip=True):
        if not HAS_LXML:
            raise ImportError(
                "lxml is required for XMLSource. "
                "Install it with: pip install lxml"
            )
        super().__init__(filename, stream, binary=True, encoding='utf8')
        self.tagname = tagname
        self.prefix_strip = prefix_strip
        self.pos = 0
        self.root = None
        self._open_reader()

    def _open_reader(self):
        self.reader = etree.iterparse(self.fobj, recover=True)

    def reset(self):
        """Rewind the stream and rebuild the iterparse reader."""
        super().reset()
        self.root = None
        self.pos = 0
        self._open_reader()

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
                if self.root is None:
                    self.root = elem.getroottree().getroot()
                if self.prefix_strip:
                    row = etree_to_dict(elem, self.prefix_strip)
                else:
                    row = etree_to_dict(elem)
                # Release the parsed element and any accumulated siblings so
                # memory stays bounded for large files.
                elem.clear()
                if self.root is not None:
                    self.root.clear()
        self.pos += 1
        return row[self.tagname]
