"""Integration tests for ETL pipeline"""
import os
import json
import pytest

from datacrafter.sources.jsonl import JSONLinesSource
from datacrafter.destinations.jsonl import JSONLinesDestination
from datacrafter.processors.base import CommonProcessor, DataPipeline, KeymapFieldsStep
from datacrafter.cmds.project import Project


@pytest.mark.integration
class TestETLPipeline:
    """Integration tests for complete ETL pipeline"""
    
    def test_simple_etl_pipeline(self, temp_dir, jsonl_file):
        """Test a simple ETL pipeline: read -> process -> write"""
        # Setup source
        source = JSONLinesSource(filename=jsonl_file)
        
        # Setup destination
        output_file = os.path.join(temp_dir, 'output.jsonl')
        destination = JSONLinesDestination(filename=output_file)
        
        # Process records
        try:
            record_count = 0
            while True:
                try:
                    record = source.read()
                    if record is None:
                        break
                    # Simple transformation: add a processed flag
                    record['processed'] = True
                    destination.write(record)
                    record_count += 1
                except StopIteration:
                    break
        finally:
            source.close()
            destination.close()
        
        # Verify output
        assert os.path.exists(output_file)
        assert record_count == 3
        with open(output_file, 'r', encoding='utf8') as f:
            lines = f.readlines()
            assert len(lines) == 3
            for line in lines:
                data = json.loads(line)
                assert data['processed'] is True
    
    def test_pipeline_with_keymapping(self, temp_dir, jsonl_file):
        """Test pipeline with keymapping transformation"""
        # Setup source
        source = JSONLinesSource(filename=jsonl_file)
        
        # Setup pipeline with keymapping
        keys = {'name': {'name': 'full_name'}, 'age': {'name': 'years'}}
        keymap_step = KeymapFieldsStep(keys=keys)
        pipeline = DataPipeline(steps=[keymap_step])
        
        # Setup destination
        output_file = os.path.join(temp_dir, 'output.jsonl')
        destination = JSONLinesDestination(filename=output_file)
        
        # Process records
        try:
            while True:
                try:
                    record = source.read()
                    if record is None:
                        break
                    transformed = pipeline.execute(record)
                    if transformed:
                        destination.write(transformed)
                except StopIteration:
                    break
        finally:
            source.close()
            destination.close()
        
        # Verify transformation
        assert os.path.exists(output_file)
        with open(output_file, 'r', encoding='utf8') as f:
            line = f.readline()
            data = json.loads(line)
            assert 'full_name' in data
            assert 'years' in data
            assert 'name' not in data
            assert 'age' not in data
    
    def test_processor_with_error_handling(self, temp_dir, jsonl_file, sample_project):
        """Test processor with error handling"""
        # Setup source
        source = JSONLinesSource(filename=jsonl_file)
        
        # Setup processor
        processor = CommonProcessor(sample_project)
        
        # Setup destination
        output_file = os.path.join(temp_dir, 'output.jsonl')
        destination = JSONLinesDestination(filename=output_file)
        
        # Process with error handling
        try:
            processor.run(source, destination, buffer_size=2)
        finally:
            source.close()
            destination.close()
        
        # Verify stats
        assert processor.stats['total_records'] == 3
        assert processor.stats['successful_records'] == 3
        assert processor.stats['failed_records'] == 0
        
        # Verify output
        assert os.path.exists(output_file)
        with open(output_file, 'r', encoding='utf8') as f:
            lines = f.readlines()
            assert len(lines) == 3

