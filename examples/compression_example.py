"""
Example demonstrating the compression extension fix.

This example shows how the fix allows both 'compress' and 'compression' 
keys to work in YAML configuration files.
"""

# Example 1: Using 'compress' key (original, still works)
config_with_compress = {
    'type': 'file-jsonl',
    'fileprefix': 'data',
    'compress': 'zst'
}
# Result: Creates file 'data.jsonl.zst'

# Example 2: Using 'compression' key (new, now works)
config_with_compression = {
    'type': 'file-jsonl',
    'fileprefix': 'data',
    'compression': 'zst'
}
# Result: Creates file 'data.jsonl.zst'

# Example 3: No compression
config_no_compression = {
    'type': 'file-jsonl',
    'fileprefix': 'data'
}
# Result: Creates file 'data.jsonl'

# Example 4: Different compression types
examples = [
    ({'type': 'file-jsonl', 'fileprefix': 'data', 'compression': 'gz'}, 'data.jsonl.gz'),
    ({'type': 'file-jsonl', 'fileprefix': 'data', 'compression': 'bz2'}, 'data.jsonl.bz2'),
    ({'type': 'file-jsonl', 'fileprefix': 'data', 'compression': 'xz'}, 'data.jsonl.xz'),
    ({'type': 'file-jsonl', 'fileprefix': 'data', 'compression': 'zst'}, 'data.jsonl.zst'),
    ({'type': 'file-jsonl', 'fileprefix': 'data', 'compression': 'zip'}, 'data.jsonl.zip'),
    ({'type': 'file-bson', 'fileprefix': 'output', 'compress': 'gz'}, 'output.bson.gz'),
    ({'type': 'file-csv', 'fileprefix': 'export', 'compression': 'xz'}, 'export.csv.xz'),
]

print("Compression Extension Examples:")
print("=" * 60)
for config, expected_filename in examples:
    compression_key = 'compression' if 'compression' in config else 'compress' if 'compress' in config else 'none'
    compression_value = config.get('compression') or config.get('compress') or 'none'
    print(f"Type: {config['type']:15} | Key: {compression_key:11} | Value: {compression_value:4} → {expected_filename}")
print("=" * 60)
