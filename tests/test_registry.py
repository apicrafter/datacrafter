"""Tests for the source/destination plugin registry."""
import pytest

from datacrafter._registry import (
    UnknownDestinationTypeError, UnknownSourceTypeError, get_destination_class,
    get_source_class, list_destinations, list_sources)


class TestRegistryPopulation:
    def test_all_sources_registered(self):
        names = list_sources()
        assert sorted(names) == [
            'bson', 'csv', 'json', 'jsonl', 'xls', 'xlsx', 'xml', 'zipxml']

    def test_all_destinations_registered(self):
        names = list_destinations()
        assert sorted(names) == [
            'arangodb', 'file-bson', 'file-csv', 'file-jsonl',
            'meilisearch', 'mongodb']

    def test_list_returns_sorted_names(self):
        # list_sources/list_destinations must return sorted names.
        assert list_sources() == sorted(list_sources())
        assert list_destinations() == sorted(list_destinations())


class TestRegistryLookup:
    def test_get_source_class_returns_registered_class(self):
        from datacrafter.sources.csv import CSVSource
        assert get_source_class('csv') is CSVSource

    def test_get_destination_class_returns_registered_class(self):
        from datacrafter.destinations.mongo import MongoDBDestination
        assert get_destination_class('mongodb') is MongoDBDestination

    def test_unknown_source_raises_typed_error_with_known_types(self):
        with pytest.raises(UnknownSourceTypeError) as exc_info:
            get_source_class('nonexistent')
        # Error message must list the registered types so the user can see options.
        msg = str(exc_info.value)
        assert 'nonexistent' in msg
        assert 'csv' in msg

    def test_unknown_destination_raises_typed_error_with_known_types(self):
        with pytest.raises(UnknownDestinationTypeError) as exc_info:
            get_destination_class('nonexistent')
        msg = str(exc_info.value)
        assert 'nonexistent' in msg
        assert 'mongodb' in msg


class TestFactoryIntegration:
    """The factory functions should raise the typed errors on unknown types."""

    def test_source_factory_raises_typed_error(self):
        from datacrafter.sources import get_source_from_file, UnknownSourceTypeError
        with pytest.raises(UnknownSourceTypeError):
            get_source_from_file('x.unknown', stype='doesnotexist')

    def test_destination_factory_raises_typed_error(self):
        from datacrafter.destinations import (
            get_destination_from_config, UnknownDestinationTypeError)
        with pytest.raises(UnknownDestinationTypeError):
            get_destination_from_config('/tmp', {'type': 'doesnotexist'})
