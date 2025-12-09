#!/usr/bin/env python
"""Test the actual usage pattern that was causing the error"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("Testing datacrafter processor with different source types...")

from datacrafter.processors.base import CommonProcessor
from datacrafter.sources import get_source_from_file
import tempfile
import json

# Create a test project
class MockProject:
    def __init__(self):
        self.project = {
            'processor': {
                'config': {}
            }
        }

# Create a temporary JSON lines file
with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
    temp_file = f.name
    for i in range(10):
        json.dump({'id': i, 'value': f'test_{i}'}, f)
        f.write('\n')

try:
    print(f"\nTest 1: Processing {temp_file}")
    
    # Create processor
    project = MockProject()
    processor = CommonProcessor(project)
    
    # Get source (this creates a generator without __len__)
    source = get_source_from_file(temp_file, stype='jsonl')
    
    print(f"Source type: {type(source)}")
    print(f"Has __len__: {hasattr(source, '__len__')}")
    
    # Try to get length
    try:
        length = len(source)
        print(f"Source length: {length}")
    except TypeError as e:
        print(f"Cannot get length: {e}")
    
    # Create a mock destination
    class MockDestination:
        def write(self, record):
            pass
        
        def write_bulk(self, records):
            pass
        
        def close(self):
            pass
    
    destination = MockDestination()
    
    # This should not crash even if source has no __len__
    print("\nRunning processor...")
    processor.run(source, destination, buffer_size=5, show_progress=True)
    
    print("\n✓ Test passed - no crash!")
    print(f"Stats: {processor.stats}")
    
finally:
    # Clean up
    os.unlink(temp_file)

print("\n" + "="*60)
print("All tests completed successfully! ✓")
print("="*60)
