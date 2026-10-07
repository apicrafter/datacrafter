"""Parametrized compression tests: format x config key x codec grid."""
import bz2
import gzip
import lzma
import zipfile

import pytest

from datacrafter.destinations import get_compression_value, get_destination_from_config


def _has_zstandard():
    """Check if zstandard is installed"""
    try:
        import zstandard  # noqa: F401
        return True
    except ImportError:
        return False


FORMATS = ['jsonl', 'bson', 'csv']
CODECS = ['gz', 'bz2', 'xz', 'zip', 'zst']
KEYS = ['compress', 'compression']


def _read_text(path, codec):
    """Decompress a written file and return its text content."""
    if codec == 'gz':
        with gzip.open(path, 'rt', encoding='utf-8') as fobj:
            return fobj.read()
    if codec == 'bz2':
        with bz2.open(path, 'rt', encoding='utf-8') as fobj:
            return fobj.read()
    if codec == 'xz':
        with lzma.open(path, 'rt', encoding='utf-8') as fobj:
            return fobj.read()
    if codec == 'zip':
        with zipfile.ZipFile(path) as archive:
            return archive.read(archive.namelist()[0]).decode('utf-8')
    if codec == 'zst':
        zstandard = pytest.importorskip('zstandard')
        with zstandard.open(path, 'rt', encoding='utf-8') as fobj:
            return fobj.read()
    raise ValueError(f'unknown codec {codec}')


@pytest.mark.parametrize('key', KEYS)
@pytest.mark.parametrize('codec', CODECS)
@pytest.mark.parametrize('fmt', FORMATS)
def test_compressed_destination(fmt, key, codec, tmp_path):
    """file-{fmt} with {key}: {codec} writes data.{fmt}.{codec} with the record."""
    if codec == 'zst' and not _has_zstandard():
        pytest.skip('zstandard not installed')
    options = {'type': f'file-{fmt}', 'fileprefix': 'data', key: codec}
    dest = get_destination_from_config(str(tmp_path), options)
    dest.write({'id': 1, 'name': 'test'})
    dest.close()

    expected = tmp_path / f'data.{fmt}.{codec}'
    assert expected.exists(), f'expected {expected} to be written'
    if fmt == 'jsonl':
        content = _read_text(str(expected), codec)
        assert '{"id": 1, "name": "test"}' in content


def test_destination_without_compression(tmp_path):
    """file-jsonl without compression writes plain data.jsonl."""
    options = {'type': 'file-jsonl', 'fileprefix': 'data'}
    dest = get_destination_from_config(str(tmp_path), options)
    dest.write({'id': 1, 'name': 'test'})
    dest.close()

    expected = tmp_path / 'data.jsonl'
    assert expected.exists()
    with open(expected, 'r', encoding='utf-8') as fobj:
        assert '{"id": 1, "name": "test"}' in fobj.read()


def test_compression_key_takes_priority(tmp_path):
    """'compression' wins when both 'compress' and 'compression' are set."""
    options = {
        'type': 'file-jsonl',
        'fileprefix': 'data',
        'compress': 'gz',
        'compression': 'bz2',
    }
    dest = get_destination_from_config(str(tmp_path), options)
    dest.write({'id': 1})
    dest.close()

    assert (tmp_path / 'data.jsonl.bz2').exists()
    assert not (tmp_path / 'data.jsonl.gz').exists()


class TestCodecCapabilityTable:
    """SUPPORTED_COMPRESSION must reflect actually-implemented handlers."""

    def test_no_phantom_codecs(self):
        from datacrafter.destinations.base import (
            IMPLEMENTED_COMPRESSION,
            SUPPORTED_COMPRESSION,
        )
        assert set(SUPPORTED_COMPRESSION) == set(IMPLEMENTED_COMPRESSION)
        assert '7z' not in SUPPORTED_COMPRESSION
        assert 'lz4' not in SUPPORTED_COMPRESSION

    def test_zst_capability_follows_zstandard(self):
        from datacrafter.destinations import base as dest_base
        assert dest_base.SUPPORTED_COMPRESSION['zst'] == (
            dest_base.zstandard is not None)

    def test_unsupported_codec_raises_clear_error(self, tmp_path):
        with pytest.raises(ValueError, match='Unsupported compression'):
            get_destination_from_config(
                str(tmp_path),
                {'type': 'file-jsonl', 'fileprefix': 'data',
                 'compression': 'lz4'})


class TestZstWithoutZstandard:
    def test_zst_source_raises_friendly_importerror(self, tmp_path, monkeypatch):
        """Reading .zst without zstandard names the package to install."""
        from datacrafter.sources import open_compressed_file
        monkeypatch.setattr('datacrafter.sources.HAS_ZSTANDARD', False)
        path = tmp_path / 'data.jsonl.zst'
        path.write_bytes(b'')
        with pytest.raises(ImportError, match='pip install zstandard'):
            open_compressed_file(str(path))


class TestGetCompressionValue:
    """Tests for get_compression_value helper."""

    def test_compress_key(self):
        assert get_compression_value({'compress': 'gz'}) == 'gz'

    def test_compression_key(self):
        assert get_compression_value({'compression': 'zst'}) == 'zst'

    def test_neither_key(self):
        assert get_compression_value({'type': 'file-jsonl'}) is None

    def test_compression_wins(self):
        assert get_compression_value(
            {'compress': 'gz', 'compression': 'bz2'}) == 'bz2'
