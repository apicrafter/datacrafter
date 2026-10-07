"""Tests for Project-independent processor construction and config loading."""
import os

import pytest

from datacrafter.common.projectconfig import load_config
from datacrafter.processors.base import CommonProcessor, ProcessorConfig
from tests.conftest import RecordingDestination


@pytest.fixture
def standalone_processor(tmp_path):
    """Processor built from ProcessorConfig + explicit paths only."""
    config = ProcessorConfig(autoid=True, autoid_fields=['code'])
    return CommonProcessor(
        config, project_path=str(tmp_path), output=str(tmp_path / 'output'),
        state=None)


class TestStandaloneProcessor:
    def test_runs_without_project_instance(
            self, standalone_processor, tmp_path, jsonl_file):
        from datacrafter.sources import get_source_from_file
        source = get_source_from_file(jsonl_file)
        dest = RecordingDestination()
        standalone_processor.run(
            source, dest, buffer_size=1, show_progress=False)
        assert standalone_processor.stats['total_records'] == 3
        assert dest.records
        assert standalone_processor.project is None

    def test_autoid_applied_without_project(self, standalone_processor, tmp_path):
        dest = RecordingDestination()
        standalone_processor.run(
            [{'code': 'x'}], dest, buffer_size=1, show_progress=False)
        assert '_id' in dest.records[0]

    def test_config_normalization_in_dataclass(self):
        config = ProcessorConfig.from_project_config({
            'config': {'autoid': True, 'autoid_fields': 'a, b'}})
        assert config.autoid is True
        assert config.autoid_fields == 'a, b'
        # Attribute-level normalization still happens in the processor
        processor = CommonProcessor(config)
        assert processor.autoid_fields == ['a', 'b']

    def test_from_project_config_ignores_unknown_keys(self):
        config = ProcessorConfig.from_project_config({
            'config': {'autoid': True, 'future_option': 1},
            'keymap': {'type': 'names', 'fields': {'a': 'b'}},
        })
        assert config.autoid is True
        assert not hasattr(config, 'future_option')
        assert config.keymap == {'type': 'names', 'fields': {'a': 'b'}}

    def test_from_empty_section_gives_defaults(self):
        config = ProcessorConfig.from_project_config(None)
        assert config.autoid is False
        assert config.error_strategy == 'skip'
        assert config.max_retries == 3


class TestConfigLoaderModule:
    def test_load_config_applies_env_interpolation(self, tmp_path, monkeypatch):
        monkeypatch.setenv('DC_TEST_URI', 'mongodb://remote:27017')
        path = tmp_path / 'datacrafter.yml'
        path.write_text(
            'destination:\n  connstr: ${DC_TEST_URI}\n', encoding='utf8')
        config = load_config(str(path))
        assert config['destination']['connstr'] == 'mongodb://remote:27017'

    def test_load_config_missing_var_raises(self, tmp_path):
        path = tmp_path / 'datacrafter.yml'
        path.write_text('a: ${DC_DEFINITELY_UNSET_VAR}\n', encoding='utf8')
        from datacrafter.common.env import MissingEnvVarError
        with pytest.raises(MissingEnvVarError, match='DC_DEFINITELY_UNSET_VAR'):
            load_config(str(path))

    def test_load_config_empty_file(self, tmp_path):
        path = tmp_path / 'datacrafter.yml'
        path.write_text('', encoding='utf8')
        assert load_config(str(path)) == {}

    def test_project_reexports_load_config(self):
        from datacrafter.cmds.project import load_config as project_loader
        assert project_loader is load_config
