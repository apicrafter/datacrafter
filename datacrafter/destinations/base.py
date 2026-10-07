"""Base destination classes for writing data."""
import gzip
import io
import logging
import os.path
from bz2 import BZ2File
from lzma import LZMAFile
from typing import Any, ClassVar, Iterable, Optional
from zipfile import ZIP_DEFLATED, ZipFile

from ..errors import DestinationWriteError

try:
    import zstandard
except ImportError:
    zstandard = None  # type: ignore[assignment]

COMPRESSED_FILE_TYPES = ['gz', 'xz', 'zip', 'bz2', 'zst']
BINARY_FILE_TYPES = ['xls', 'xlsx', 'bson', 'parquet'] + COMPRESSED_FILE_TYPES

# Derived from the codec branches implemented in BaseFileDestination.__init__:
# a codec is supported if and only if a handler branch exists for it.
IMPLEMENTED_COMPRESSION = ('gz', 'bz2', 'xz', 'zip', 'zst')
SUPPORTED_COMPRESSION = {
    ext: ext != 'zst' or zstandard is not None
    for ext in IMPLEMENTED_COMPRESSION
}


def get_option_value(options, key, default):
    """Return option value or default"""
    return options[key] if key in options.keys() else default


def get_compression_value(options):
    """Get compression value from either 'compress' or 'compression' key.

    Supports both keys for user convenience; returns None if neither present.
    """
    if 'compression' in options:
        return options['compression']
    if 'compress' in options:
        return options['compress']
    return None


class BaseDestination:
    """Base destination class"""

    def __init__(self) -> None:
        pass

    def id(self) -> str:
        """Identifier of selected destination"""
        raise NotImplementedError

    def write(self, record: Any) -> None:
        """Write single record"""
        raise NotImplementedError

    def write_bulk(self, records: Iterable[Any]) -> None:
        """Write multiple records"""
        raise NotImplementedError

    def is_flat(self) -> bool:
        """Is destination flat. Default: False"""
        return False

    def is_streaming(self) -> bool:
        """Is destination streaming. Default: False"""
        return False


class BaseFileDestination(BaseDestination):
    """Basic file destination"""

    def id(self) -> str:
        """Identifier of selected destination - must be overridden"""
        raise NotImplementedError

    def write(self, record: Any) -> None:
        """Write single record - must be overridden"""
        raise NotImplementedError

    def write_bulk(self, records: Iterable[Any]) -> None:
        """Write multiple records - must be overridden"""
        raise NotImplementedError

    #: File extension used to build the output filename from ``fileprefix``.
    FILE_EXTENSION: ClassVar[Optional[str]] = None

    @classmethod
    def from_config(cls, dirpath, options):
        """Build a file destination from config (fileprefix + compression)."""
        if cls.FILE_EXTENSION is None:
            raise ValueError(
                f'{cls.__name__} does not support config-based construction')
        if 'fileprefix' not in options:
            raise ValueError(
                f"File destination requires the 'fileprefix' option; "
                f"got: {sorted(options)}")
        compression = get_compression_value(options)
        filename = os.path.join(
            dirpath, options['fileprefix'] + '.' + cls.FILE_EXTENSION)
        if compression is not None:
            filename = filename + '.' + compression
        return cls(
            filename=filename, compression=compression,
            **cls._extra_config_kwargs(options))

    @classmethod
    def _extra_config_kwargs(cls, options):
        """Per-type constructor kwargs beyond filename/compression."""
        return {}

    def __init__(
            self, filename: str, binary: bool = False, encoding: str = 'utf8',
            compression: Optional[str] = None, ftype: Optional[str] = None) -> None:
        self.binary = binary
        self.ftype = ftype
        self.mode = 'wb' if binary else 'w'
        self.fobj: Optional[Any] = None
        # Store reference to underlying file for proper cleanup
        self._underlying_file: Optional[Any] = None
        self._closed = False
        # Store filename for error messages
        self._filename = filename
        logging.info(
            'Destination %s, is binary %s, compression %s',
            filename, binary, compression)
        if not compression:
            if binary:
                self.fobj = open(filename, self.mode, encoding=None)
            else:
                self.fobj = open(filename, self.mode, encoding=encoding)
        else:
            ext = compression
            if ext in SUPPORTED_COMPRESSION and SUPPORTED_COMPRESSION[ext]:
                if ext == 'gz':
                    self.mode = 'wb' if binary else 'wt'
                    if binary:
                        self.fobj = gzip.open(filename, self.mode)
                    else:
                        # Use gzip.open() with text mode and encoding directly
                        # (Python 3.3+)
                        # This avoids the TextIOWrapper issue that causes
                        # "lost gzip_file" error
                        self.fobj = gzip.open(
                            filename, 'wt', encoding=encoding)
                elif ext == 'bz2':
                    if binary:
                        self.fobj = BZ2File(filename, 'wb')
                    else:
                        bz2_file = BZ2File(filename, 'w')
                        self._underlying_file = bz2_file
                        self.fobj = io.TextIOWrapper(bz2_file, encoding=encoding)
                elif ext == 'xz':
                    if binary:
                        self.fobj = LZMAFile(filename, self.mode)
                    else:
                        xz_file = LZMAFile(filename, 'w')
                        self._underlying_file = xz_file
                        self.fobj = io.TextIOWrapper(xz_file, encoding=encoding)
                elif ext == 'zip':
                    self.archiveobj = ZipFile(
                        filename, mode='w', compression=ZIP_DEFLATED)
                    if self.ftype:
                        filename = filename.rsplit('.', 2)[0] + '.' + self.ftype
                    else:
                        filename = filename.rsplit('.', 2)[0] + '.' + self.id()
                    if binary:
                        self.fobj = self.archiveobj.open(filename, 'w')
                    else:
                        zip_file = self.archiveobj.open(os.path.basename(filename), 'w')
                        self._underlying_file = zip_file
                        self.fobj = io.TextIOWrapper(zip_file, encoding=encoding)
                elif ext == 'zst':
                    if zstandard is None:
                        raise ImportError(
                            "zstandard is required for .zst compression. "
                            "Install it with: pip install zstandard")
                    if binary:
                        self.fobj = zstandard.open(filename, self.mode)
                    else:
                        self.fobj = zstandard.open(filename, 'wt', encoding=encoding)
            else:
                raise ValueError(
                    f'Unsupported compression {compression!r}. '
                    f'Supported codecs: {list(IMPLEMENTED_COMPRESSION)}')

    def close(self):
        """Close the output stream, wrapped file, and archive container.

        A flush failure raises ``DestinationWriteError`` after best-effort
        cleanup of every owned stream; closing already-failed resources stays
        best-effort.
        """
        if self._closed:
            return
        self._closed = True
        flush_error = None
        try:
            if self.fobj is not None:
                try:
                    if hasattr(self.fobj, 'flush'):
                        self.fobj.flush()
                except (RuntimeError, OSError, IOError) as error:
                    flush_error = error
                try:
                    self.fobj.close()
                except (RuntimeError, OSError, IOError) as error:
                    logging.debug('Error closing file object: %s', error)
            if self._underlying_file is not None:
                try:
                    self._underlying_file.close()
                except (RuntimeError, OSError, IOError) as error:
                    logging.debug('Error closing underlying file: %s', error)
        finally:
            archiveobj = getattr(self, 'archiveobj', None)
            if archiveobj is not None:
                try:
                    archiveobj.close()
                except (RuntimeError, OSError, IOError) as error:
                    logging.warning('Error closing archive: %s', error)
        if flush_error is not None:
            raise DestinationWriteError(
                f'Failed to flush destination {self._filename}: {flush_error}'
            ) from flush_error

    def __del__(self):
        """Destructor: close all owned streams even without explicit close()"""
        try:
            self.close()
        except Exception:
            # Never raise from a destructor; log for diagnosis instead.
            logging.debug('Error closing destination in destructor', exc_info=True)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures all streams are closed"""
        self.close()
        return False


class BaseDBDestination(BaseDestination):
    """Basic database destination"""

    #: Fallback connection string when the config omits ``connstr``.
    DEFAULT_CONNSTR: ClassVar[Optional[str]] = None

    @classmethod
    def from_config(cls, dirpath, options):
        """Build a DB destination from config (connstr/dbname/tablename)."""
        return cls(
            connstr=get_option_value(options, 'connstr', cls.DEFAULT_CONNSTR),
            dbname=get_option_value(options, 'dbname', 'default'),
            tablename=get_option_value(options, 'tablename', 'default'),
            username=get_option_value(options, 'username', None),
            password=get_option_value(options, 'password', None))

    def __init__(self, connstr, dbname, tablename, username=None, password=None):
        self.connstr = connstr
        self.dbname = dbname
        self.tablename = tablename
        self.username = username
        self.password = password

    def close(self):
        """Should close db connection"""
        raise NotImplementedError


class BaseSearchDestination(BaseDestination):
    """Basic search index destination"""
    def __init__(self, connstr, indexname, token, reset=False, incremental=False):
        """Init basic search index destination"""
        self.connstr = connstr
        self.indexname = indexname
        self.token = token
        self.reset = reset
        self.incremental = incremental

    def close(self):
        """Should close client connection"""
        raise NotImplementedError
