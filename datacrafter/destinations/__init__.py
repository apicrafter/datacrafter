"""Destination modules for writing data to various targets."""
import os

from .._registry import (
    UnknownDestinationTypeError, get_destination_class, list_destinations)
from .bsonf import BSONDestination
from .csv import CSVDestination
from .jsonl import JSONLinesDestination
from .mongo import MongoDBDestination
from .arango import ArangoDBDestination
from .meilisearch import MeilisearchDestination

__all__ = [
    "UnknownDestinationTypeError",
    "get_destination_class",
    "list_destinations",
    "get_destination_from_config",
]

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
    # Validate the type is registered; raises UnknownDestinationTypeError listing
    # known types if not. The class itself is looked up from the registry so there
    # is a single declaration point (the @register_destination decorator).
    get_destination_class(options['type'])
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
        raise UnknownDestinationTypeError(
            f"Unknown destination type {options['type']!r}. "
            f"Registered destination types: {list_destinations()}")
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
