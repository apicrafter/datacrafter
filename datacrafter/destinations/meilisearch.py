import meilisearch
import uuid
import logging

from .base import BaseSearchDestination


class MeilisearchDestination(BaseSearchDestination):
    """Meilisearch Destination"""
    def __init__(self, connstr, indexname, token, reset=False, incremental=True):
        """Init destination"""
        super(MeilisearchDestination, self).__init__(connstr, indexname, token, reset, incremental)
        self.client = meilisearch.Client(connstr, token)
        self.sindex = self.client.index(self.indexname)
        self.incremental = incremental
        self.docid = 0
        if reset:
            logging.debug('Pruning all documents from index %s' % (self.indexname))
            self.sindex.delete_all_documents()
        pass


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
        if 'id' not in record.keys():
            record['id'] = self.getdocid()
        self.sindex.add_documents([record,])

    def write_bulk(self, records):
        """Write bulk"""
        documents = []
        for r in records:
            if 'id' not in r.keys():
                r['id'] = self.getdocid()
            documents.append(r)
        self.sindex.add_documents(documents)
