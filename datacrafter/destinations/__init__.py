"""Destination modules for writing data to various targets."""
import os

from .bsonf import BSONDestination
from .csv import CSVDestination
from .jsonl import JSONLinesDestination
from .mongo import MongoDBDestination
from .arango import ArangoDBDestination
from .meilisearch import MeilisearchDestination

FILEEXT_MAP = {'file-jsonl': 'jsonl', 'file-bson': 'bson', 'file-csv': 'csv'}
DESTINATION_TYPES_SEARCH = ['meilisearch', ]
DESTINATION_TYPES_DB = ['mongodb', 'arangodb']
DESTINATION_TYPES_FILES = ['file-jsonl', 'file-bson', 'file-csv']
DEFAULT_DELIMITER = ','
DEFAULT_QUOTECHAR = '"'


def get_option_value(options, key, default):
    """Return option value or default"""
    return options[key] if key in options.keys() else default


def get_compression_value(options):
    """Get compression value from either 'compress' or 'compression' key.

    Supports both 'compress' and 'compression' keys for user convenience.
    Returns None if neither key is present.
    """
    if 'compression' in options:
        return options['compression']
    if 'compress' in options:
        return options['compress']
    return None


def get_destination_from_config(dirpath, options):
    """Temporary function to create destination from config.

    Should be replaced in the future.
    """
    if 'type' not in options:
        raise NotImplementedError
    if options['type'] in DESTINATION_TYPES_SEARCH:
        if options['type'] == 'meilisearch':
            return MeilisearchDestination(
                connstr=get_option_value(options, 'connstr', 'https://127.0.0.1:7700'),
                indexname=get_option_value(options, 'indexname', ''),
                token=get_option_value(options, 'token', ''),
                reset=get_option_value(options, 'reset', False),
                incremental=get_option_value(options, 'incremental', True))
    if options['type'] in DESTINATION_TYPES_DB:
        if options['type'] == 'mongodb':
            return MongoDBDestination(
                connstr=get_option_value(
                    options, 'connstr', 'mongodb://localhost:27017'),
                dbname=get_option_value(options, 'dbname', 'default'),
                tablename=get_option_value(options, 'tablename', 'default'),
                username=get_option_value(options, 'username', None),
                password=get_option_value(options, 'password', None))

        if options['type'] == 'arangodb':
            return ArangoDBDestination(
                connstr=get_option_value(
                    options, 'connstr', 'http://localhost:8529'),
                dbname=get_option_value(options, 'dbname', 'default'),
                tablename=get_option_value(options, 'tablename', 'default'),
                username=get_option_value(options, 'username', None),
                password=get_option_value(options, 'password', None))
    if options['type'] not in DESTINATION_TYPES_FILES:
        raise NotImplementedError
    fileprefix = options['fileprefix']
    if options['type'] == 'file-jsonl':
        ext = FILEEXT_MAP[options['type']]
        filename = os.path.join(dirpath, fileprefix + '.' + ext)
        compression = get_compression_value(options)
        if compression is not None:
            filename = filename + '.' + compression
        return JSONLinesDestination(filename=filename, compression=compression)
    if options['type'] == 'file-bson':
        ext = FILEEXT_MAP[options['type']]
        filename = os.path.join(dirpath, fileprefix + '.' + ext)
        compression = get_compression_value(options)
        if compression is not None:
            filename = filename + '.' + compression
        return BSONDestination(filename=filename, compression=compression)
    if options['type'] == 'file-csv':
        ext = FILEEXT_MAP[options['type']]
        filename = os.path.join(dirpath, fileprefix + '.' + ext)
        compression = get_compression_value(options)
        if compression is not None:
            filename = filename + '.' + compression
        delimiter = options.get('delimiter', DEFAULT_DELIMITER)
        quotechar = options.get('quotechar', DEFAULT_QUOTECHAR)
        return CSVDestination(
            filename=filename, delimiter=delimiter, quotechar=quotechar,
            compression=compression)
    raise NotImplementedError
