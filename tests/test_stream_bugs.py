"""Regression tests for source/destination stream-handling fixes."""
import gc
import gzip
import os
import zipfile

import pytest

from datacrafter.common.common import set_dict_value
from datacrafter.destinations.jsonl import JSONLinesDestination
from datacrafter.sources import get_source_from_file
from datacrafter.sources.xml import XMLSource


class TestSetDictValueOnLists:
    """set_dict_value must update every element of a list, not just the first."""

    def test_every_list_element_updated(self):
        adict = {'items': [{'a': {'b': 1}}, {'a': {'b': 2}}, {'a': {'b': 3}}]}
        result = set_dict_value(adict, 'items.a.b', 'x')
        assert result is adict
        for elem in adict['items']:
            assert elem['a']['b'] == 'x'

    def test_missing_key_created_with_build_path(self):
        adict = {'items': [{'a': {'b': 1}}, {'c': 1}]}
        set_dict_value(adict, 'items.a.b', 'x')
        assert adict['items'][0]['a']['b'] == 'x'
        assert adict['items'][1]['a'] == {'b': 'x'}

    def test_missing_key_skipped_without_build_path(self):
        adict = {'items': [{'a': {'b': 1}}, {'c': 1}]}
        set_dict_value(adict, 'items.a.b', 'x', build_path=False)
        assert adict['items'][0]['a']['b'] == 'x'
        assert adict['items'][1] == {'c': 1}


class TestCompressedSources:
    """Compressed files must be decompressed for all stream-capable types."""

    def _write_gz(self, path, text):
        with gzip.open(path, 'wt', encoding='utf-8') as fobj:
            fobj.write(text)

    def test_gzipped_csv_reads_records(self, tmp_path):
        path = str(tmp_path / 'data.csv.gz')
        self._write_gz(path, 'id,name\n1,one\n2,two\n')
        source = get_source_from_file(path, options={})
        records = list(source)
        source.close()
        assert records == [{'id': '1', 'name': 'one'}, {'id': '2', 'name': 'two'}]
        assert source.fobj.closed

    def test_gzipped_jsonl_reads_records(self, tmp_path):
        path = str(tmp_path / 'data.jsonl.gz')
        self._write_gz(path, '{"id": 1}\n{"id": 2}\n')
        source = get_source_from_file(path, options={})
        records = list(source)
        source.close()
        assert records == [{'id': 1}, {'id': 2}]
        assert source.fobj.closed

    def test_gzipped_json_reads_records(self, tmp_path):
        path = str(tmp_path / 'data.json.gz')
        self._write_gz(path, '[{"id": 1}, {"id": 2}]')
        source = get_source_from_file(path, options={})
        records = list(source)
        source.close()
        assert records == [{'id': 1}, {'id': 2}]

    def test_gzipped_xml_reads_records(self, tmp_path):
        path = str(tmp_path / 'data.xml.gz')
        self._write_gz(
            path,
            '<root><row><id>1</id></row><row><id>2</id></row></root>')
        source = get_source_from_file(path, options={'tagname': 'row'})
        records = list(source)
        source.close()
        assert records == [{'id': '1'}, {'id': '2'}]

    def test_compression_rejected_for_xlsx(self, tmp_path):
        path = str(tmp_path / 'data.xlsx.gz')
        self._write_gz(path, 'not a real workbook')
        with pytest.raises(ValueError, match='not supported'):
            get_source_from_file(path, options={'keys': 'a,b'})


class TestXMLSourceReiteration:
    def test_second_pass_yields_same_records(self, tmp_path):
        path = str(tmp_path / 'data.xml')
        with open(path, 'w', encoding='utf-8') as fobj:
            fobj.write('<root><row><id>1</id></row><row><id>2</id></row></root>')
        source = XMLSource(filename=path, tagname='row')
        first = list(source)
        second = list(source)
        source.close()
        assert first == second == [{'id': '1'}, {'id': '2'}]


class TestDestinationClosure:
    def test_garbage_collected_zip_destination_is_valid(self, tmp_path):
        path = str(tmp_path / 'out.zip')
        dest = JSONLinesDestination(path, compression='zip')
        dest.write({'id': 1})
        dest.write({'id': 2})
        del dest
        gc.collect()
        assert zipfile.is_zipfile(path)
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            assert len(names) == 1

    def test_destination_context_manager(self, tmp_path):
        path = str(tmp_path / 'out.jsonl')
        with JSONLinesDestination(path) as dest:
            dest.write({'id': 1})
        assert dest.fobj.closed
        with open(path, 'r', encoding='utf-8') as fobj:
            assert fobj.readline().startswith('{"id"')

    def test_close_is_idempotent(self, tmp_path):
        path = str(tmp_path / 'out.jsonl')
        dest = JSONLinesDestination(path)
        dest.write({'id': 1})
        dest.close()
        dest.close()

    def test_source_requires_filename_or_stream(self):
        from datacrafter.sources.jsonl import JSONLinesSource
        with pytest.raises(ValueError, match='filename or stream'):
            JSONLinesSource()
