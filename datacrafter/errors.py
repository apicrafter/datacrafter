"""Package-wide exception hierarchy.

Every public datacrafter exception derives from :class:`DataCrafterError` so
callers can catch package failures with a single type. This module has no
dependencies so importing the base never drags in CLI or registry code.
"""


class DataCrafterError(Exception):
    """Root of all public datacrafter exceptions."""


class DestinationWriteError(DataCrafterError):
    """Raised when writing, flushing, or finalizing a destination fails."""
