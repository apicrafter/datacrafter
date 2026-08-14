"""Parquet file destination (optional pyarrow)."""
import logging

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    HAS_PYARROW = True
except ImportError:
    HAS_PYARROW = False
    pa = None
    pq = None

from .._registry import register_destination
from .base import BaseDestination


@register_destination("file-parquet")
class ParquetDestination(BaseDestination):
    """Buffer records and write a Parquet file on close."""

    def __init__(self, filename, compression=None):
        if not HAS_PYARROW:
            raise ImportError(
                "pyarrow is required for file-parquet. "
                "Install it with: pip install 'datacrafter[parquet]' or pip install pyarrow"
            )
        self.filename = filename
        self._filename = filename
        self.compression = compression
        self._rows = []
        self._closed = False
        logging.info('Parquet destination %s', filename)

    def id(self):
        return 'parquet'

    def write(self, record):
        self._rows.append(dict(record) if isinstance(record, dict) else record)

    def write_bulk(self, records):
        for record in records:
            self.write(record)

    def close(self):
        if self._closed:
            return
        table = pa.Table.from_pylist(self._rows) if self._rows else pa.table({})
        pq.write_table(table, self.filename, compression=self.compression)
        self._closed = True
        logging.info('Wrote %s parquet rows to %s', len(self._rows), self.filename)
