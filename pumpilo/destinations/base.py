class BaseDestination:
    """Base destination class"""
    def __init__(self):
        pass

    def id(self):
        """Identifier of selected destination"""
        raise NotImplemented

    def write(self, rec):
        """Write single record"""
        raise NotImplemented

    def write_bulk(self, records):
        """Write multiple records"""
        raise NotImplemented

    def is_flat(self):
        """Is destination flat. Default: False"""
        return False

    def is_streaming(self):
        """Is destination streaming. Default: False"""
        return False


class BaseFileDestination:
    """Basic file destination"""
    def __init__(self, filename, binary=False, encoding='utf8'):
        if binary:
            self.fobj = open(filename, 'wb')
        else:
            self.fobj = open(filename, 'w', encoding=encoding)
