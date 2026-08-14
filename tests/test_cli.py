"""CLI tests for datacrafter commands."""
import os

import yaml
from typer.testing import CliRunner

from datacrafter.core import app

runner = CliRunner()


def _write_config(path, config):
    with open(os.path.join(path, 'datacrafter.yml'), 'w', encoding='utf8') as file_obj:
        yaml.safe_dump(config, file_obj)


class TestCli:
    def test_version(self):
        result = runner.invoke(app, ['version'])
        assert result.exit_code == 0
        assert 'datacrafter version' in result.stdout

    def test_init_and_check_incomplete(self, temp_dir):
        result = runner.invoke(app, ['init', '--path', temp_dir, '--name', 'demo'])
        assert result.exit_code == 0
        assert 'initialized' in result.stdout.lower()

        check = runner.invoke(app, ['check', '--path', temp_dir])
        assert check.exit_code == 1
        assert 'extractor' in check.stdout.lower()

    def test_init_positional_directory(self, temp_dir):
        project_dir = os.path.join(temp_dir, 'my-project')
        result = runner.invoke(app, ['init', project_dir])
        assert result.exit_code == 0
        config_path = os.path.join(project_dir, 'datacrafter.yml')
        assert os.path.exists(config_path)
        with open(config_path, encoding='utf8') as file_obj:
            config = yaml.safe_load(file_obj)
        assert config['project-name'] == 'my-project'

    def test_init_rejects_directory_and_path(self, temp_dir):
        result = runner.invoke(
            app, ['init', temp_dir, '--path', temp_dir])
        assert result.exit_code == 1
        assert 'not both' in result.stdout.lower()

    def test_check_valid_config(self, sample_project, sample_config):
        _write_config(sample_project.project_path, sample_config)
        result = runner.invoke(app, ['check', '--path', sample_project.project_path])
        assert result.exit_code == 0
        assert 'valid' in result.stdout.lower()

    def test_check_unknown_destination(self, sample_project, sample_config):
        sample_config['destination'] = {'type': 'redshift'}
        _write_config(sample_project.project_path, sample_config)
        result = runner.invoke(app, ['check', '--path', sample_project.project_path])
        assert result.exit_code == 1
        assert 'redshift' in result.stdout
        assert 'file-jsonl' in result.stdout

    def test_config_schema_lists_live_types(self):
        result = runner.invoke(app, ['config', 'schema'])
        assert result.exit_code == 0
        assert 'couchdb' in result.stdout
        assert 'file-jsonl' in result.stdout
        assert 'file-csv' in result.stdout
        assert 'rss' in result.stdout
        assert 'autoid' in result.stdout

    def test_config_validate_missing_file(self, temp_dir):
        result = runner.invoke(app, ['config', 'validate', '--path', temp_dir])
        assert result.exit_code == 1
        assert 'not found' in result.stdout.lower()

    def test_run_calls_project(self, sample_project, sample_config, monkeypatch):
        _write_config(sample_project.project_path, sample_config)
        called = {}

        def fake_run(self, structured_log=False):
            called['structured_log'] = structured_log

        monkeypatch.setattr('datacrafter.core.Project.run', fake_run)
        result = runner.invoke(
            app, ['run', '--path', sample_project.project_path])
        assert result.exit_code == 0
        assert 'structured_log' in called

    def test_status_reads_state(self, sample_project):
        import json
        state_path = os.path.join(sample_project.project_path, 'state.json')
        with open(state_path, 'w', encoding='utf8') as file_obj:
            json.dump({
                'stages': [
                    {'name': 'extractor', 'status': 'success', 'results': []},
                ]
            }, file_obj)
        result = runner.invoke(
            app, ['status', '--path', sample_project.project_path])
        assert result.exit_code == 0
        assert 'extractor' in result.stdout
        assert 'success' in result.stdout.lower() or 'completed' in result.stdout.lower()

    def test_config_validate_success(self, sample_project, sample_config):
        _write_config(sample_project.project_path, sample_config)
        result = runner.invoke(
            app, ['config', 'validate', '--path', sample_project.project_path])
        assert result.exit_code == 0
        assert 'valid' in result.stdout.lower()

    def test_log_missing_file(self, sample_project):
        result = runner.invoke(
            app, ['log', '--path', sample_project.project_path])
        assert result.exit_code == 0
        assert 'not found' in result.stdout.lower()

    def test_log_shows_recent_lines(self, sample_project):
        log_path = os.path.join(sample_project.project_path, 'datacrafter.log')
        with open(log_path, 'w', encoding='utf8') as file_obj:
            file_obj.write('first\nsecond\n')
        result = runner.invoke(
            app, ['log', '--path', sample_project.project_path, '--lines', '1'])
        assert result.exit_code == 0
        assert 'second' in result.stdout
        assert 'first' not in result.stdout

    def test_clean(self, sample_project):
        result = runner.invoke(
            app, ['clean', '--path', sample_project.project_path])
        assert result.exit_code == 0
        assert 'cleanup' in result.stdout.lower()

    def test_status_missing_state(self, temp_dir):
        result = runner.invoke(app, ['status', '--path', temp_dir])
        assert result.exit_code == 0
        assert 'no execution state' in result.stdout.lower()

    def test_unimplemented_commands(self):
        for command, token in [
            ('ui', 'ui'),
            ('builds', 'builds'),
            ('push', 'push'),
        ]:
            result = runner.invoke(app, [command])
            assert result.exit_code == 0
            assert 'not yet implemented' in result.stdout.lower()
            assert token in result.stdout.lower()

    def test_schema_and_metrics_from_output(self, sample_project):
        output = os.path.join(sample_project.project_path, 'output')
        os.makedirs(output, exist_ok=True)
        path = os.path.join(output, 'data.jsonl')
        with open(path, 'w', encoding='utf8') as file_obj:
            file_obj.write('{"age": "30", "name": "Ada"}\n')
            file_obj.write('{"age": "25", "name": "Bob"}\n')
        schema = runner.invoke(
            app, ['schema', '--path', sample_project.project_path])
        assert schema.exit_code == 0
        assert 'age' in schema.stdout
        assert 'int' in schema.stdout
        metrics = runner.invoke(
            app, ['metrics', '--path', sample_project.project_path])
        assert metrics.exit_code == 0
        assert 'records' in metrics.stdout
        assert '2' in metrics.stdout

    def test_schema_missing_jsonl(self, temp_dir):
        result = runner.invoke(app, ['schema', '--path', temp_dir])
        assert result.exit_code == 1
        assert 'jsonl' in result.stdout.lower()

    def test_dry_run_prints_plan(self, sample_project, sample_config):
        _write_config(sample_project.project_path, sample_config)
        output_before = os.listdir(
            os.path.join(sample_project.project_path, 'output'))
        result = runner.invoke(
            app, ['run', '--dry-run', '--path', sample_project.project_path])
        assert result.exit_code == 0
        assert 'file-jsonl' in result.stdout
        assert 'will_write' in result.stdout
        output_after = os.listdir(
            os.path.join(sample_project.project_path, 'output'))
        assert output_after == output_before

    def test_dry_run_lists_extractors(self, sample_project, sample_config):
        spec = sample_config.pop('extractor')
        second = dict(spec)
        second['name'] = 'two'
        second['config'] = {'url': 'https://example.com/two.csv'}
        spec['name'] = 'one'
        sample_config['extractors'] = [spec, second]
        _write_config(sample_project.project_path, sample_config)
        result = runner.invoke(
            app, ['run', '--dry-run', '--path', sample_project.project_path])
        assert result.exit_code == 0
        assert 'one' in result.stdout
        assert 'two' in result.stdout
        assert 'extractors' in result.stdout

    def test_run_quiet_and_validation_error(self, sample_project, sample_config):
        sample_config['destination'] = {'type': 'redshift'}
        _write_config(sample_project.project_path, sample_config)
        result = runner.invoke(
            app, ['run', '--quiet', '--path', sample_project.project_path])
        assert result.exit_code == 1
        assert 'validation failed' in result.stdout.lower()
