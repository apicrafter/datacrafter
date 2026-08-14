"""Destination modules for writing data to various targets."""
import os

from .._registry import (
    UnknownDestinationTypeError,
    get_destination_class,
    list_destinations,
)
from .arango import ArangoDBDestination
from .bsonf import BSONDestination
from .couchdb import CouchDBDestination
from .csv import CSVDestination
from .jsonl import JSONLinesDestination
from .meilisearch import MeilisearchDestination
from .mongo import MongoDBDestination
from .parquet import ParquetDestination

__all__ = [
    "UnknownDestinationTypeError",
    "get_destination_class",
    "list_destinations",
    "get_destination_from_config",
    "BSONDestination",
    "CSVDestination",
    "JSONLinesDestination",
    "MongoDBDestination",
    "ArangoDBDestination",
    "CouchDBDestination",
    "MeilisearchDestination",
    "ParquetDestination",
]

FILEEXT_MAP = {
    'file-jsonl': 'jsonl', 'file-bson': 'bson', 'file-csv': 'csv',
    'file-parquet': 'parquet'}
DESTINATION_TYPES_SEARCH = ['meilisearch', ]
DESTINATION_TYPES_DB = ['mongodb', 'arangodb', 'couchdb']
DESTINATION_TYPES_FILES = ['file-jsonl', 'file-bson', 'file-csv', 'file-parquet']
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
    """Create a destination instance from a config dict.

    The config ``type`` is validated against the destination registry; an unknown
    type raises :class:`UnknownDestinationTypeError` listing the registered types.
    (Per-type construction logic is retained here because destination constructors
    take heterogeneous keyword arguments derived from config.)
    """
    if 'type' not in options:
        raise UnknownDestinationTypeError(
            "Destination config is missing the required 'type' key. "
            f"Registered destination types: {list_destinations()}")
    cls = get_destination_class(options['type'])
    dest_type = options['type']
    if dest_type == 'meilisearch':
        return cls(
            connstr=get_option_value(options, 'connstr', 'https://127.0.0.1:7700'),
            indexname=get_option_value(options, 'indexname', ''),
            token=get_option_value(options, 'token', ''),
            reset=get_option_value(options, 'reset', False),
            incremental=get_option_value(options, 'incremental', True))
    if dest_type in DESTINATION_TYPES_DB:
        default_conn = {
            'mongodb': 'mongodb://localhost:27017',
            'arangodb': 'http://localhost:8529',
            'couchdb': 'http://localhost:5984',
        }
        return cls(
            connstr=get_option_value(
                options, 'connstr', default_conn[dest_type]),
            dbname=get_option_value(options, 'dbname', 'default'),
            tablename=get_option_value(options, 'tablename', 'default'),
            username=get_option_value(options, 'username', None),
            password=get_option_value(options, 'password', None))
    if dest_type not in DESTINATION_TYPES_FILES:
        raise UnknownDestinationTypeError(
            f"Unknown destination type {dest_type!r}. "
            f"Registered destination types: {list_destinations()}")
    fileprefix = options['fileprefix']
    ext = FILEEXT_MAP[dest_type]
    filename = os.path.join(dirpath, fileprefix + '.' + ext)
    compression = get_compression_value(options)
    if compression is not None:
        filename = filename + '.' + compression
    if dest_type == 'file-csv':
        return cls(
            filename=filename,
            delimiter=options.get('delimiter', DEFAULT_DELIMITER),
            quotechar=options.get('quotechar', DEFAULT_QUOTECHAR),
            compression=compression)
    if dest_type == 'file-parquet':
        return cls(filename=filename, compression=compression)
    return cls(filename=filename, compression=compression)
