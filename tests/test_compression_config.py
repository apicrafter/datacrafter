"""Tests for compression configuration support"""
import os
import json
import gzip
import tempfile
import shutil
import pytest

from datacrafter.destinations import get_destination_from_config


def _has_zstandard():
    """Check if zstandard is installed"""
    try:
        import zstandard  # noqa: F401
        return True
    except ImportError:
        return False


class TestCompressionConfig:
    """Tests for compression configuration with both 'compress' and 'compression' keys"""
    
    def setup_method(self):
        """Setup test directory"""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test directory"""
        shutil.rmtree(self.test_dir)
    
    def test_jsonl_with_compress_key(self):
        """Test file-jsonl with 'compress' key"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compress': 'gz'
        }
        dest = get_destination_from_config(self.test_dir, options)
        
        # Write a record
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension
        expected_file = os.path.join(self.test_dir, 'data.jsonl.gz')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
        
        # Verify file is actually compressed
        with gzip.open(expected_file, 'rt', encoding='utf-8') as f:
            content = f.read()
            assert '{"id": 1, "name": "test"}' in content
    
    def test_jsonl_with_compression_key(self):
        """Test file-jsonl with 'compression' key"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compression': 'gz'
        }
        dest = get_destination_from_config(self.test_dir, options)
        
        # Write a record
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension
        expected_file = os.path.join(self.test_dir, 'data.jsonl.gz')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
        
        # Verify file is actually compressed
        with gzip.open(expected_file, 'rt', encoding='utf-8') as f:
            content = f.read()
            assert '{"id": 1, "name": "test"}' in content
    
    def test_jsonl_without_compression(self):
        """Test file-jsonl without compression"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data'
        }
        dest = get_destination_from_config(self.test_dir, options)
        
        # Write a record
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension (no compression)
        expected_file = os.path.join(self.test_dir, 'data.jsonl')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
        
        # Verify file is plain text
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '{"id": 1, "name": "test"}' in content
    
    def test_bson_with_compress_key(self):
        """Test file-bson with 'compress' key"""
        options = {
            'type': 'file-bson',
            'fileprefix': 'data',
            'compress': 'gz'
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension
        expected_file = os.path.join(self.test_dir, 'data.bson.gz')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
    
    def test_bson_with_compression_key(self):
        """Test file-bson with 'compression' key"""
        options = {
            'type': 'file-bson',
            'fileprefix': 'data',
            'compression': 'gz'
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension
        expected_file = os.path.join(self.test_dir, 'data.bson.gz')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
    
    def test_csv_with_compress_key(self):
        """Test file-csv with 'compress' key"""
        options = {
            'type': 'file-csv',
            'fileprefix': 'data',
            'compress': 'gz'
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension
        expected_file = os.path.join(self.test_dir, 'data.csv.gz')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
    
    def test_csv_with_compression_key(self):
        """Test file-csv with 'compression' key"""
        options = {
            'type': 'file-csv',
            'fileprefix': 'data',
            'compression': 'gz'
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension
        expected_file = os.path.join(self.test_dir, 'data.csv.gz')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
    
    def test_compression_priority(self):
        """Test that 'compression' key takes priority over 'compress' key"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compress': 'gz',
            'compression': 'bz2'  # This should take priority
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file uses 'compression' value
        expected_file = os.path.join(self.test_dir, 'data.jsonl.bz2')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
        
        # Verify gz file was NOT created
        wrong_file = os.path.join(self.test_dir, 'data.jsonl.gz')
        assert not os.path.exists(wrong_file), f"Unexpected file {wrong_file} found"


class TestCompressionTypes:
    """Tests for different compression types"""
    
    def setup_method(self):
        """Setup test directory"""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test directory"""
        shutil.rmtree(self.test_dir)
    
    def test_gz_compression(self):
        """Test gzip compression"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compression': 'gz'
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'test': 'data'})
        dest.close()
        
        expected_file = os.path.join(self.test_dir, 'data.jsonl.gz')
        assert os.path.exists(expected_file)
    
    def test_bz2_compression(self):
        """Test bz2 compression"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compression': 'bz2'
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'test': 'data'})
        dest.close()
        
        expected_file = os.path.join(self.test_dir, 'data.jsonl.bz2')
        assert os.path.exists(expected_file)
    
    def test_xz_compression(self):
        """Test xz compression"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compression': 'xz'
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'test': 'data'})
        dest.close()
        
        expected_file = os.path.join(self.test_dir, 'data.jsonl.xz')
        assert os.path.exists(expected_file)
    
    @pytest.mark.skipif(not _has_zstandard(), reason="zstandard not installed")
    def test_zst_compression(self):
        """Test zstandard compression"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compression': 'zst'
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'test': 'data'})
        dest.close()

        expected_file = os.path.join(self.test_dir, 'data.jsonl.zst')
        assert os.path.exists(expected_file)

    def test_zip_compression(self):
        """Test zip compression"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compression': 'zip'
        }
        dest = get_destination_from_config(self.test_dir, options)
        dest.write({'test': 'data'})
        dest.close()

        expected_file = os.path.join(self.test_dir, 'data.jsonl.zip')
        assert os.path.exists(expected_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
