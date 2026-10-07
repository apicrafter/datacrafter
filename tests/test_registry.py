"""Tests for the source/destination/extractor plugin registry."""
import pytest

import datacrafter.destinations  # noqa: F401  populate registry
import datacrafter.extractors  # noqa: F401  populate registry
import datacrafter.sources  # noqa: F401  populate registry
from datacrafter._registry import (
    UnknownDestinationTypeError,
    UnknownExtractorTypeError,
    UnknownSourceTypeError,
    get_destination_class,
    get_extractor_class,
    get_source_class,
    list_destinations,
    list_extractors,
    list_sources,
)


class TestRegistryPopulation:
    def test_all_sources_registered(self):
        names = list_sources()
        assert sorted(names) == [
            'bson', 'csv', 'json', 'jsonl', 'xls', 'xlsx', 'xml', 'zipxml']

    def test_all_destinations_registered(self):
        names = list_destinations()
        assert sorted(names) == [
            'arangodb', 'couchdb', 'file-bson', 'file-csv', 'file-jsonl',
            'file-parquet', 'meilisearch', 'mongodb']

    def test_list_returns_sorted_names(self):
        # list_* helpers must return sorted names.
        assert list_sources() == sorted(list_sources())
        assert list_destinations() == sorted(list_destinations())
        assert list_extractors() == sorted(list_extractors())

    def test_all_extractors_registered(self):
        names = list_extractors()
        assert 'file-csv' in names
        assert 'api' in names
        assert 'code' in names
        assert 'rss' in names
        assert 'dcat' in names


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

    def test_get_extractor_class_returns_registered_class(self):
        from datacrafter.extractors.file import FileExtractor
        assert get_extractor_class('file-csv') is FileExtractor
        assert get_extractor_class('file-xlsx') is FileExtractor

    def test_unknown_extractor_raises_typed_error_with_known_types(self):
        with pytest.raises(UnknownExtractorTypeError) as exc_info:
            get_extractor_class('nonexistent')
        msg = str(exc_info.value)
        assert 'nonexistent' in msg
        assert 'file-csv' in msg


class TestFactoryIntegration:
    """The factory functions should raise the typed errors on unknown types."""

    def test_source_factory_raises_typed_error(self):
        from datacrafter.sources import UnknownSourceTypeError, get_source_from_file
        with pytest.raises(UnknownSourceTypeError):
            get_source_from_file('x.unknown', stype='doesnotexist')

    def test_xlsx_factory_defines_start_line_without_xls_branch(self, monkeypatch):
        """xlsx used to reference start_line only assigned in the xls branch."""
        from datacrafter._registry import get_source_class as real_get
        from datacrafter.sources import get_source_from_file
        captured = {}

        class FakeXLSX:
            # Plugins own their construction via from_config.
            @classmethod
            def from_config(cls, filename=None, stream=None, options=None):
                options = options or {}
                return cls(
                    filename=filename,
                    keys=options['keys'].split(','),
                    start_line=options.get('start_line', 0))

            def __init__(self, filename=None, keys=None, start_line=1):
                captured['start_line'] = start_line
                captured['keys'] = keys
                captured['filename'] = filename

        def fake_get(name):
            if name == 'xlsx':
                return FakeXLSX
            return real_get(name)

        monkeypatch.setattr('datacrafter.sources.get_source_class', fake_get)
        source = get_source_from_file(
            'book.xlsx', stype='xlsx', options={'keys': 'a,b'})
        assert isinstance(source, FakeXLSX)
        assert captured['start_line'] == 0
        assert captured['keys'] == ['a', 'b']

    def test_destination_factory_builds_couchdb(self, monkeypatch):
        from unittest import mock

        import datacrafter.destinations.couchdb as couch_mod
        from datacrafter.destinations import get_destination_from_config

        fake_pycouchdb = mock.MagicMock()
        with mock.patch.object(couch_mod, 'HAS_PYCOUCHDB', True), \
                mock.patch.object(couch_mod, 'pycouchdb', fake_pycouchdb):
            dest = get_destination_from_config('/tmp', {
                'type': 'couchdb',
                'connstr': 'http://localhost:5984',
                'dbname': 'db',
                'tablename': 'docs',
            })
        assert dest.id() == 'couchdb'

    def test_destination_factory_builds_meilisearch(self, monkeypatch):
        from unittest import mock

        import datacrafter.destinations.meilisearch as mei_mod
        from datacrafter.destinations import get_destination_from_config

        fake_client = mock.MagicMock()
        fake_mod = mock.MagicMock()
        fake_mod.Client.return_value = fake_client
        with mock.patch.object(mei_mod, 'HAS_MEILISEARCH', True), \
                mock.patch.object(mei_mod, 'meilisearch', fake_mod):
            dest = get_destination_from_config('/tmp', {
                'type': 'meilisearch',
                'connstr': 'http://localhost:7700',
                'indexname': 'docs',
                'token': 'secret',
            })
        assert dest.id() == 'meilisearch'

    def test_destination_factory_requires_type(self):
        from datacrafter.destinations import (
            UnknownDestinationTypeError,
            get_destination_from_config,
        )
        with pytest.raises(UnknownDestinationTypeError):
            get_destination_from_config('/tmp', {'fileprefix': 'out'})

    def test_extractor_factory_builds_file_csv(self, sample_project):
        from datacrafter.extractors import get_extractor
        from datacrafter.extractors.file import FileExtractor
        sample_project.project['extractor'] = {
            'mode': 'singlefile',
            'type': 'file-csv',
            'method': 'url',
            'config': {'url': 'https://example.com/data.csv'},
        }
        extractor = get_extractor(sample_project)
        assert isinstance(extractor, FileExtractor)

    def test_extractor_factory_raises_typed_error(self, sample_project):
        from datacrafter.extractors import UnknownExtractorTypeError, get_extractor
        sample_project.project['extractor'] = {
            'mode': 'singlefile',
            'type': 'doesnotexist',
            'method': 'url',
            'config': {'url': 'https://example.com/data.csv'},
        }
        with pytest.raises(UnknownExtractorTypeError):
            get_extractor(sample_project)


class TestPluginContract:
    """from_config contract: new plugins need zero factory edits."""

    def test_new_source_plugin_constructible_without_factory_edit(self, tmp_path):
        from datacrafter._registry import _SOURCE_REGISTRY, register_source
        from datacrafter.sources import get_source_from_file

        @register_source("fake-cfg")
        class FakeCfgSource:
            COMPRESSION_MODE = 'text'

            @classmethod
            def from_config(cls, filename=None, stream=None, options=None):
                return cls(filename, (options or {}).get('greeting'))

            def __init__(self, filename, greeting):
                self.filename = filename
                self.greeting = greeting

        try:
            path = tmp_path / 'data.fakecfg'
            path.write_text('x')
            source = get_source_from_file(
                str(path), stype='fake-cfg', options={'greeting': 'hi'})
            assert isinstance(source, FakeCfgSource)
            assert source.greeting == 'hi'
        finally:
            _SOURCE_REGISTRY.pop('fake-cfg', None)

    def test_new_destination_plugin_constructible_without_factory_edit(self, tmp_path):
        from datacrafter._registry import _DESTINATION_REGISTRY, register_destination
        from datacrafter.destinations import get_destination_from_config
        from datacrafter.destinations.base import BaseFileDestination

        @register_destination("file-fake")
        class FakeDestination(BaseFileDestination):
            FILE_EXTENSION = 'fake'

            def id(self):
                return 'fake'

            def write(self, record):
                pass

        try:
            dest = get_destination_from_config(
                str(tmp_path), {'type': 'file-fake', 'fileprefix': 'out'})
            assert isinstance(dest, FakeDestination)
            assert dest._filename.endswith('out.fake')
            dest.close()
        finally:
            _DESTINATION_REGISTRY.pop('file-fake', None)

    def test_extractor_run_is_a_template_method(self, sample_project, monkeypatch):
        """run() drives validate/reset/_execute/commit exactly once."""
        from datacrafter.extractors import get_extractor

        calls = []
        sample_project.project['extractor'] = {
            'mode': 'singlefile', 'type': 'file-csv', 'method': 'url',
            'config': {'url': 'https://example.com/x.csv'}}
        extractor = get_extractor(sample_project)
        monkeypatch.setattr(
            extractor, 'validate', lambda: calls.append('validate'))
        monkeypatch.setattr(
            extractor, '_execute', lambda: calls.append('execute')
            or extractor.results.extend(
                [{'filename': 'x.csv', 'compressed': False, 'type': 'file'}]))
        extractor.run(update_state=False)
        assert calls == ['validate', 'execute']
        # commit derived a success status from results
        assert extractor.results[0]['filename'] == 'x.csv'
