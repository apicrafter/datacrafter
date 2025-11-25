"""Tests for destination classes"""
import os
import json
import pytest

from datacrafter.destinations.jsonl import JSONLinesDestination


class TestJSONLinesDestination:
    """Tests for JSONLinesDestination"""
    
    def test_write_single_record(self, temp_dir):
        """Test writing a single record"""
        filename = os.path.join(temp_dir, 'output.jsonl')
        dest = JSONLinesDestination(filename=filename)
        
        record = {'id': 1, 'name': 'Alice', 'age': 30}
        dest.write(record)
        dest.close()
        
        # Verify file was written
        assert os.path.exists(filename)
        with open(filename, 'r', encoding='utf8') as f:
            line = f.readline()
            data = json.loads(line)
            assert data == record
    
    def test_write_bulk_records(self, temp_dir):
        """Test writing bulk records"""
        filename = os.path.join(temp_dir, 'output.jsonl')
        dest = JSONLinesDestination(filename=filename)
        
        records = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
            {'id': 3, 'name': 'Charlie'}
        ]
        dest.write_bulk(records)
        dest.close()
        
        # Verify all records were written
        assert os.path.exists(filename)
        with open(filename, 'r', encoding='utf8') as f:
            lines = f.readlines()
            assert len(lines) == 3
            for i, line in enumerate(lines):
                data = json.loads(line)
                assert data == records[i]
    
    def test_id(self, temp_dir):
        """Test destination ID"""
        filename = os.path.join(temp_dir, 'output.jsonl')
        dest = JSONLinesDestination(filename=filename)
        assert dest.id() == 'jsonl'
        dest.close()

