#!/usr/bin/env python
"""The main entry point. Invoke as `datacrafter' or `python -m datacrafter`.

"""
import logging
import sys

from .common.logconfig import configure_logging


def main():
    """Main entry point for datacrafter CLI."""
    configure_logging(logging.WARNING)

    try:
        from .core import cli  # pylint: disable=import-outside-toplevel
        cli()
    except KeyboardInterrupt:
        logging.warning("Ctrl-C pressed. Aborting")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as error:
        logging.error("Fatal error: %s", error, exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
