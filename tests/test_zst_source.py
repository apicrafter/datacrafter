"""Tests for reading zstd-compressed JSONL sources."""
import json
import os
import shutil
import tempfile

import pytest

from datacrafter.sources import get_source_from_file

zstandard = pytest.importorskip("zstandard")


def test_zst_reading():
    """Test reading a .jsonl.zst file."""
    test_dir = tempfile.mkdtemp()
    test_file = os.path.join(test_dir, 'test.jsonl.zst')
    test_data = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Charlie'},
    ]
    try:
        with zstandard.open(test_file, 'wt', encoding='utf-8') as file_obj:
            for item in test_data:
                file_obj.write(json.dumps(item) + '\n')
        source = get_source_from_file(test_file)
        records = list(source)
        assert records == test_data
    finally:
        shutil.rmtree(test_dir)
