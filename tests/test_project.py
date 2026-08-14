"""Tests for Project class"""
import os
import yaml
import pytest

from datacrafter.cmds.project import Project
from datacrafter.extractors.base import DataCrafterConfigurationError


class TestProject:
    """Tests for Project class"""
    
    def test_init_creates_directories(self, temp_dir):
        """Test that init creates required directories"""
        project = Project(temp_dir)
        project.init(name="test-project")
        
        assert os.path.exists(os.path.join(temp_dir, 'current'))
        assert os.path.exists(os.path.join(temp_dir, 'output'))
        assert os.path.exists(os.path.join(temp_dir, 'temp'))
        assert os.path.exists(os.path.join(temp_dir, 'builds'))
        assert os.path.exists(os.path.join(temp_dir, 'storage'))
    
    def test_init_creates_config_file(self, temp_dir):
        """Test that init creates datacrafter.yml"""
        project = Project(temp_dir)
        project.init(name="test-project")
        
        config_file = os.path.join(temp_dir, 'datacrafter.yml')
        assert os.path.exists(config_file)
        
        with open(config_file, 'r', encoding='utf8') as f:
            config = yaml.safe_load(f)
        assert config['project-name'] == 'test-project'
        assert 'project-id' in config
    
    def test_validate_init_stub_is_incomplete(self, sample_project):
        """init writes a stub YAML without extractor; check must fail."""
        is_valid, report = sample_project.validate()
        assert is_valid is False
        assert 'extractor' in report

    def test_validate_full_config(self, sample_project, sample_config):
        sample_project.project = sample_config
        is_valid, report = sample_project.validate()
        assert is_valid is True
        assert report is None

    def test_validate_unknown_destination(self, sample_project, sample_config):
        sample_config['destination'] = {'type': 'doesnotexist'}
        sample_project.project = sample_config
        is_valid, report = sample_project.validate()
        assert is_valid is False
        assert 'doesnotexist' in report
    
    def test_clean_removes_files(self, sample_project):
        """Test that clean removes temporary files"""
        # Create some test files
        output_file = os.path.join(sample_project.output, 'test.jsonl')
        with open(output_file, 'w') as f:
            f.write('test')
        
        assert os.path.exists(output_file)
        sample_project.clean()
        assert not os.path.exists(output_file)
    
    def test_load_existing_project(self, temp_dir):
        """Test loading an existing project"""
        # Create project
        project1 = Project(temp_dir)
        project1.init(name="test-project")
        
        # Load project
        project2 = Project(temp_dir)
        assert project2.project is not None
        assert project2.project['project-name'] == 'test-project'

    def test_prepare_sets_extractor_processor_destination(
            self, sample_project, sample_config):
        sample_project.project = sample_config
        sample_project.prepare()
        assert sample_project.extractor is not None
        assert sample_project.processor is not None
        assert sample_project.destination is not None

    def test_plan_does_not_write(self, sample_project, sample_config):
        sample_project.project = sample_config
        jsonl = os.path.join(sample_project.current, 'preview.jsonl')
        with open(jsonl, 'w', encoding='utf8') as file_obj:
            file_obj.write('{"id": 1}\n{"id": 2}\n')
        plan = sample_project.plan()
        assert plan['will_write'] is False
        assert plan['extractor']['type'] == 'file-csv'
        assert plan['estimated_records'] == 2
        assert len(plan['extractors']) == 1

    def test_plan_lists_extractors(self, sample_project, sample_config):
        spec = sample_config.pop('extractor')
        second = dict(spec)
        second['name'] = 'two'
        second['config'] = {'url': 'https://example.com/two.csv'}
        spec['name'] = 'one'
        sample_config['extractors'] = [spec, second]
        sample_project.project = sample_config
        plan = sample_project.plan()
        assert [item['name'] for item in plan['extractors']] == ['one', 'two']
        assert plan['extractor']['name'] == 'one'
        assert plan['extractors'][1]['url'] == 'https://example.com/two.csv'

    def test_collect_skips_successful_extractor(
            self, sample_project, sample_config, monkeypatch):
        from datacrafter.common.state import ProjectState
        sample_project.project = sample_config
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)
        sample_project.state.add(
            'extractor', status='success',
            results=[{'filename': 'already.csv'}])
        called = []
        monkeypatch.setattr(
            'datacrafter.cmds.project.get_extractor',
            lambda *_args, **_kwargs: called.append(True))
        sample_project.collect()
        assert called == []

    def test_collect_records_failure(
            self, sample_project, sample_config, monkeypatch):
        from datacrafter.common.state import ProjectState
        sample_project.project = sample_config
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)

        class Boom:
            results = []

            def run(self, update_state=False):
                raise RuntimeError('network down')

        monkeypatch.setattr(
            'datacrafter.cmds.project.get_extractor',
            lambda *_args, **_kwargs: Boom())
        with pytest.raises(RuntimeError, match='network down'):
            sample_project.collect()
        assert sample_project.state.stages[-1]['status'] == 'fail'

    def test_process_requires_extractor_stage(
            self, sample_project, sample_config):
        from datacrafter.common.state import ProjectState
        sample_project.project = sample_config
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)
        sample_project.prepare()
        with pytest.raises(ValueError, match='No extractor'):
            sample_project.process()

    def test_process_jsonl_to_file_destination(
            self, sample_project, sample_config):
        from datacrafter.common.state import ProjectState
        sample_project.project = sample_config
        src = os.path.join(sample_project.current, 'data.jsonl')
        with open(src, 'w', encoding='utf8') as file_obj:
            file_obj.write('{"id": 1, "name": "Ada"}\n')
            file_obj.write('{"id": 2, "name": "Bob"}\n')
        sample_project.state = ProjectState(
            filename=os.path.join(sample_project.project_path, 'state.json'),
            reset=True, autosave=True)
        sample_project.state.add(
            'extractor', status='success',
            results=[{'filename': src, 'type': 'file', 'compressed': False}])
        sample_project.prepare()
        sample_project.process()
        sample_project.finish()
        out = os.path.join(sample_project.output, 'output.jsonl')
        assert os.path.exists(out)
        with open(out, encoding='utf8') as file_obj:
            lines = [line for line in file_obj if line.strip()]
        assert len(lines) == 2
        assert os.path.exists(
            os.path.join(sample_project.output, 'datapackage.json'))

    def test_run_dry_run_returns_plan(
            self, sample_project, sample_config):
        sample_project.project = sample_config
        plan = sample_project.run(dry_run=True)
        assert plan['will_write'] is False
        assert plan['project-name'] == 'test-project'

    def test_run_executes_stages(
            self, sample_project, sample_config, monkeypatch):
        sample_project.project = sample_config
        order = []
        monkeypatch.setattr(
            sample_project, 'prepare', lambda: order.append('prepare'))
        monkeypatch.setattr(
            sample_project, 'collect',
            lambda _proceed=True: order.append('collect'))
        monkeypatch.setattr(
            sample_project, 'process', lambda: order.append('process'))
        monkeypatch.setattr(
            sample_project, 'finish', lambda: order.append('finish'))
        sample_project.run()
        assert order == ['prepare', 'collect', 'process', 'finish']

    def test_run_rejects_invalid_config(self, sample_project):
        sample_project.project = {
            'version': '1', 'project-name': 'x'}
        with pytest.raises(ValueError, match='Invalid configuration'):
            sample_project.run()

    def test_log_returns_recent_lines(self, sample_project):
        with open(sample_project.logfile, 'w', encoding='utf8') as file_obj:
            file_obj.write('first\nsecond\nthird\n')
        assert sample_project.log(lines=2) == 'second\nthird\n'

    def test_log_missing_file(self, sample_project):
        if os.path.exists(sample_project.logfile):
            os.remove(sample_project.logfile)
        assert sample_project.log() is None

