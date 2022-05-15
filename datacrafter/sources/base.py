
SOURCE_TYPE_STREAM = 10
SOURCE_TYPE_FILE = 20
DEFAULT_BULK_NUMBER = 100

class BaseSource:
    """Base data source class"""
    def __init__(self):
        pass

    def reset(self):
        """Reset iterator"""
        raise NotImplemented

    def id(self):
        """Identifier of selected destination"""
        raise NotImplemented

    def read(self, skip_empty=True):
        """Read single record"""
        raise NotImplemented

    def read_bulk(self, num=DEFAULT_BULK_NUMBER):
        """Read multiple records"""
        raise NotImplemented

    def is_flat(self):
        """Is source flat flat. Default: False"""
        return False

    def is_streaming(self):
        """Is source streaming. Default: False"""
        return False

    def __next__(self):
        return self.read()

    def __iter__(self):
        self.reset()
        return self


class BaseFileSource(BaseSource):
    """Basic file source"""
    def __init__(self, filename, stream, binary=False, encoding='utf8', noopen=False):
        self.filename = filename
        self.noopen = noopen
        if stream is not None:
            self.stype = SOURCE_TYPE_STREAM
        elif filename is not None:
            self.stype = SOURCE_TYPE_FILE
        if filename:
            if not noopen:
                if binary:
                    self.fobj = open(filename, 'rb')
                else:
                    self.fobj = open(filename, 'r', encoding=encoding)
            else:
                self.fobj = None
        else:
            self.fobj = stream

    def reset(self):
        if not self.noopen:
            self.fobj.seek(0)


    def close(self):
        if self.sourcetype == SOURCE_TYPE_FILE:
            if self.fobj:
                self.fobj.close()

