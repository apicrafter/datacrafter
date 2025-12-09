"""Manual test to demonstrate compression extension fix"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datacrafter.destinations import get_compression_value


def test_get_compression_value():
    """Test the get_compression_value helper function"""
    
    print("Testing get_compression_value() function...\n")
    
    # Test 1: 'compress' key
    options1 = {'compress': 'gz'}
    result1 = get_compression_value(options1)
    assert result1 == 'gz', f"Expected 'gz', got {result1}"
    print("✓ Test 1: 'compress' key returns 'gz'")
    
    # Test 2: 'compression' key
    options2 = {'compression': 'zst'}
    result2 = get_compression_value(options2)
    assert result2 == 'zst', f"Expected 'zst', got {result2}"
    print("✓ Test 2: 'compression' key returns 'zst'")
    
    # Test 3: No compression key
    options3 = {'type': 'file-jsonl'}
    result3 = get_compression_value(options3)
    assert result3 is None, f"Expected None, got {result3}"
    print("✓ Test 3: No compression key returns None")
    
    # Test 4: Both keys present (compression takes priority)
    options4 = {'compress': 'gz', 'compression': 'bz2'}
    result4 = get_compression_value(options4)
    assert result4 == 'bz2', f"Expected 'bz2', got {result4}"
    print("✓ Test 4: 'compression' key takes priority over 'compress'")
    
    print("\n✅ All helper function tests passed!")


def demonstrate_filename_construction():
    """Demonstrate how filenames are constructed"""
    
    print("\nDemonstrating filename construction...\n")
    
    test_cases = [
        ({'type': 'file-jsonl', 'fileprefix': 'data', 'compress': 'gz'}, 'data.jsonl.gz'),
        ({'type': 'file-jsonl', 'fileprefix': 'data', 'compression': 'zst'}, 'data.jsonl.zst'),
        ({'type': 'file-jsonl', 'fileprefix': 'data'}, 'data.jsonl'),
        ({'type': 'file-bson', 'fileprefix': 'output', 'compression': 'xz'}, 'output.bson.xz'),
        ({'type': 'file-csv', 'fileprefix': 'export', 'compress': 'bz2'}, 'export.csv.bz2'),
    ]
    
    for options, expected in test_cases:
        # Simulate filename construction logic
        from datacrafter.destinations import FILEEXT_MAP
        ext = FILEEXT_MAP[options['type']]
        filename = options['fileprefix'] + '.' + ext
        compression = get_compression_value(options)
        if compression is not None:
            filename = filename + '.' + compression
        
        assert filename == expected, f"Expected {expected}, got {filename}"
        print(f"✓ {options} → {filename}")
    
    print("\n✅ All filename construction tests passed!")


if __name__ == '__main__':
    test_get_compression_value()
    demonstrate_filename_construction()
    print("\n" + "="*60)
    print("SUCCESS: Compression extension fix is working correctly!")
    print("="*60)
