#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to verify zst file reading"""
import os
import sys
import tempfile
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datacrafter.sources import get_source_from_file

def test_zst_reading():
    """Test reading a .jsonl.zst file"""
    # Create a test file
    test_dir = tempfile.mkdtemp()
    test_file = os.path.join(test_dir, 'test.jsonl.zst')
    
    # Write some test data
    import zstandard
    test_data = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Charlie'}
    ]
    
    with zstandard.open(test_file, 'wt', encoding='utf-8') as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"Created test file: {test_file}")
    
    # Try to read it back
    try:
        source = get_source_from_file(test_file)
        print(f"Source type: {source.id()}")
        
        records = []
        for record in source:
            records.append(record)
            print(f"Read record: {record}")
        
        print(f"\nSuccessfully read {len(records)} records from {test_file}")
        
        # Verify data
        assert len(records) == len(test_data), f"Expected {len(test_data)} records, got {len(records)}"
        for i, (expected, actual) in enumerate(zip(test_data, records)):
            assert expected == actual, f"Record {i} mismatch: expected {expected}, got {actual}"
        
        print("✓ All tests passed!")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)

if __name__ == '__main__':
    success = test_zst_reading()
    sys.exit(0 if success else 1)
