"""Tests for extractor classes"""
import os

import pytest

from datacrafter.common.state import ProjectState
from datacrafter.extractors import get_extractor
from datacrafter.extractors.base import BaseExtractor, DataCrafterConfigurationError


class TestBaseExtractor:
    """Tests for BaseExtractor"""
    
    def test_validate_missing_project(self, sample_config):
        """Test validation fails without project"""
        # Create extractor without project
        class MockProject:
            def __init__(self):
                self.project = sample_config
        
        project = MockProject()
        project.project['extractor'] = {
            'mode': 'singlefile',
            'type': 'file-csv',
            'method': 'url',
            'force': True,
            'config': {}
        }
        
        extractor = BaseExtractor(project)
        extractor.project = None  # Remove project to test validation
        
        with pytest.raises(DataCrafterConfigurationError):
            extractor.validate()
    
    def test_validate_missing_url(self, sample_project):
        """Test validation fails without URL for url method"""
        # Modify project config to have url method without url
        sample_project.project['extractor'] = {
            'mode': 'singlefile', 'type': 'file-csv', 'method': 'url', 'config': {}}
        extractor = BaseExtractor(sample_project)

        with pytest.raises(DataCrafterConfigurationError) as exc_info:
            extractor.validate()

        assert 'url' in str(exc_info.value).lower()

    def test_validate_urlbypattern_missing_keys(self, sample_project):
        """Test validation fails without required keys for urlbypattern"""
        # Modify project config
        sample_project.project['extractor'] = {
            'mode': 'singlefile', 'type': 'file-csv',
            'method': 'urlbypattern', 'config': {}}
        
        extractor = BaseExtractor(sample_project)
        
        with pytest.raises(DataCrafterConfigurationError) as exc_info:
            extractor.validate()
        
        error_msg = str(exc_info.value).lower()
        assert 'prefix' in error_msg or 'data_prefix' in error_msg

    def test_run_url_downloads_into_current(self, sample_project, monkeypatch):
        sample_project.project['extractor'] = {
            'mode': 'singlefile',
            'type': 'file-csv',
            'method': 'url',
            'force': True,
            'config': {'url': 'https://example.com/data.csv'},
        }
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)

        def fake_get_file(url, pathname, **_kwargs):
            with open(pathname, 'w', encoding='utf8') as file_obj:
                file_obj.write('id,name\n1,a\n')
            return True

        monkeypatch.setattr(
            'datacrafter.extractors.base.get_file', fake_get_file)
        extractor = get_extractor(sample_project)
        extractor.run()
        assert extractor.results
        assert extractor.results[0]['filename'].endswith('data.csv')
        assert sample_project.state.last_stage == 'extractor'
        assert sample_project.state.stages[-1]['status'] == 'success'

    def test_run_urlbypattern_uses_collector(self, sample_project, monkeypatch):
        sample_project.project['extractor'] = {
            'mode': 'singlefile',
            'type': 'file-csv',
            'method': 'urlbypattern',
            'force': True,
            'config': {
                'prefix': 'https://example.com/',
                'data_prefix': 'data-',
            },
        }
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)

        def fake_pattern(*_args, **_kwargs):
            return True

        monkeypatch.setattr(
            'datacrafter.extractors.base.get_file_by_pattern', fake_pattern)
        extractor = get_extractor(sample_project)
        extractor.run()
        assert extractor.results
        assert extractor.results[0]['filename'].endswith('data.csv')

    def test_run_code_script_under_project(self, sample_project):
        script = os.path.join(sample_project.project_path, 'collect.py')
        with open(script, 'w', encoding='utf8') as file_obj:
            file_obj.write(
                'def collect(config):\n'
                '    return [{"filename": "current/data.jsonl", "type": "file"}]\n'
            )
        sample_project.project['extractor'] = {
            'mode': 'code',
            'type': 'code',
            'method': 'url',
            'config': {'script': 'collect.py'},
        }
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)
        extractor = get_extractor(sample_project)
        extractor.run()
        assert extractor.results[0]['filename'] == 'current/data.jsonl'
        assert sample_project.state.stages[-1]['status'] == 'success'

    def test_run_rss_feed(self, sample_project, monkeypatch):
        feed = (
            '<?xml version="1.0"?><rss><channel>'
            '<item><title>A</title><link>https://example.com/a</link></item>'
            '</channel></rss>'
        )

        def fake_get(url, pathname, **_kwargs):
            os.makedirs(os.path.dirname(pathname), exist_ok=True)
            with open(pathname, 'w', encoding='utf8') as file_obj:
                file_obj.write(feed)
            return True

        monkeypatch.setattr('datacrafter.extractors.feeds.get_file', fake_get)
        sample_project.project['extractor'] = {
            'type': 'rss',
            'config': {'url': 'https://example.com/feed.xml'},
        }
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)
        extractor = get_extractor(sample_project)
        extractor.run()
        assert extractor.results
        assert extractor.results[0]['filename'].endswith('data.jsonl')

    def test_collect_extractors_list(self, sample_project, monkeypatch):

        written = []

        def fake_get(url, pathname, **_kwargs):
            os.makedirs(os.path.dirname(pathname), exist_ok=True)
            with open(pathname, 'w', encoding='utf8') as file_obj:
                file_obj.write('id,name\n1,a\n')
            written.append(pathname)
            return True

        monkeypatch.setattr('datacrafter.extractors.base.get_file', fake_get)
        sample_project.project['extractors'] = [
            {
                'name': 'one',
                'mode': 'singlefile',
                'type': 'file-csv',
                'method': 'url',
                'config': {'url': 'https://example.com/one.csv'},
            },
            {
                'name': 'two',
                'mode': 'singlefile',
                'type': 'file-csv',
                'method': 'url',
                'config': {'url': 'https://example.com/two.csv'},
            },
        ]
        sample_project.project.pop('extractor', None)
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)
        sample_project.collect()
        names = [os.path.basename(r['filename']) for r in sample_project.state.stages[-1]['results']]
        assert 'one.csv' in names
        assert 'two.csv' in names

    def test_run_dcat_catalog(self, sample_project, monkeypatch):
        catalog = {
            'dataset': [{
                'title': 'Roads',
                'distribution': [{
                    'downloadURL': 'https://example.com/roads.csv',
                    'format': 'CSV',
                }],
            }]
        }

        def fake_get(url, pathname, **_kwargs):
            os.makedirs(os.path.dirname(pathname), exist_ok=True)
            with open(pathname, 'w', encoding='utf8') as file_obj:
                import json
                json.dump(catalog, file_obj)
            return True

        monkeypatch.setattr('datacrafter.extractors.feeds.get_file', fake_get)
        sample_project.project['extractor'] = {
            'type': 'dcat',
            'config': {'url': 'https://example.com/data.json'},
        }
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)
        extractor = get_extractor(sample_project)
        extractor.run()
        assert extractor.results
        assert extractor.results[0]['filename'].endswith('data.jsonl')

    def test_run_api_missing_package(self, sample_project, monkeypatch):
        monkeypatch.setattr(
            'datacrafter.extractors.base.HAS_APIBACKUPER', False)
        sample_project.project['extractor'] = {
            'mode': 'api',
            'type': 'api',
            'method': 'apibackuper',
            'config': {},
        }
        extractor = get_extractor(sample_project)
        with pytest.raises(ImportError, match='apibackuper'):
            extractor.run()

    def test_run_api_missing_config_file(self, sample_project, monkeypatch):
        monkeypatch.setattr(
            'datacrafter.extractors.base.HAS_APIBACKUPER', True)
        sample_project.project['extractor'] = {
            'mode': 'api',
            'type': 'api',
            'method': 'apibackuper',
            'config': {},
        }
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)
        extractor = get_extractor(sample_project)
        extractor.run()
        assert extractor.results == []
        assert sample_project.state.stages[-1]['status'] == 'fail'

    def test_run_api_mocked_builder(self, sample_project, monkeypatch):
        monkeypatch.setattr(
            'datacrafter.extractors.base.HAS_APIBACKUPER', True)
        os.makedirs(sample_project.storage, exist_ok=True)
        with open(
                os.path.join(sample_project.storage, 'apibackuper.cfg'),
                'w', encoding='utf8') as file_obj:
            file_obj.write('[project]\n')
        with open(
                os.path.join(sample_project.storage, 'params.json'),
                'w', encoding='utf8') as file_obj:
            file_obj.write('{}\n')

        class FakeBuilder:
            def __init__(self, path):
                self.path = path
                self.storagedir = os.path.join(path, 'storage')
                os.makedirs(self.storagedir, exist_ok=True)
                self.followed = False

            def run(self, mode=None):
                self.mode = mode

            def follow(self, mode=None):
                self.followed = True

            def export(self, format=None, filename=None):
                with open(filename, 'w', encoding='utf8') as file_obj:
                    file_obj.write('{"id": 1}\n')

        monkeypatch.setattr(
            'datacrafter.extractors.base.ProjectBuilder', FakeBuilder)
        sample_project.project['extractor'] = {
            'mode': 'api',
            'type': 'api',
            'method': 'apibackuper',
            'force': True,
            'config': {'follow': True},
        }
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)
        extractor = get_extractor(sample_project)
        extractor.run()
        assert extractor.results[0]['filename'].endswith('data.jsonl')
        assert sample_project.state.stages[-1]['status'] == 'success'

