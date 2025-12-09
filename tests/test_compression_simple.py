"""Simple test for compression configuration without external dependencies"""
import os
import json
import gzip
import tempfile
import shutil
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datacrafter.destinations import get_destination_from_config


def test_jsonl_with_compress_key():
    """Test file-jsonl with 'compress' key"""
    test_dir = tempfile.mkdtemp()
    try:
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compress': 'gz'
        }
        dest = get_destination_from_config(test_dir, options)
        
        # Write a record
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension
        expected_file = os.path.join(test_dir, 'data.jsonl.gz')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
        print(f"✓ File created with correct extension: {expected_file}")
        
        # Verify file is actually compressed
        with gzip.open(expected_file, 'rt', encoding='utf-8') as f:
            content = f.read()
            assert '{"id": 1, "name": "test"}' in content
        print("✓ File is properly compressed and readable")
        
    finally:
        shutil.rmtree(test_dir)


def test_jsonl_with_compression_key():
    """Test file-jsonl with 'compression' key"""
    test_dir = tempfile.mkdtemp()
    try:
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compression': 'gz'
        }
        dest = get_destination_from_config(test_dir, options)
        
        # Write a record
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension
        expected_file = os.path.join(test_dir, 'data.jsonl.gz')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
        print(f"✓ File created with correct extension: {expected_file}")
        
        # Verify file is actually compressed
        with gzip.open(expected_file, 'rt', encoding='utf-8') as f:
            content = f.read()
            assert '{"id": 1, "name": "test"}' in content
        print("✓ File is properly compressed and readable")
        
    finally:
        shutil.rmtree(test_dir)


def test_jsonl_without_compression():
    """Test file-jsonl without compression"""
    test_dir = tempfile.mkdtemp()
    try:
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data'
        }
        dest = get_destination_from_config(test_dir, options)
        
        # Write a record
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file has correct extension (no compression)
        expected_file = os.path.join(test_dir, 'data.jsonl')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
        print(f"✓ File created without compression: {expected_file}")
        
        # Verify file is plain text
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '{"id": 1, "name": "test"}' in content
        print("✓ File is plain text and readable")
        
    finally:
        shutil.rmtree(test_dir)


def test_compression_priority():
    """Test that 'compression' key takes priority over 'compress' key"""
    test_dir = tempfile.mkdtemp()
    try:
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compress': 'gz',
            'compression': 'bz2'  # This should take priority
        }
        dest = get_destination_from_config(test_dir, options)
        dest.write({'id': 1, 'name': 'test'})
        dest.close()
        
        # Verify file uses 'compression' value
        expected_file = os.path.join(test_dir, 'data.jsonl.bz2')
        assert os.path.exists(expected_file), f"Expected file {expected_file} not found"
        print(f"✓ 'compression' key takes priority: {expected_file}")
        
        # Verify gz file was NOT created
        wrong_file = os.path.join(test_dir, 'data.jsonl.gz')
        assert not os.path.exists(wrong_file), f"Unexpected file {wrong_file} found"
        print("✓ 'compress' key was correctly ignored")
        
    finally:
        shutil.rmtree(test_dir)


if __name__ == '__main__':
    print("Testing compression configuration support...\n")
    
    print("Test 1: JSONL with 'compress' key")
    test_jsonl_with_compress_key()
    print()
    
    print("Test 2: JSONL with 'compression' key")
    test_jsonl_with_compression_key()
    print()
    
    print("Test 3: JSONL without compression")
    test_jsonl_without_compression()
    print()
    
    print("Test 4: Compression priority")
    test_compression_priority()
    print()
    
    print("✅ All tests passed!")
