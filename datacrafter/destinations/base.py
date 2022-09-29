import gzip
import io
import logging
import os.path
from bz2 import BZ2File
from lzma import LZMAFile
from zipfile import ZipFile, ZIP_DEFLATED

SUPPORTED_FILE_TYPES = ['xls', 'xlsx', 'csv', 'xml', 'json', 'jsonl', 'yaml', 'tsv', 'sql', 'bson', 'parquet']
COMPRESSED_FILE_TYPES = ['gz', 'xz', 'zip', 'lz4', '7z', 'bz2']
BINARY_FILE_TYPES = ['xls', 'xlsx', 'bson', 'parquet'] + COMPRESSED_FILE_TYPES

SUPPORTED_COMPRESSION = {'gz': True, 'zip': True, 'xz': False, '7z': False, 'lz4': False, 'bz2': True}

try:
    import lz4
    SUPPORTED_COMPRESSION['lz4'] = True
except ImportError:
    pass

try:
    import py7zr

    SUPPORTED_COMPRESSION['7z'] = True
except ImportError:
    pass


class BaseDestination:
    """Base destination class"""

    def __init__(self):
        pass

    def id(self):
        """Identifier of selected destination"""
        raise NotImplementedError

    def write(self, rec):
        """Write single record"""
        raise NotImplementedError

    def write_bulk(self, records):
        """Write multiple records"""
        raise NotImplementedError

    def is_flat(self):
        """Is destination flat. Default: False"""
        return False

    def is_streaming(self):
        """Is destination streaming. Default: False"""
        return False


class BaseFileDestination(BaseDestination):
    """Basic file destination"""

    def __init__(self, filename, binary=False, encoding='utf8', compression=None, ftype=None):
        self.binary = binary
        self.ftype = ftype
        self.mode = 'wb' if binary else 'w'
        logging.info('Destination %s, is binary %s, compression %s' % (filename, str(binary), str(compression)))
        if not compression:
            self.fobj = open(filename, self.mode) if binary else open(filename, self.mode, encoding=encoding)
        else:
            ext = compression
            if ext in SUPPORTED_COMPRESSION.keys():
                if ext == 'gz':
                    self.mode = 'wb' if binary else 'wt'
                    if binary:
                        self.fobj = gzip.open(filename, self.mode)
                    else:
                        self.fobj = io.TextIOWrapper(gzip.open(filename, 'w'), encoding=encoding)
                elif ext == 'bz2':
                    if binary:
                        self.fobj = BZ2File(filename, self.mode)
                    else:
                        self.fobj = io.TextIOWrapper(BZ2File(filename, 'w'), encoding=encoding)
                elif ext == 'xz':
                    if binary:
                        self.fobj = LZMAFile(filename, self.mode)
                    else:
                        self.fobj = io.TextIOWrapper(LZMAFile(filename, 'w'), encoding=encoding)
                elif ext == 'zip':
                    self.archiveobj = ZipFile(filename, mode='w', compression=ZIP_DEFLATED)
                    filename = filename.rsplit('.', 2)[0] + '.' + self.ftype if self.ftype else filename.rsplit('.', 2)[
                                                                                                    0] + '.' + self.id()
                    if binary:
                        self.fobj = self.archiveobj.open(filename, 'w')
                    else:
                        self.fobj = io.TextIOWrapper(self.archiveobj.open(os.path.basename(filename), 'w'),
                                                     encoding=encoding)
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError

    def close(self):
        """Close file and archive container if ZIP or 7z file formats"""
        if self.fobj:
            self.fobj.close()
        if hasattr(self, 'archiveobj'):
            self.archiveobj.close()


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
        """Init basic search indexedr destination"""
        self.connstr = connstr
        self.indexname = indexname
        self.token = token
        self.reset = reset
        self.incremental = incremental

    def close(self):
        """Should close client connection"""
        raise NotImplementedError
