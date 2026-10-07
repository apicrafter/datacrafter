"""Meilisearch destination module."""
import logging
import uuid

try:
    import meilisearch
    HAS_MEILISEARCH = True
except ImportError:
    HAS_MEILISEARCH = False
    meilisearch = None  # type: ignore[assignment]

from .._registry import register_destination
from .base import BaseSearchDestination


@register_destination("meilisearch")
class MeilisearchDestination(BaseSearchDestination):
    """Meilisearch Destination"""

    @classmethod
    def from_config(cls, dirpath, options):
        from .base import get_option_value
        return cls(
            connstr=get_option_value(
                options, 'connstr', 'https://127.0.0.1:7700'),
            indexname=get_option_value(options, 'indexname', ''),
            token=get_option_value(options, 'token', ''),
            reset=get_option_value(options, 'reset', False),
            incremental=get_option_value(options, 'incremental', True))

    def __init__(self, connstr, indexname, token, reset=False, incremental=True):
        """Init destination"""
        if not HAS_MEILISEARCH:
            raise ImportError(
                "meilisearch is required for MeilisearchDestination. "
                "Install it with: pip install meilisearch"
            )
        super().__init__(connstr, indexname, token, reset, incremental)
        self.client = meilisearch.Client(connstr, token)
        self.sindex = self.client.index(self.indexname)
        self.incremental = incremental
        self.docid = 0
        if reset:
            logging.debug('Pruning all documents from index %s', self.indexname)
            self.sindex.delete_all_documents()

    def close(self):
        """Close Meilisearch client connection."""
        # Meilisearch client doesn't have explicit close method,
        # but we can clean up references
        self.client = None
        self.sindex = None

    def getdocid(self):
        """Returns unique document id"""
        if self.incremental:
            self.docid += 1
            return self.docid
        return str(uuid.uuid1())

    def id(self):
        """Return destination identifier"""
        return 'meilisearch'

    def write(self, record):
        """Write single record"""
        if 'id' not in record:
            record['id'] = self.getdocid()
        self.sindex.add_documents([record])

    def write_bulk(self, records):
        """Write bulk"""
        documents = []
        for record in records:
            if 'id' not in record:
                record['id'] = self.getdocid()
            documents.append(record)
        self.sindex.add_documents(documents)
