"""Tests for datacrafter.common.converters (etree_to_dict)."""
import pytest

from datacrafter.common import converters


def test_etree_to_dict_text_and_attrs():
    etree = pytest.importorskip('lxml.etree')
    root = etree.fromstring(b'<item id="7">Ada</item>')
    assert converters.etree_to_dict(root) == {'item': {'@id': '7', '#text': 'Ada'}}


def test_etree_to_dict_children():
    etree = pytest.importorskip('lxml.etree')
    root = etree.fromstring(b'<item><name>Ada</name><name>Bob</name></item>')
    result = converters.etree_to_dict(root)
    assert result['item']['name'] == ['Ada', 'Bob']


def test_etree_to_dict_namespaced_tag_stripped():
    etree = pytest.importorskip('lxml.etree')
    root = etree.fromstring(
        b'<root xmlns:dc="http://purl.org/dc/elements/1.1/">'
        b'<item><dc:name>Ada</dc:name></item></root>')
    result = converters.etree_to_dict(root.find('item'))
    assert result['item']['name'] == 'Ada'
