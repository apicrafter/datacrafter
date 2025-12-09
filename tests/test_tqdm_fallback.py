#!/usr/bin/env python
"""Test script to verify tqdm fallback implementation works correctly"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test with tqdm uninstalled by temporarily hiding it
import importlib.util

# Test the fallback implementation
print("Testing tqdm fallback implementation...")

# Force import of processors.base without real tqdm
spec = importlib.util.find_spec('tqdm')
if spec is not None:
    # tqdm is installed, we need to test both cases
    print("\n--- Test 1: With tqdm installed ---")
    from datacrafter.processors.base import tqdm, TQDM_AVAILABLE
    print(f"TQDM_AVAILABLE: {TQDM_AVAILABLE}")
    
    # Test progress bar with total parameter (the problematic case)
    print("\nTest 1a: Progress bar with total parameter")
    try:
        pbar = tqdm(total=100, desc="Testing")
        for i in range(10):
            pbar.update(1)
        pbar.close()
        print("✓ Progress bar with total - SUCCESS")
    except Exception as e:
        print(f"✗ Progress bar with total - FAILED: {e}")
        sys.exit(1)
    
    # Test iteration mode
    print("\nTest 1b: Iterator wrapper mode")
    try:
        data = [1, 2, 3, 4, 5]
        for item in tqdm(data, desc="Iterating"):
            pass
        print("✓ Iterator wrapper - SUCCESS")
    except Exception as e:
        print(f"✗ Iterator wrapper - FAILED: {e}")
        sys.exit(1)

# Now test the fallback by hiding tqdm
print("\n--- Test 2: With tqdm hidden (fallback mode) ---")

# Remove tqdm from sys.modules to force reimport
modules_to_remove = [k for k in sys.modules.keys() if 'tqdm' in k or 'datacrafter' in k]
for mod in modules_to_remove:
    del sys.modules[mod]

# Hide tqdm temporarily
sys.modules['tqdm'] = None

# Re-import to use fallback
from datacrafter.processors.base import tqdm as tqdm_fallback, TQDM_AVAILABLE
print(f"TQDM_AVAILABLE: {TQDM_AVAILABLE}")

# Test progress bar with total parameter (the problematic case)
print("\nTest 2a: Progress bar with total parameter (fallback)")
try:
    pbar = tqdm_fallback(total=100, desc="Testing fallback")
    for i in range(10):
        pbar.update(1)
        pbar.set_postfix(success=i)
    pbar.close()
    print("✓ Progress bar with total (fallback) - SUCCESS")
except Exception as e:
    print(f"✗ Progress bar with total (fallback) - FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test iteration mode
print("\nTest 2b: Iterator wrapper mode (fallback)")
try:
    data = [1, 2, 3, 4, 5]
    result = []
    for item in tqdm_fallback(data, desc="Iterating"):
        result.append(item)
    assert result == data, f"Expected {data}, got {result}"
    print("✓ Iterator wrapper (fallback) - SUCCESS")
except Exception as e:
    print(f"✗ Iterator wrapper (fallback) - FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test no iterable (the original bug scenario)
print("\nTest 2c: Progress bar with only total, no iterable (original bug)")
try:
    pbar = tqdm_fallback(total=None, desc="No total")
    pbar.update(1)
    pbar.close()
    print("✓ Progress bar without total (fallback) - SUCCESS")
except Exception as e:
    print(f"✗ Progress bar without total (fallback) - FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("All tests passed! ✓")
print("="*60)
