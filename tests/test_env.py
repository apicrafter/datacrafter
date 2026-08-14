"""Tests for ${VAR} interpolation in project YAML."""
import pytest

from datacrafter.cmds.project import load_config
from datacrafter.common.env import MissingEnvVarError, interpolate_env


def test_interpolate_required_and_default(monkeypatch):
    monkeypatch.setenv('MONGO_URI', 'mongodb://secret')
    data = interpolate_env({
        'connstr': '${MONGO_URI}',
        'token': '${MISSING_TOKEN:-dev}',
        'nested': ['${MONGO_URI}'],
    })
    assert data['connstr'] == 'mongodb://secret'
    assert data['token'] == 'dev'
    assert data['nested'] == ['mongodb://secret']


def test_missing_required_var():
    with pytest.raises(MissingEnvVarError) as exc_info:
        interpolate_env({'url': '${NOT_SET_IN_ENV}'}, environ={})
    assert 'NOT_SET_IN_ENV' in str(exc_info.value)


def test_load_config_interpolates(tmp_path, monkeypatch):
    monkeypatch.setenv('DATA_URL', 'https://example.com/a.csv')
    path = tmp_path / 'datacrafter.yml'
    path.write_text(
        'version: "1"\nproject-name: x\nextractor:\n  config:\n    url: ${DATA_URL}\n',
        encoding='utf8')
    loaded = load_config(str(path))
    assert loaded['extractor']['config']['url'] == 'https://example.com/a.csv'
