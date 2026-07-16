from typing import Any, Iterator, List, Optional


SOURCE_TYPE_STREAM = 10
SOURCE_TYPE_FILE = 20
DEFAULT_BULK_NUMBER = 100


class BaseSource:
    """Base data source class"""

    def __init__(self) -> None:
        pass

    def reset(self) -> None:
        """Reset iterator"""
        raise NotImplementedError

    def id(self) -> str:
        """Identifier of selected destination"""
        raise NotImplementedError

    def read(self, skip_empty: bool = True) -> Optional[Any]:
        """Read single record"""
        raise NotImplementedError

    def read_bulk(self, num: int = DEFAULT_BULK_NUMBER) -> List[Any]:
        """Read multiple records"""
        raise NotImplementedError

    def is_flat(self) -> bool:
        """Is source flat flat. Default: False"""
        return False

    def is_streaming(self) -> bool:
        """Is source streaming. Default: False"""
        return False

    def __next__(self) -> Any:
        return self.read()

    def __iter__(self) -> Iterator[Any]:
        self.reset()
        return self


class BaseFileSource(BaseSource):
    """Basic file source"""

    def id(self) -> str:
        """Identifier of selected source - must be overridden"""
        raise NotImplementedError

    def read(self, skip_empty: bool = True) -> Optional[Any]:
        """Read single record - must be overridden"""
        raise NotImplementedError

    def read_bulk(self, num: int = DEFAULT_BULK_NUMBER) -> List[Any]:
        """Read multiple records - must be overridden"""
        raise NotImplementedError

    def __init__(self, filename: Optional[str], stream: Optional[Any],
                 binary: bool = False, encoding: str = 'utf8',
                 noopen: bool = False) -> None:
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
            # Check if the file object is seekable before attempting to seek
            if hasattr(self.fobj, 'seekable') and not self.fobj.seekable():
                # Stream is not seekable (e.g., compressed files)
                # Cannot reset, just continue from current position
                pass
            else:
                self.fobj.seek(0)

    def close(self):
        """Close the file object if it's a file source"""
        if self.stype == SOURCE_TYPE_FILE:
            if self.fobj:
                try:
                    if hasattr(self.fobj, 'closed') and not self.fobj.closed:
                        self.fobj.close()
                    elif not hasattr(self.fobj, 'closed'):
                        # Some file-like objects don't have 'closed' attribute
                        self.fobj.close()
                except (AttributeError, OSError, IOError):
                    # File may already be closed or not closeable
                    pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures file is closed"""
        self.close()
        return False
