"""Mock-based tests for the database/search destinations.

These tests exercise the write paths of MongoDB, ArangoDB, CouchDB, and
Meilisearch destinations WITHOUT requiring live services. The driver clients
are mocked, so no network/DB connection is made.
"""
from unittest import mock

import pytest

from datacrafter.destinations.mongo import MongoDBDestination
from datacrafter.destinations.arango import ArangoDBDestination
from datacrafter.destinations.couchdb import CouchDBDestination
from datacrafter.destinations.meilisearch import MeilisearchDestination

pytestmark = pytest.mark.backend


class TestMongoDBDestination:
    """MongoDB destination write path, mocked."""

    def _make(self):
        """Create a MongoDBDestination with a mocked pymongo client.

        Returns (destination, mock_collection).
        """
        mock_client = mock.MagicMock()
        mock_coll = mock_client["testdb"]["testcoll"]
        with mock.patch("datacrafter.destinations.mongo.MongoClient",
                        return_value=mock_client) as client_cls:
            dest = MongoDBDestination("mongodb://localhost", "testdb", "testcoll")
            client_cls.assert_called_once_with("mongodb://localhost")
        return dest, mock_coll

    def test_write_inserts_single_record(self):
        dest, coll = self._make()
        record = {"name": "alice", "age": 30}
        dest.write(record)
        coll.insert_one.assert_called_once_with(record)

    def test_write_bulk_inserts_many(self):
        dest, coll = self._make()
        records = [{"i": 1}, {"i": 2}, {"i": 3}]
        dest.write_bulk(records)
        coll.insert_many.assert_called_once_with(records)

    def test_close_closes_client(self):
        dest, _ = self._make()
        dest.close()
        dest.client.close.assert_called_once()

    def test_id_is_mongodb(self):
        dest, _ = self._make()
        assert dest.id() == 'mongodb'


class TestArangoDBDestination:
    """ArangoDB destination write path, mocked.

    python-arango is an optional dependency; when it is not installed the module
    sets ``HAS_ARANGO=False``. We patch both the ``HAS_ARANGO`` flag and the
    ``ArangoClient`` symbol so the destination can be constructed and its write
    path exercised without the real driver or a live ArangoDB.
    """

    def _make(self):
        import datacrafter.destinations.arango as arango_mod
        mock_client = mock.MagicMock()
        mock_coll = mock_client.db("testdb", "u", "p").collection("testcoll")
        with mock.patch.object(arango_mod, "HAS_ARANGO", True), \
                mock.patch.object(arango_mod, "ArangoClient",
                                  return_value=mock_client):
            dest = ArangoDBDestination("http://localhost:8529", "testdb",
                                       "testcoll", username="u", password="p")
        return dest, mock_coll

    def test_write_inserts_single_record(self):
        dest, coll = self._make()
        record = {"name": "alice"}
        dest.write(record)
        coll.insert.assert_called_once_with(record)

    def test_write_bulk_inserts_many(self):
        dest, coll = self._make()
        records = [{"i": 1}, {"i": 2}]
        dest.write_bulk(records)
        coll.insert_many.assert_called_once_with(records)

    def test_id_is_arango(self):
        dest, _ = self._make()
        assert dest.id() == 'arango'


class TestCouchDBDestination:
    """CouchDB destination write path, mocked."""

    def _make(self):
        import datacrafter.destinations.couchdb as couch_mod
        mock_server = mock.MagicMock()
        mock_db = mock_server.database("testdb")
        # pycouchdb is optional; patch the HAS_ flag and the pycouchdb module
        # symbol together so construction works without the real driver.
        fake_pycouchdb = mock.MagicMock()
        fake_pycouchdb.Server.return_value = mock_server
        with mock.patch.object(couch_mod, "HAS_PYCOUCHDB", True), \
                mock.patch.object(couch_mod, "pycouchdb", fake_pycouchdb):
            dest = CouchDBDestination("http://localhost:5984", "testdb", "testcoll")
        return dest, mock_db

    def test_write_saves_single_record(self):
        dest, db = self._make()
        record = {"name": "alice"}
        dest.write(record)
        db.save.assert_called_once_with(record)

    def test_write_bulk_saves_each_record(self):
        dest, db = self._make()
        records = [{"i": 1}, {"i": 2}, {"i": 3}]
        dest.write_bulk(records)
        assert db.save.call_count == 3
        for rec in records:
            db.save.assert_any_call(rec)

    def test_id_is_couchdb(self):
        dest, _ = self._make()
        assert dest.id() == 'couchdb'


class TestMeilisearchDestination:
    """Meilisearch destination write path, mocked."""

    def _make(self):
        """Create a MeilisearchDestination with a mocked meilisearch.Client.

        The destination calls ``meilisearch.Client(connstr, token)``; we patch the
        package-level ``Client`` attribute so no network call is made.
        """
        import datacrafter.destinations.meilisearch as ms_mod
        mock_client = mock.MagicMock()
        mock_index = mock_client.index("testindex")
        with mock.patch.object(ms_mod, "meilisearch") as pkg:
            pkg.Client.return_value = mock_client
            dest = MeilisearchDestination("http://localhost:7700", "testindex",
                                          token="key")
        return dest, mock_index

    @pytest.mark.skipif(
        not __import__("datacrafter.destinations.meilisearch",
                       fromlist=["x"]).HAS_MEILISEARCH,
        reason="meilisearch not installed")
    def test_write_adds_single_document(self):
        dest, index = self._make()
        record = {"id": "1", "title": "doc"}
        dest.write(record)
        index.add_documents.assert_called_once_with([record])

    @pytest.mark.skipif(
        not __import__("datacrafter.destinations.meilisearch",
                       fromlist=["x"]).HAS_MEILISEARCH,
        reason="meilisearch not installed")
    def test_write_assigns_id_when_missing(self):
        dest, index = self._make()
        # No 'id' key: the destination MUST assign one before adding.
        dest.write({"title": "doc"})
        called_args = index.add_documents.call_args[0][0]
        assert called_args[0]["title"] == "doc"
        assert "id" in called_args[0]

    @pytest.mark.skipif(
        not __import__("datacrafter.destinations.meilisearch",
                       fromlist=["x"]).HAS_MEILISEARCH,
        reason="meilisearch not installed")
    def test_write_bulk_adds_documents(self):
        dest, index = self._make()
        records = [{"id": "1"}, {"id": "2"}]
        dest.write_bulk(records)
        index.add_documents.assert_called_once_with(records)

    @pytest.mark.skipif(
        not __import__("datacrafter.destinations.meilisearch",
                       fromlist=["x"]).HAS_MEILISEARCH,
        reason="meilisearch not installed")
    def test_id_is_meilisearch(self):
        dest, _ = self._make()
        assert dest.id() == 'meilisearch'
