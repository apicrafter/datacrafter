# -*- coding: utf-8 -*-
"""Source modules for reading data from various file formats."""
import logging

from .._registry import UnknownSourceTypeError, get_source_class, list_sources
from .bsonf import BSONSource
from .csv import CSVSource
from .json import JSONSource
from .jsonl import JSONLinesSource
from .xls import XLSSource
from .xlsx import XLSXSource
from .xml import XMLSource
from .zipped import ZIPSourceWrapper
from .zipxml import ZIPXMLSource

__all__ = [
    "UnknownSourceTypeError",
    "get_source_class",
    "list_sources",
    "get_source_from_file",
    "BSONSource",
    "CSVSource",
    "JSONSource",
    "JSONLinesSource",
    "XLSSource",
    "XLSXSource",
    "XMLSource",
    "ZIPSourceWrapper",
    "ZIPXMLSource",
]


def validate_options(options, required=None):
    """Validate that required options are present."""
    if required is None:
        required = []
    for k in required:
        if k not in options.keys():
            raise ValueError
    return True


MAP_REQUIRED_OPTIONS = {
    'zipxml': ['tagname', ],
    'xml': ['tagname', ],
    'xls': ['keys', ],
    'xlsx': ['keys', ],
    'csv': ['delimiter', ]
}

FILEEXT_TO_SOURCETYPE = {
    'xml': 'xml',
    'xls': 'xls',
    'xlsx': 'xlsx',
    'csv': 'csv',
    'jsonl': 'jsonl',
    'bson': 'bson',
    'json': 'json'
}

COMPRESSED_EXTENSIONS = ['gz', 'bz2', 'xz', 'zst']

# Try to import compression libraries
try:
    import gzip
except ImportError:
    pass

try:
    from bz2 import BZ2File
except ImportError:
    pass

try:
    from lzma import LZMAFile
except ImportError:
    pass

try:
    import zstandard
except ImportError:
    pass


def open_compressed_file(filename, mode='rt', encoding='utf-8'):
    """Open a compressed file and return a file-like object"""
    ext = filename.rsplit('.', 1)[-1].lower()

    if ext == 'gz':
        return gzip.open(filename, mode, encoding=encoding)
    elif ext == 'bz2':
        return BZ2File(filename, mode)
    elif ext == 'xz':
        return LZMAFile(filename, mode)
    elif ext == 'zst':
        return zstandard.open(filename, mode, encoding=encoding)
    else:
        raise ValueError(f"Unsupported compression format: {ext}")



def get_source_from_file(filename, stype=None, options=None):
    if options is None:
        options = {}
    logging.info(
        'Getting source from extractor results, filename: %s stype: %s, '
        'options: %s',
        str(filename), str(stype), str(options))

    # Check if file is compressed
    parts = filename.rsplit('.', 2)
    is_compressed = False
    compression_ext = None

    if len(parts) >= 2 and parts[-1].lower() in COMPRESSED_EXTENSIONS:
        is_compressed = True
        compression_ext = parts[-1].lower()
        # Get the actual file extension before compression
        if len(parts) >= 3:
            ext = parts[-2].lower()
        else:
            ext = parts[-2].lower()
        logging.debug(
            'Detected compressed file: %s, compression: %s, type: %s',
            filename, compression_ext, ext)
    else:
        ext = filename.rsplit('.', 1)[-1].lower()

    if not stype:
        if ext in FILEEXT_TO_SOURCETYPE.keys():
            stype = FILEEXT_TO_SOURCETYPE[ext]
        else:
            logging.error('Unknown file type: %s for file %s', ext, filename)
            raise ValueError(
                f'Unknown file type: {ext}. Supported types: {list(FILEEXT_TO_SOURCETYPE.keys())}')

    # Open compressed file if needed
    file_stream = None
    if is_compressed:
        try:
            file_stream = open_compressed_file(
                filename, mode='rt', encoding='utf-8')
            logging.debug(
                'Opened compressed file %s with %s compression',
                filename, compression_ext)
        except Exception as error:
            logging.error(
                'Failed to open compressed file %s: %s', filename, error)
            raise

    cls = get_source_class(stype)

    if stype == 'zipxml':
        validate_options(options, ['tagname', ])
        logging.debug(
            'Use ZIP XML source with filename %s, tag %s',
            filename, options['tagname'])
        return cls(filename=filename, tagname=options['tagname'])
    if stype == 'xml':
        validate_options(options, ['tagname', ])
        logging.debug(
            'Use XML source with filename %s, tag %s',
            filename, options['tagname'])
        return cls(filename=filename, tagname=options['tagname'])
    if stype == 'json':
        tagname = options['tagname'] if 'tagname' in options else None
        logging.debug(
            'Use JSON source with filename %s, tag %s', filename, tagname)
        return cls(filename=filename, tagname=tagname)
    if stype in ('xls', 'xlsx'):
        validate_options(options, ['keys', ])
        keys = options['keys'].split(',') if options.get('keys') else None
        start_line = options['start_line'] if 'start_line' in options else 0
        logging.debug(
            'Use %s source with filename %s, keys %s',
            stype.upper(), filename, keys)
        return cls(filename=filename, keys=keys, start_line=start_line)
    if stype == 'csv':
        keys = options['keys'].split(',') if 'keys' in options else None
        delimiter = options['delimiter'] if 'delimiter' in options else None
        encoding = options['encoding'] if 'encoding' in options else None
        logging.debug(
            'Use CSV source with filename %s, keys %s, delimiter "%s", encoding %s',
            filename, keys, delimiter, encoding)
        return cls(
            filename=filename, keys=keys, delimiter=delimiter, encoding=encoding)
    if stype == 'bson':
        logging.debug('Use BSON source with filename %s', filename)
        return cls(filename=filename)
    if stype == 'jsonl':
        logging.debug('Use JSON lines source with filename %s', filename)
        if file_stream:
            return cls(stream=file_stream)
        return cls(filename=filename)
    raise UnknownSourceTypeError(
        f"Unknown source type {stype!r}. "
        f"Registered source types: {list_sources()}")
