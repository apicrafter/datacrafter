"""Single place to configure CLI logging."""
import logging

DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


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
