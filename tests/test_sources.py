"""Tests for source classes"""
import os
import pytest

from datacrafter.sources.jsonl import JSONLinesSource
from datacrafter.sources.csv import CSVSource


class TestJSONLinesSource:
    """Tests for JSONLinesSource"""
    
    def test_read_single_record(self, jsonl_file):
        """Test reading a single record"""
        source = JSONLinesSource(filename=jsonl_file)
        record = source.read()
        
        assert record['id'] == 1
        assert record['name'] == 'Alice'
        assert record['age'] == 30
    
    def test_read_multiple_records(self, jsonl_file):
        """Test reading multiple records"""
        source = JSONLinesSource(filename=jsonl_file)
        records = []
        try:
            for _ in range(3):
                records.append(source.read())
        except (StopIteration, ValueError):
            pass  # End of file or parsing error
        
        assert len(records) == 3
        assert records[0]['name'] == 'Alice'
        assert records[1]['name'] == 'Bob'
        assert records[2]['name'] == 'Charlie'
    
    def test_read_bulk(self, jsonl_file):
        """Test reading bulk records"""
        source = JSONLinesSource(filename=jsonl_file)
        records = source.read_bulk(2)
        
        assert len(records) == 2
        assert records[0]['id'] == 1
        assert records[1]['id'] == 2
    
    def test_reset(self, jsonl_file):
        """Test resetting the source"""
        source = JSONLinesSource(filename=jsonl_file)
        record1 = source.read()
        source.reset()
        record2 = source.read()
        
        assert record1 == record2
    
    def test_context_manager(self, jsonl_file):
        """Test using source as context manager"""
        with JSONLinesSource(filename=jsonl_file) as source:
            record = source.read()
            assert record is not None
        # File should be closed after context


class TestCSVSource:
    """Tests for CSVSource"""
    
    def test_read_single_record(self, csv_file):
        """Test reading a single CSV record"""
        source = CSVSource(filename=csv_file, keys=None)
        record = source.read()
        
        assert record['id'] == '1'
        assert record['name'] == 'Alice'
        assert record['age'] == '30'
    
    def test_read_with_custom_keys(self, csv_file):
        """Test reading CSV with custom keys"""
        source = CSVSource(filename=csv_file, keys=['id', 'name', 'age'])
        record = source.read()
        
        assert 'id' in record
        assert 'name' in record
        assert 'age' in record
    
    def test_is_flat(self, csv_file):
        """Test that CSV source is flat"""
        source = CSVSource(filename=csv_file)
        assert source.is_flat() is True

