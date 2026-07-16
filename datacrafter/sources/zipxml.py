"""ZIP XML source module."""
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    etree = None

from .zipped import ZIPSourceWrapper
from .._registry import register_source
from ..common.converters import etree_to_dict


@register_source("zipxml")
class ZIPXMLSource(ZIPSourceWrapper):
    """ZIP XML source implementation."""
    def __init__(self, filename=None, tagname=None, prefix_strip=True):
        if not HAS_LXML:
            raise ImportError(
                "lxml is required for ZIPXMLSource. "
                "Install it with: pip install lxml"
            )
        super().__init__(filename)
        self.tagname = tagname
        self.prefix_strip = prefix_strip
        self.reader = etree.iterparse(self.current_file, recover=True)

    def id(self):
        return 'zip-xml'

    def is_flat(self):
        return False

    def reset(self):
        """Reset the XML parser to the beginning of the current file."""
        # Reset file position
        self.filenum = 0
        self.filepos = 0
        self.globalpos = 0
        # Close current file and reopen
        if self.current_file:
            self.current_file.close()
        if self.filenames:
            self.current_file = self.fobj.open(
                self.filenames[self.filenum], mode=self.mode)
            self.reader = etree.iterparse(self.current_file, recover=True)

    def iterfile(self):
        """Move to next file in ZIP archive."""
        res = super().iterfile()
        if res:
            self.reader = etree.iterparse(self.current_file, recover=True)
        return res

    def read_single(self):
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
        self.filepos += 1
        self.globalpos += 1
        return row[self.tagname]
