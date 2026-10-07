"""Single place to configure CLI logging.

This module is the only owner of root-logger handlers and levels: no other
module configures the root logger as an import side effect, and project
logging attaches its handlers without removing handlers installed by an
embedding application.
"""
import json
import logging
import sys
from logging.handlers import RotatingFileHandler

DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
PROJECT_LOG_FORMAT = (
    '%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')


def configure_logging(level=logging.INFO):
    """Configure the root logger once; later calls only adjust levels."""
    root = logging.getLogger()
    if root.handlers:
        root.setLevel(level)
        for handler in root.handlers:
            if handler.level > level:
                handler.setLevel(level)
        return
    logging.basicConfig(
        format=DEFAULT_LOG_FORMAT,
        level=level,
        force=False)


def set_log_level(level):
    """Set the root logger and every existing handler to ``level``."""
    root = logging.getLogger()
    root.setLevel(level)
    for handler in root.handlers:
        handler.setLevel(level)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def _is_ours(handler, kind):
    return getattr(handler, f'_datacrafter_{kind}', False)


class ConsoleHandler(logging.StreamHandler):
    """StreamHandler resolving ``sys.stderr`` at emit time.

    Capturing the stream at construction time would break when the stream is
    replaced and closed between invocations (e.g. CLI test runners).
    """

    def __init__(self):
        super().__init__(stream=sys.stderr)

    @property
    def stream(self):
        return sys.stderr

    @stream.setter
    def stream(self, _value):
        pass  # super().__init__ assignment; resolved dynamically instead


def enable_project_logging(logfile, console=True, tofile=False,
                           structured=False):
    """Attach project handlers to the root logger.

    Existing (external) handlers and an externally configured DEBUG level are
    preserved; our own handlers are tagged so repeated calls do not stack
    duplicates. A console handler is only added when no external handler is
    present, so an embedding application's handler stays the only sink.
    """
    root = logging.getLogger()
    current_level = root.getEffectiveLevel()
    root.setLevel(
        logging.DEBUG if current_level <= logging.DEBUG else logging.INFO)

    formatter = (
        JSONFormatter() if structured
        else logging.Formatter(PROJECT_LOG_FORMAT))

    if tofile and not any(_is_ours(h, 'file') for h in root.handlers):
        file_handler = RotatingFileHandler(
            logfile,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8',
        )
        file_handler.setLevel(logging.DEBUG)  # File gets all logs
        file_handler.setFormatter(formatter)
        file_handler._datacrafter_file = True  # noqa: B010 - tag, not API
        root.addHandler(file_handler)

    external = [
        handler for handler in root.handlers
        if not _is_ours(handler, 'file') and not _is_ours(handler, 'console')]
    if console and not external:
        console_handler = ConsoleHandler()
        console_handler.setLevel(
            logging.DEBUG if root.level <= logging.DEBUG else logging.INFO)
        console_handler.setFormatter(formatter)
        console_handler._datacrafter_console = True  # noqa: B010
        root.addHandler(console_handler)
