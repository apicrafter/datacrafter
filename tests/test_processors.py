"""Tests for processor classes"""
import os
import pytest

from datacrafter.processors.base import (
    DataPipeline,
    KeymapFieldsStep,
    TypemapStep,
    CommonProcessor,
    RecordProcessingError,
    ERROR_STRATEGY_SKIP,
    ERROR_STRATEGY_FAIL,
    ERROR_STRATEGY_RETRY,
)


class TestDataPipeline:
    """Tests for DataPipeline"""
    
    def test_empty_pipeline(self):
        """Test pipeline with no steps"""
        pipeline = DataPipeline()
        record = {'name': 'test', 'value': 42}
        result = pipeline.execute(record)
        assert result == record
    
    def test_keymap_step(self):
        """Test keymapping step"""
        keys = {'old_name': {'name': 'new_name'}}
        step = KeymapFieldsStep(keys=keys)
        pipeline = DataPipeline(steps=[step])
        
        record = {'old_name': 'value'}
        result = pipeline.execute(record)
        assert 'new_name' in result
        assert result['new_name'] == 'value'
        assert 'old_name' not in result
    
    def test_error_strategy_skip(self):
        """Test error strategy skip"""
        class FailingStep:
            def apply(self, record):
                raise ValueError("Test error")
        
        pipeline = DataPipeline(steps=[FailingStep()], error_strategy=ERROR_STRATEGY_SKIP)
        record = {'test': 'value'}
        result = pipeline.execute(record)
        assert result is None  # Record should be skipped
    
    def test_error_strategy_fail(self):
        """Test error strategy fail"""
        class FailingStep:
            def apply(self, record):
                raise ValueError("Test error")
        
        pipeline = DataPipeline(steps=[FailingStep()], error_strategy=ERROR_STRATEGY_FAIL)
        record = {'test': 'value'}
        
        with pytest.raises(RecordProcessingError):
            pipeline.execute(record)

    def test_error_strategy_retry_reraises(self):
        class FailingStep:
            def apply(self, record):
                raise ValueError("Test error")

        pipeline = DataPipeline(
            steps=[FailingStep()], error_strategy=ERROR_STRATEGY_RETRY)
        with pytest.raises(RecordProcessingError):
            pipeline.execute({'test': 'value'})
    
    def test_multiple_steps(self):
        """Test pipeline with multiple steps"""
        keys = {'name': {'name': 'full_name'}}
        step1 = KeymapFieldsStep(keys=keys)
        
        pipeline = DataPipeline(steps=[step1])
        record = {'name': 'Alice', 'age': 30}
        result = pipeline.execute(record)
        
        assert 'full_name' in result
        assert result['full_name'] == 'Alice'
        assert 'age' in result


class TestCommonProcessor:
    """Tests for CommonProcessor"""
    
    def test_process_record(self, sample_project):
        """Test processing a single record"""
        processor = CommonProcessor(sample_project)
        record = {'name': 'test', 'value': '42'}
        
        # Process record (should pass through if no steps configured)
        result = processor.process_record(record)
        assert result is not None
        assert result == record  # No transformation, should be same
    
    def test_stats_initialization(self, sample_project):
        """Test that stats are initialized"""
        processor = CommonProcessor(sample_project)
        assert hasattr(processor, 'stats')
        assert processor.stats['total_records'] == 0
        assert processor.stats['successful_records'] == 0
        assert processor.stats['failed_records'] == 0
        assert processor.stats['skipped_records'] == 0
        assert 'errors' in processor.stats

    def test_run_success_buffered(self, sample_project):
        processor = CommonProcessor(sample_project)
        dest = _RecordingDestination()
        processor.run(
            [{'id': 1}, {'id': 2}, {'id': 3}],
            dest, buffer_size=2, show_progress=False)
        assert processor.stats['total_records'] == 3
        assert processor.stats['successful_records'] == 3
        assert dest.bulk_records == [{'id': 1}, {'id': 2}]
        assert dest.records == [{'id': 3}]

    def test_run_buffer_size_one_uses_single_write(self, sample_project):
        processor = CommonProcessor(sample_project)
        dest = _RecordingDestination()
        processor.run(
            [{'id': 1}, {'id': 2}],
            dest, buffer_size=1, show_progress=False)
        assert dest.records == [{'id': 1}, {'id': 2}]
        assert dest.bulk_records == []

    def test_run_skip_on_error(self, sample_project):
        processor = CommonProcessor(sample_project)

        class Boom:
            def apply(self, record):
                if record.get('bad'):
                    raise ValueError('boom')
                return record

        processor.pipeline.add_step(Boom())
        dest = _RecordingDestination()
        processor.run(
            [{'ok': 1}, {'bad': True}, {'ok': 2}],
            dest, buffer_size=10, show_progress=False)
        assert processor.stats['total_records'] == 3
        written = dest.records + dest.bulk_records
        assert {'ok': 1} in written
        assert {'ok': 2} in written
        assert processor.stats['skipped_records'] == 1

    def test_autoid_disabled_by_default(self, sample_project):
        processor = CommonProcessor(sample_project)
        dest = _RecordingDestination()
        processor.run(
            [{'name': 'Ada'}], dest, buffer_size=1, show_progress=False)
        assert dest.records[0] == {'name': 'Ada'}
        assert '_id' not in dest.records[0]

    def test_autoid_adds_stable_id(self, sample_project):
        sample_project.project['processor'] = {
            'config': {'autoid': True},
        }
        processor = CommonProcessor(sample_project)
        dest = _RecordingDestination()
        processor.run(
            [{'name': 'Ada'}], dest, buffer_size=1, show_progress=False)
        first = dest.records[0]['_id']
        dest2 = _RecordingDestination()
        processor.run(
            [{'name': 'Ada'}], dest2, buffer_size=1, show_progress=False)
        assert dest2.records[0]['_id'] == first
        assert len(first) == 64

    def test_autotype_converts_ints(self, sample_project):
        sample_project.project['processor'] = {
            'config': {'autotype': True},
        }
        processor = CommonProcessor(sample_project)
        dest = _RecordingDestination()
        processor.run(
            [{'age': '30'}, {'age': '25'}],
            dest, buffer_size=10, show_progress=False)
        written = dest.records + dest.bulk_records
        assert written[0]['age'] == 30
        assert written[1]['age'] == 25

    def test_typemap_overrides_autotype(self, sample_project):
        sample_project.project['processor'] = {
            'config': {'autotype': True},
            'typemap': {'age': 'float'},
        }
        processor = CommonProcessor(sample_project)
        dest = _RecordingDestination()
        processor.run(
            [{'age': '30'}], dest, buffer_size=1, show_progress=False)
        assert dest.records[0]['age'] == 30.0
        assert isinstance(dest.records[0]['age'], float)

    def test_keymap_and_typemap_from_config(self, sample_project):
        sample_project.project['processor'] = {
            'config': {},
            'keymap': {'type': 'names', 'fields': {'old': 'new'}},
            'typemap': {'age': 'int'},
        }
        processor = CommonProcessor(sample_project)
        dest = _RecordingDestination()
        processor.run(
            [{'old': 'Ada', 'age': '30'}],
            dest, buffer_size=1, show_progress=False)
        assert dest.records[0] == {'new': 'Ada', 'age': 30}

    def test_custom_script_step(self, sample_project):
        script = os.path.join(sample_project.project_path, 'transform.py')
        with open(script, 'w', encoding='utf8') as file_obj:
            file_obj.write(
                'def process(record):\n'
                '    record["flag"] = True\n'
                '    return record\n'
            )
        sample_project.project['processor'] = {
            'config': {},
            'custom': {'type': 'script', 'code': 'transform.py'},
        }
        processor = CommonProcessor(sample_project)
        dest = _RecordingDestination()
        processor.run(
            [{'name': 'Ada'}], dest, buffer_size=1, show_progress=False)
        assert dest.records[0] == {'name': 'Ada', 'flag': True}

    def test_failed_record_sidecar(self, sample_project, temp_dir):
        sample_project.output = temp_dir
        processor = CommonProcessor(sample_project)

        class Boom:
            def apply(self, record):
                if record.get('bad'):
                    raise ValueError('boom')
                return record

        processor.pipeline.add_step(Boom())
        dest = _RecordingDestination()
        processor.run(
            [{'ok': 1}, {'bad': True}],
            dest, buffer_size=10, show_progress=False)
        sidecar = os.path.join(temp_dir, 'errors.jsonl')
        assert os.path.exists(sidecar)
        with open(sidecar, encoding='utf8') as file_obj:
            lines = [line for line in file_obj if line.strip()]
        assert len(lines) == 1
        assert 'skipped' in lines[0] or 'boom' in lines[0]

    def test_processor_state_persisted(self, sample_project, temp_dir):
        from datacrafter.common.state import ProjectState
        sample_project.state = ProjectState(
            filename=os.path.join(temp_dir, 'state.json'),
            reset=True, autosave=True)
        processor = CommonProcessor(sample_project)
        dest = _RecordingDestination()
        processor.run([{'n': 1}], dest, buffer_size=1, show_progress=False)
        assert sample_project.state.last_stage == 'processor'
        stage = sample_project.state.stages[-1]
        assert stage['status'] == 'success'
        assert stage['results']['total_records'] == 1

    def test_error_strategy_retry_then_succeed(
            self, sample_project, monkeypatch):
        monkeypatch.setattr(
            'datacrafter.processors.base.time.sleep', lambda _delay: None)
        sample_project.project['processor'] = {
            'config': {
                'error_strategy': ERROR_STRATEGY_RETRY,
                'max_retries': 3,
            }
        }
        processor = CommonProcessor(sample_project)

        class Flaky:
            def __init__(self):
                self.attempts = 0

            def apply(self, record):
                self.attempts += 1
                if self.attempts < 3:
                    raise ValueError('transient')
                return record

        processor.pipeline.add_step(Flaky())
        result = processor.process_record({'ok': 1})
        assert result == {'ok': 1}
        assert processor.stats['successful_records'] == 1
        assert processor.stats['failed_records'] == 0

    def test_error_strategy_retry_exhausted(
            self, sample_project, monkeypatch):
        monkeypatch.setattr(
            'datacrafter.processors.base.time.sleep', lambda _delay: None)
        sample_project.project['processor'] = {
            'config': {
                'error_strategy': ERROR_STRATEGY_RETRY,
                'max_retries': 2,
            }
        }
        processor = CommonProcessor(sample_project)

        class AlwaysFail:
            def apply(self, record):
                raise ValueError('nope')

        processor.pipeline.add_step(AlwaysFail())
        result = processor.process_record({'x': 1})
        assert result is None
        assert processor.stats['failed_records'] == 1
        assert processor.stats['successful_records'] == 0


class _RecordingDestination:
    def __init__(self):
        self.records = []
        self.bulk_records = []

    def write(self, record):
        self.records.append(record)

    def write_bulk(self, records):
        self.bulk_records.extend(records)

    def close(self):
        pass

