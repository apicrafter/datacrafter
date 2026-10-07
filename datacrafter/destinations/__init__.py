"""Destination modules for writing data to various targets."""
import os  # noqa: F401 - re-exported for backwards compatibility

from .._registry import (
    UnknownDestinationTypeError,
    get_destination_class,
    list_destinations,
)
from .arango import ArangoDBDestination
from .base import get_compression_value, get_option_value  # noqa: F401
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
    "get_compression_value",
    "get_option_value",
    "BSONDestination",
    "CSVDestination",
    "JSONLinesDestination",
    "MongoDBDestination",
    "ArangoDBDestination",
    "CouchDBDestination",
    "MeilisearchDestination",
    "ParquetDestination",
]


def get_destination_from_config(dirpath, options):
    """Create a destination instance from a config dict.

    The config ``type`` is validated against the destination registry; an unknown
    type raises :class:`UnknownDestinationTypeError` listing the registered types.
    Construction is delegated to the class's ``from_config``.
    """
    if 'type' not in options:
        raise UnknownDestinationTypeError(
            "Destination config is missing the required 'type' key. "
            f"Registered destination types: {list_destinations()}")
    cls = get_destination_class(options['type'])
    return cls.from_config(dirpath, options)
