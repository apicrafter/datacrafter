"""Tests for processor classes"""
import pytest

from datacrafter.processors.base import (
    DataPipeline,
    KeymapFieldsStep,
    TypemapStep,
    CommonProcessor,
    RecordProcessingError,
    ERROR_STRATEGY_SKIP,
    ERROR_STRATEGY_FAIL
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

