import os
import shutil
import tempfile
import unittest
import zstandard
from datacrafter.destinations.jsonl import JSONLinesDestination
from datacrafter.destinations import get_destination_from_config

class TestZstdCompression(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.filename = os.path.join(self.test_dir, 'test.jsonl.zst')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_write_read_zstd_direct(self):
        """Test direct instantiation with zst compression"""
        # Write data
        dest = JSONLinesDestination(filename=self.filename, compression='zst')
        data = {'key': 'value', 'number': 123}
        dest.write(data)
        dest.close()

        # Verify file exists with correct extension
        self.assertTrue(os.path.exists(self.filename))
        self.assertTrue(self.filename.endswith('.jsonl.zst'))

        # Read data back using zstandard
        with zstandard.open(self.filename, 'rt', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('{"key": "value", "number": 123}', content)

    def test_write_read_zstd_from_config_compress(self):
        """Test config-based instantiation with 'compress' key"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compress': 'zst'
        }
        dest = get_destination_from_config(self.test_dir, options)
        data = {'key': 'value', 'number': 456}
        dest.write(data)
        dest.close()

        # Verify file exists with correct extension
        expected_file = os.path.join(self.test_dir, 'data.jsonl.zst')
        self.assertTrue(os.path.exists(expected_file))

        # Read data back
        with zstandard.open(expected_file, 'rt', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('{"key": "value", "number": 456}', content)

    def test_write_read_zstd_from_config_compression(self):
        """Test config-based instantiation with 'compression' key"""
        options = {
            'type': 'file-jsonl',
            'fileprefix': 'data',
            'compression': 'zst'
        }
        dest = get_destination_from_config(self.test_dir, options)
        data = {'key': 'value', 'number': 789}
        dest.write(data)
        dest.close()

        # Verify file exists with correct extension
        expected_file = os.path.join(self.test_dir, 'data.jsonl.zst')
        self.assertTrue(os.path.exists(expected_file))

        # Read data back
        with zstandard.open(expected_file, 'rt', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('{"key": "value", "number": 789}', content)

if __name__ == '__main__':
    unittest.main()

