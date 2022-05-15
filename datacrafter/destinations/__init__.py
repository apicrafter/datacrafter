import os
from .bsonf import BSONDestination
from .jsonl import JSONLinesDestination
from .csv import CSVDestination




FILEEXT_MAP = {'file-jsonl' : 'jsonl', 'file-bson' : 'bson', 'file-csv' : 'csv'}
DESTINATION_TYPES = ['file-jsonl', 'file-bson', 'file-csv']
DEFAULT_DELIMITER = ','
DEFAULT_QUOTECHAR='"'


def get_destination_from_config(dirpath, options):
    fileprefix = options['fileprefix']
    if 'type' in options.keys():
        if options['type'] not in DESTINATION_TYPES:
            raise NotImplemented
        if options['type'] == 'file-jsonl':
            ext = FILEEXT_MAP[options['type']]
            filename = os.path.join(dirpath, fileprefix + '.' + ext)
            if 'compress' in options.keys() and options['compress'] is not None:
                filename = filename + '.' + options['compress']
            return JSONLinesDestination(filename=filename, compression=options['compress'] if 'compress' in options.keys() else None)
        elif options['type'] == 'file-bson':
            ext = FILEEXT_MAP[options['type']]
            filename = os.path.join(dirpath, fileprefix + '.' + ext)
            if 'compress' in options.keys() and options['compress'] is not None:
                filename = filename + '.' + options['compress']
            return BSONDestination(filename=filename, compression=options['compress'] if 'compress' in options.keys() else None)
        elif options['type'] == 'file-csv':
            ext = FILEEXT_MAP[options['type']]
            filename = os.path.join(dirpath, fileprefix + '.' + ext)
            if 'compress' in options.keys() and options['compress'] is not None:
                filename = filename + '.' + options['compress']
            return CSVDestination(filename=filename,
                                  delimiter=options['delimiter'] if 'delimiter' in options.keys() else DEFAULT_DELIMITER,
                                  quotechar=options['quotechar'] if 'quotechar' in options.keys() else DEFAULT_QUOTECHAR,
                                  compression=options['compress'] if 'compress' in options.keys() else None)
        else:
            raise NotImplemented


