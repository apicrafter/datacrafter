#!/usr/bin/env python
"""The main entry point. Invoke as `datacrafter' or `python -m datacrafter`.

"""
import logging
import sys


def main():
    # Configure basic logging for startup errors
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARNING  # Only show warnings/errors during startup
    )
    
    try:
        from .core import cli
        cli()
    except KeyboardInterrupt:
        logging.warning("Ctrl-C pressed. Aborting")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
