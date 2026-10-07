import logging
from typing import Any, Iterator, Optional

SOURCE_TYPE_STREAM = 10
SOURCE_TYPE_FILE = 20


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

    def __init__(self, filename: Optional[str], stream: Optional[Any],
                 binary: bool = False, encoding: str = 'utf8',
                 noopen: bool = False) -> None:
        if filename is None and stream is None:
            raise ValueError(
                'Either filename or stream must be provided to open a source')
        self.filename = filename
        self.noopen = noopen
        # An explicit stream takes precedence over the filename and is owned
        # by this source: close() closes it.
        if stream is not None:
            self.stype = SOURCE_TYPE_STREAM
            self.fobj = stream
        else:
            self.stype = SOURCE_TYPE_FILE
            if not noopen:
                if binary:
                    self.fobj = open(filename or '', 'rb')
                else:
                    self.fobj = open(filename or '', 'r', encoding=encoding)
            else:
                self.fobj = None

    def reset(self):
        if self.fobj is None:
            return
        # Check if the file object is seekable before attempting to seek
        if hasattr(self.fobj, 'seekable') and not self.fobj.seekable():
            # Stream is not seekable (e.g., some compressed streams)
            # Cannot reset, just continue from current position
            return
        try:
            self.fobj.seek(0)
        except (OSError, ValueError):
            logging.debug('Cannot rewind source stream', exc_info=True)

    def close(self):
        """Close the file or stream owned by this source"""
        if self.fobj is None:
            return
        try:
            if getattr(self.fobj, 'closed', False):
                return
        except Exception:  # noqa: B011 - defensive probe of exotic streams
            pass
        try:
            self.fobj.close()
        except (AttributeError, OSError, IOError):
            # File may already be closed or not closeable
            logging.debug('Error closing source stream', exc_info=True)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures file is closed"""
        self.close()
        return False
