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


class TestParquetDestination:
    def test_write_parquet(self, temp_dir):
        pytest.importorskip('pyarrow')
        from datacrafter.destinations.parquet import ParquetDestination
        import pyarrow.parquet as pq

        filename = os.path.join(temp_dir, 'output.parquet')
        dest = ParquetDestination(filename=filename)
        dest.write_bulk([{'id': 1, 'name': 'Ada'}, {'id': 2, 'name': 'Bob'}])
        dest.close()
        assert os.path.exists(filename)
        table = pq.read_table(filename)
        assert table.num_rows == 2
        assert dest.id() == 'parquet'


class TestCSVDestination:
    def test_write_infers_header(self, temp_dir):
        from datacrafter.destinations.csv import CSVDestination
        filename = os.path.join(temp_dir, 'output.csv')
        dest = CSVDestination(filename=filename)
        dest.write({'id': 1, 'name': 'Ada'})
        dest.write({'id': 2, 'name': 'Bob'})
        dest.close()
        with open(filename, encoding='utf8') as file_obj:
            text = file_obj.read()
        assert 'id' in text and 'name' in text
        assert 'Ada' in text
        assert dest.id() == 'csv'
        assert dest.is_flat() is True

    def test_write_bulk_with_keys(self, temp_dir):
        from datacrafter.destinations.csv import CSVDestination
        filename = os.path.join(temp_dir, 'output.csv')
        dest = CSVDestination(filename=filename, keys=['id', 'name'])
        dest.write_bulk([
            {'id': 1, 'name': 'Ada'},
            {'id': 2, 'name': 'Bob'},
        ])
        dest.close()
        with open(filename, encoding='utf8') as file_obj:
            lines = [line.strip() for line in file_obj if line.strip()]
        assert lines[0] == 'id,name'
        assert '1,Ada' in lines[1]

    def test_write_bulk_infers_keys(self, temp_dir):
        from datacrafter.destinations.csv import CSVDestination
        filename = os.path.join(temp_dir, 'output.csv')
        dest = CSVDestination(filename=filename)
        dest.write_bulk([
            {'id': 1, 'name': 'Ada'},
            {'id': 2, 'name': 'Bob'},
        ])
        dest.close()
        with open(filename, encoding='utf8') as file_obj:
            lines = [line.strip() for line in file_obj if line.strip()]
        assert lines[0] == 'id,name'
        assert '1,Ada' in lines[1]
        assert '2,Bob' in lines[2]

    def test_write_bulk_empty_without_keys(self, temp_dir):
        from datacrafter.destinations.csv import CSVDestination
        filename = os.path.join(temp_dir, 'empty.csv')
        dest = CSVDestination(filename=filename)
        dest.write_bulk([])
        dest.close()
        assert os.path.getsize(filename) == 0


class TestBSONDestination:
    def test_write_and_bulk_roundtrip(self, temp_dir):
        bson = pytest.importorskip('bson')
        from datacrafter.destinations.bsonf import BSONDestination
        filename = os.path.join(temp_dir, 'output.bson')
        dest = BSONDestination(filename=filename)
        dest.write({'id': 1, 'name': 'Ada'})
        dest.write_bulk([{'id': 2, 'name': 'Bob'}])
        dest.close()
        with open(filename, 'rb') as file_obj:
            docs = list(bson.decode_file_iter(file_obj))
        assert docs == [
            {'id': 1, 'name': 'Ada'},
            {'id': 2, 'name': 'Bob'},
        ]
        assert dest.id() == 'bson'

