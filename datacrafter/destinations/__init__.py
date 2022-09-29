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


def get_destination_from_config(dirpath, options):
    """Temporary function to create destination from config. Should be replaced in the future"""
    if 'type' in options.keys():
        if options['type'] in DESTINATION_TYPES_SEARCH:
            if options['type'] == 'meilisearch':
                return MeilisearchDestination(connstr=get_option_value(options, 'connstr', 'https://127.0.0.1:7700'),
                                          indexname=get_option_value(options, 'indexname', ''),
                                          token=get_option_value(options, 'token', ''),
                                          reset=get_option_value(options, 'reset', False),
                                          incremental=get_option_value(options, 'incremental', True),
                                          )
        elif options['type'] in DESTINATION_TYPES_DB:
            if options['type'] == 'mongodb':
                return MongoDBDestination(connstr=get_option_value(options, 'connstr', 'mongodb://localhost:27017'),
                                          dbname=get_option_value(options, 'dbname', 'default'),
                                          tablename=get_option_value(options, 'tablename', 'default'),
                                          username=get_option_value(options, 'username', None),
                                          password=get_option_value(options, 'password', None),
                                          )

            elif options['type'] == 'arangodb':
                return ArangoDBDestination(connstr=get_option_value(options, 'connstr', 'http://localhost:8529'),
                                          dbname=get_option_value(options, 'dbname', 'default'),
                                          tablename=get_option_value(options, 'tablename', 'default'),
                                          username=get_option_value(options, 'username', None),
                                          password=get_option_value(options, 'password', None),
                                          )
        if options['type'] not in DESTINATION_TYPES_FILES:
            raise NotImplemented            
        fileprefix = options['fileprefix']
        if options['type'] == 'file-jsonl':
            ext = FILEEXT_MAP[options['type']]
            filename = os.path.join(dirpath, fileprefix + '.' + ext)
            if 'compress' in options.keys() and options['compress'] is not None:
                filename = filename + '.' + options['compress']
            return JSONLinesDestination(filename=filename,
                                        compression=options['compress'] if 'compress' in options.keys() else None)
        elif options['type'] == 'file-bson':
            ext = FILEEXT_MAP[options['type']]
            filename = os.path.join(dirpath, fileprefix + '.' + ext)
            if 'compress' in options.keys() and options['compress'] is not None:
                filename = filename + '.' + options['compress']
            return BSONDestination(filename=filename,
                                   compression=options['compress'] if 'compress' in options.keys() else None)
        elif options['type'] == 'file-csv':
            ext = FILEEXT_MAP[options['type']]
            filename = os.path.join(dirpath, fileprefix + '.' + ext)
            if 'compress' in options.keys() and options['compress'] is not None:
                filename = filename + '.' + options['compress']
            return CSVDestination(filename=filename,
                                  delimiter=options[
                                      'delimiter'] if 'delimiter' in options.keys() else DEFAULT_DELIMITER,
                                  quotechar=options[
                                      'quotechar'] if 'quotechar' in options.keys() else DEFAULT_QUOTECHAR,
                                  compression=options['compress'] if 'compress' in options.keys() else None)
        else:
            raise NotImplemented
