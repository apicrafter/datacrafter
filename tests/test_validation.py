"""Tests for datacrafter.yml validation and environment preflight."""

from datacrafter.common.validation import check_environment, validate_config


def _valid_config():
    return {
        'version': '1',
        'project-name': 'test-project',
        'extractor': {
            'mode': 'singlefile',
            'type': 'file-csv',
            'method': 'url',
            'config': {'url': 'https://example.com/data.csv'},
        },
        'destination': {
            'type': 'file-jsonl',
            'fileprefix': 'output',
        },
    }


class TestValidateConfig:
    def test_valid_minimal_config(self):
        ok, errors = validate_config(_valid_config())
        assert ok is True
        assert errors == []

    def test_missing_extractor(self):
        ok, errors = validate_config({
            'version': '1', 'project-name': 'x'})
        assert ok is False
        assert any("extractor" in e for e in errors)

    def test_extractors_list_validates(self):
        config = _valid_config()
        spec = config.pop('extractor')
        spec2 = dict(spec)
        spec2['name'] = 'second'
        config['extractors'] = [spec, spec2]
        ok, errors = validate_config(config)
        assert ok is True, errors

    def test_rss_extractor_requires_url(self):
        config = _valid_config()
        config['extractor'] = {
            'mode': 'singlefile', 'type': 'rss', 'config': {}}
        ok, errors = validate_config(config)
        assert ok is False
        assert any('url' in e for e in errors)

    def test_unknown_destination_lists_registered_types(self):
        config = _valid_config()
        config['destination'] = {'type': 'doesnotexist'}
        ok, errors = validate_config(config)
        assert ok is False
        joined = ' '.join(errors)
        assert 'doesnotexist' in joined
        assert 'file-jsonl' in joined
        assert 'couchdb' in joined

    def test_file_destination_requires_fileprefix(self):
        config = _valid_config()
        config['destination'] = {'type': 'file-jsonl'}
        ok, errors = validate_config(config)
        assert ok is False
        assert any('fileprefix' in e for e in errors)

    def test_unknown_extractor_type(self):
        config = _valid_config()
        config['extractor']['type'] = 'file-parquet'
        ok, errors = validate_config(config)
        assert ok is False
        assert any('file-parquet' in e for e in errors)

    def test_url_method_requires_url(self):
        config = _valid_config()
        config['extractor']['config'] = {}
        ok, errors = validate_config(config)
        assert ok is False
        assert any('config.url' in e for e in errors)

    def test_unknown_error_strategy(self):
        config = _valid_config()
        config['processor'] = {'config': {'error_strategy': 'ignore'}}
        ok, errors = validate_config(config)
        assert ok is False
        assert any('error_strategy' in e for e in errors)

    def test_couchdb_destination_is_known(self):
        config = _valid_config()
        config['destination'] = {
            'type': 'couchdb',
            'connstr': 'http://localhost:5984',
            'dbname': 'db',
        }
        ok, errors = validate_config(config)
        assert ok is True, errors

    def test_code_extractor_requires_script(self):
        config = _valid_config()
        config['extractor'] = {
            'mode': 'code',
            'type': 'code',
            'config': {},
        }
        ok, errors = validate_config(config)
        assert ok is False
        assert any('script' in e for e in errors)

    def test_keymap_names_requires_fields(self):
        config = _valid_config()
        config['processor'] = {'keymap': {'type': 'names'}}
        ok, errors = validate_config(config)
        assert ok is False
        assert any('fields' in e for e in errors)

    def test_custom_processor_requires_code(self):
        config = _valid_config()
        config['processor'] = {'custom': {'type': 'script'}}
        ok, errors = validate_config(config)
        assert ok is False
        assert any('code' in e for e in errors)

    def test_unknown_processor_source_type(self):
        config = _valid_config()
        config['processor'] = {'config': {'type': 'redshift'}}
        ok, errors = validate_config(config)
        assert ok is False
        assert any('redshift' in e for e in errors)


class TestCheckEnvironment:
    def test_missing_project_dirs(self, temp_dir):
        issues = check_environment(_valid_config(), temp_dir)
        assert any("current/" in i for i in issues)

    def test_init_project_has_dirs(self, sample_project):
        issues = check_environment(_valid_config(), sample_project.project_path)
        assert not any("Missing project directory" in i for i in issues)

    def test_optional_destination_package_flag(self, monkeypatch):
        config = _valid_config()
        config['destination'] = {'type': 'file-parquet', 'fileprefix': 'out'}
        monkeypatch.setattr(
            'datacrafter.destinations.parquet.HAS_PYARROW', False)
        issues = check_environment(config)
        assert any('pyarrow' in i for i in issues)

    def test_apibackuper_package_flag(self, monkeypatch):
        config = _valid_config()
        config['extractor'] = {
            'mode': 'api',
            'type': 'api',
            'method': 'apibackuper',
            'config': {},
        }
        monkeypatch.setattr(
            'datacrafter.extractors.base.HAS_APIBACKUPER', False)
        issues = check_environment(config)
        assert any('apibackuper' in i for i in issues)
