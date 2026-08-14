"""Tests for datacrafter.common.converters."""
import io
import json

import pytest

from datacrafter.common import converters


def test_csv_to_json():
    source = io.StringIO("id,name\n1,Ada\n2,Bob\n")
    output = io.StringIO()
    converters.csv_to_json(source, output)
    rows = [json.loads(line) for line in output.getvalue().splitlines()]
    assert rows == [
        {'id': '1', 'name': 'Ada'},
        {'id': '2', 'name': 'Bob'},
    ]


def test_csv_to_bson_roundtrip():
    bson = pytest.importorskip('bson')
    source = io.StringIO("id,name\n1,Ada\n")
    output = io.BytesIO()
    converters.csv_to_bson(source, output)
    output.seek(0)
    docs = list(bson.decode_file_iter(output))
    assert docs == [{'id': '1', 'name': 'Ada'}]


def test_etree_to_dict_text_and_attrs():
    etree = pytest.importorskip('lxml.etree')
    root = etree.fromstring(b'<item id="7">Ada</item>')
    assert converters.etree_to_dict(root) == {'item': {'@id': '7', '#text': 'Ada'}}


def test_etree_to_dict_children():
    etree = pytest.importorskip('lxml.etree')
    root = etree.fromstring(b'<item><name>Ada</name><name>Bob</name></item>')
    result = converters.etree_to_dict(root)
    assert result['item']['name'] == ['Ada', 'Bob']


def test_xml_to_jsonl():
    pytest.importorskip('lxml.etree')
    source = io.BytesIO(
        b'<root><item><name>Ada</name></item><item><name>Bob</name></item></root>')
    output = io.StringIO()
    converters.xml_to_jsonl(source, output, tagname='item', dolog=False)
    rows = [json.loads(line) for line in output.getvalue().splitlines()]
    assert rows == [{'item': {'name': 'Ada'}}, {'item': {'name': 'Bob'}}]


def test_xml_to_jsonl_new():
    pytest.importorskip('xmltodict')
    source = io.BytesIO(
        b'<root><item><name>Ada</name></item><item><name>Bob</name></item></root>')
    output = io.StringIO()
    converters.xml_to_jsonl_new(source, output, dolog=False)
    rows = [json.loads(line) for line in output.getvalue().splitlines()]
    assert {'name': 'Ada'} in rows
    assert {'name': 'Bob'} in rows


def test_xls_to_json_uses_sheet_api():
    class FakeSheet:
        nrows = 2
        ncols = 2

        def row_values(self, rownum):
            return [['1', 'Ada'], ['2', 'Bob']][rownum]

    class FakeBook:
        def sheet_by_index(self, _index):
            return FakeSheet()

    output = io.BytesIO()
    converters.xls_to_json(FakeBook(), output, keys=['id', 'name'])
    lines = [json.loads(line) for line in output.getvalue().decode('utf8').splitlines()]
    assert lines == [{'id': '1', 'name': 'Ada'}, {'id': '2', 'name': 'Bob'}]


def test_xlsx_to_json_uses_start_page():
    pytest.importorskip('bson')

    class FakeCell:
        def __init__(self, value):
            self.value = value

    class FakeSheet:
        def __init__(self, rows):
            self._rows = rows

        def iter_rows(self):
            return iter(
                [[FakeCell(value) for value in row] for row in self._rows])

    class FakeBook:
        def __init__(self):
            self.worksheets = [
                FakeSheet([['skip', 'me']]),
                FakeSheet([['id', 'name'], ['1', 'Ada']]),
            ]
            self.active = self.worksheets[0]

        def __getitem__(self, name):
            raise AssertionError(f'unexpected sheet name {name}')

    output = io.BytesIO()
    converters.xlsx_to_json(
        FakeBook(), output, keys=['id', 'name'], start_page=1, start_line=2)
    lines = [
        json.loads(line)
        for line in output.getvalue().decode('utf8').splitlines()
    ]
    assert lines == [{'id': '1', 'name': 'Ada'}]
