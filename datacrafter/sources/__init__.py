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

import gzip  # noqa: E402
import io  # noqa: E402
from bz2 import BZ2File  # noqa: E402
from lzma import LZMAFile  # noqa: E402

try:
    import zstandard
    HAS_ZSTANDARD = True
except ImportError:
    zstandard = None  # type: ignore[assignment]
    HAS_ZSTANDARD = False


def open_compressed_file(filename, mode='rt', encoding='utf-8'):
    """Open a compressed file and return a file-like object"""
    ext = filename.rsplit('.', 1)[-1].lower()
    text = 't' in mode
    raw_mode = 'rb' if mode.startswith('r') else 'wb'

    if ext == 'gz':
        if text:
            return gzip.open(filename, mode, encoding=encoding)
        return gzip.open(filename, mode)
    if ext == 'bz2':
        stream = BZ2File(filename, raw_mode)
        return io.TextIOWrapper(stream, encoding=encoding) if text else stream
    if ext == 'xz':
        stream = LZMAFile(filename, raw_mode)
        return io.TextIOWrapper(stream, encoding=encoding) if text else stream
    if ext == 'zst':
        if not HAS_ZSTANDARD:
            raise ImportError(
                'zstandard is required for .zst files. '
                'Install it with: pip install zstandard')
        if text:
            return zstandard.open(filename, mode, encoding=encoding)
        return zstandard.open(filename, mode)
    raise ValueError(f"Unsupported compression format: {ext}")



def get_source_from_file(filename, stype=None, options=None):
    """Build a source for a resource file.

    Resolves the class from the registry (by ``stype`` or the file extension)
    and delegates construction to the class's ``from_config``; compressed
    files are opened as decompressed streams for classes that declare
    ``COMPRESSION_MODE``.
    """
    if options is None:
        options = {}
    logging.info(
        'Getting source from extractor results, filename: %s stype: %s, '
        'options: %s',
        str(filename), str(stype), str(options))

    parts = filename.rsplit('.', 2)
    if len(parts) >= 2 and parts[-1].lower() in COMPRESSED_EXTENSIONS:
        is_compressed = True
        compression_ext = parts[-1].lower()
        ext = parts[-2].lower()
        logging.debug(
            'Detected compressed file: %s, compression: %s, type: %s',
            filename, compression_ext, ext)
    else:
        is_compressed = False
        ext = filename.rsplit('.', 1)[-1].lower()

    if not stype:
        if ext in FILEEXT_TO_SOURCETYPE:
            stype = FILEEXT_TO_SOURCETYPE[ext]
        else:
            logging.error('Unknown file type: %s for file %s', ext, filename)
            raise ValueError(
                f'Unknown file type: {ext}. '
                f'Supported types: {list(FILEEXT_TO_SOURCETYPE)}')

    cls = get_source_class(stype)

    file_stream = None
    if is_compressed:
        mode = getattr(cls, 'COMPRESSION_MODE', None)
        if mode is None:
            raise ValueError(
                f'Compressed files are not supported for source type '
                f'{stype!r}; it requires a real file.')
        try:
            if mode == 'text':
                file_stream = open_compressed_file(
                    filename, mode='rt',
                    encoding=options.get('encoding') or 'utf-8')
            else:
                file_stream = open_compressed_file(filename, mode='rb')
            logging.debug(
                'Opened compressed file %s with %s compression',
                filename, compression_ext)
        except Exception as error:
            logging.error(
                'Failed to open compressed file %s: %s', filename, error)
            raise

    return cls.from_config(
        filename=filename, stream=file_stream, options=options)
