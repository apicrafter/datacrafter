"""Base destination classes for writing data."""
import gzip
import importlib.util
import io
import logging
import os.path
from bz2 import BZ2File
from lzma import LZMAFile
from typing import Any, Iterable, Optional
from zipfile import ZIP_DEFLATED, ZipFile

COMPRESSED_FILE_TYPES = [
    'gz', 'xz', 'zip', 'lz4', '7z', 'bz2', 'zst']
BINARY_FILE_TYPES = ['xls', 'xlsx', 'bson', 'parquet'] + COMPRESSED_FILE_TYPES

SUPPORTED_COMPRESSION = {
    'gz': True, 'zip': True, 'xz': False, '7z': False, 'lz4': False,
    'bz2': True, 'zst': False}

SUPPORTED_COMPRESSION['lz4'] = importlib.util.find_spec('lz4') is not None
SUPPORTED_COMPRESSION['7z'] = importlib.util.find_spec('py7zr') is not None

try:
    import zstandard
    SUPPORTED_COMPRESSION['zst'] = True
except ImportError:
    zstandard = None


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

    def __init__(
            self, filename: str, binary: bool = False, encoding: str = 'utf8',
            compression: Optional[str] = None, ftype: Optional[str] = None) -> None:
        self.binary = binary
        self.ftype = ftype
        self.mode = 'wb' if binary else 'w'
        self.fobj = None
        # Store reference to underlying file for proper cleanup
        self._underlying_file = None
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
            if ext in SUPPORTED_COMPRESSION:
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
                        self.fobj = BZ2File(filename, self.mode)
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
                    raise NotImplementedError
            else:
                raise NotImplementedError

    def close(self):
        """Close file and archive container if ZIP or 7z file formats"""
        if self._closed:
            return

        try:
            if self.fobj is not None:
                try:
                    # Flush before closing to ensure all data is written
                    if hasattr(self.fobj, 'flush'):
                        try:
                            self.fobj.flush()
                        except (RuntimeError, OSError, IOError):
                            # Ignore flush errors, proceed to close
                            pass
                    self.fobj.close()
                except (RuntimeError, OSError, IOError) as error:
                    # Handle "lost gzip_file" and similar errors gracefully
                    error_msg = str(error).lower()
                    if 'lost gzip_file' in error_msg or 'lost' in error_msg:
                        # This is a known issue with gzip files wrapped in
                        # TextIOWrapper
                        # Should not happen with direct gzip.open() text mode,
                        # but handle gracefully
                        logging.debug(
                            'Encountered gzip file closure issue: %s', error)
                    else:
                        logging.warning('Error closing file object: %s', error)
                    # Try to close underlying file if it exists
                    # (for TextIOWrapper cases)
                    if self._underlying_file is not None:
                        try:
                            self._underlying_file.close()
                        except Exception as close_error:
                            logging.debug(
                                'Error closing underlying file: %s', close_error)
                except Exception as error:
                    logging.warning(
                        'Unexpected error closing file object: %s', error)
                    # Try to close underlying file if it exists
                    if self._underlying_file is not None:
                        try:
                            self._underlying_file.close()
                        except Exception as close_error:
                            logging.debug(
                                'Error closing underlying file: %s', close_error)
        except Exception as error:
            logging.warning('Error in close() method: %s', error)
        finally:
            # Close archive container if it exists (for ZIP files)
            if hasattr(self, 'archiveobj') and self.archiveobj is not None:
                try:
                    self.archiveobj.close()
                except Exception as error:
                    logging.warning('Error closing archive: %s', error)
            self._closed = True

    def __del__(self):
        """Destructor: ensure file is closed even if close() wasn't called explicitly"""
        if not self._closed and self.fobj is not None:
            try:
                self.fobj.close()
            except Exception as error:
                logging.debug(
                    'Error closing file in destructor: %s', error)
            self._closed = True


class BaseDBDestination(BaseDestination):
    """Basic database destination"""

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
