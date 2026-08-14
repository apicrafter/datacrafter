"""Tests for RSS/Atom and DCAT catalog parsing."""
import json
import os

from datacrafter.extractors.feeds import (
    extract_dcat, extract_rss, parse_dcat, parse_feed)

RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item>
    <title>One</title>
    <link>https://example.com/one</link>
    <enclosure url="https://example.com/one.csv" type="text/csv"/>
  </item>
</channel></rss>
"""

ATOM = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Two</title>
    <link href="https://example.com/two" rel="alternate"/>
    <updated>2026-01-01T00:00:00Z</updated>
  </entry>
</feed>
"""


def test_parse_rss_and_atom():
    rss_items = parse_feed(RSS)
    assert rss_items[0]['title'] == 'One'
    assert rss_items[0]['link'] == 'https://example.com/one'
    assert rss_items[0]['enclosure'] == 'https://example.com/one.csv'
    atom_items = parse_feed(ATOM)
    assert atom_items[0]['title'] == 'Two'
    assert atom_items[0]['link'] == 'https://example.com/two'


def test_parse_dcat_us():
    datasets = parse_dcat({
        'dataset': [
            {'title': 'Roads', 'distribution': [
                {'downloadURL': 'https://example.com/roads.csv', 'format': 'CSV'}
            ]}
        ]
    })
    assert datasets[0]['title'] == 'Roads'


def test_extract_rss_writes_jsonl(tmp_path):
    feed = tmp_path / 'feed.xml'

    def fake_get(url, dest, **_kwargs):
        dest_dir = os.path.dirname(dest)
        os.makedirs(dest_dir, exist_ok=True)
        with open(dest, 'w', encoding='utf8') as file_obj:
            file_obj.write(RSS)
        return True

    jsonl = str(tmp_path / 'data.jsonl')
    results, items = extract_rss(
        'https://example.com/feed.xml', jsonl, str(tmp_path),
        get_file_func=fake_get)
    assert items[0]['title'] == 'One'
    with open(jsonl, encoding='utf8') as file_obj:
        row = json.loads(file_obj.readline())
    assert row['link'] == 'https://example.com/one'
    assert results[0]['filename'] == jsonl


def test_extract_dcat_writes_jsonl(tmp_path):
    catalog = {
        'dataset': [{'title': 'A', 'distribution': []}]
    }

    def fake_get(url, dest, **_kwargs):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf8') as file_obj:
            json.dump(catalog, file_obj)
        return True

    jsonl = str(tmp_path / 'data.jsonl')
    _results, datasets = extract_dcat(
        'https://example.com/data.json', jsonl, str(tmp_path),
        get_file_func=fake_get)
    assert datasets[0]['title'] == 'A'
    with open(jsonl, encoding='utf8') as file_obj:
        assert json.loads(file_obj.readline())['title'] == 'A'


def test_extract_rss_downloads_enclosures(tmp_path):
    written = []

    def fake_get(url, dest, **_kwargs):
        os.makedirs(os.path.dirname(dest) or '.', exist_ok=True)
        if url.endswith('.xml') or 'feed' in url:
            with open(dest, 'w', encoding='utf8') as file_obj:
                file_obj.write(RSS)
        else:
            with open(dest, 'w', encoding='utf8') as file_obj:
                file_obj.write('id\n1\n')
        written.append(dest)
        return True

    jsonl = str(tmp_path / 'data.jsonl')
    results, _items = extract_rss(
        'https://example.com/feed.xml', jsonl, str(tmp_path),
        download_enclosures=True, get_file_func=fake_get)
    assert any(r['filename'].endswith('one.csv') for r in results)


def test_extract_dcat_downloads_matching_format(tmp_path):
    catalog = {
        'dataset': [{
            'title': 'A',
            'distribution': [
                {'downloadURL': 'https://example.com/a.csv', 'format': 'CSV'},
                {'downloadURL': 'https://example.com/a.json', 'format': 'JSON'},
            ],
        }]
    }

    def fake_get(url, dest, **_kwargs):
        os.makedirs(os.path.dirname(dest) or '.', exist_ok=True)
        if dest.endswith('.json') and 'catalog' in os.path.basename(dest):
            with open(dest, 'w', encoding='utf8') as file_obj:
                json.dump(catalog, file_obj)
        elif url.endswith('data.json'):
            with open(dest, 'w', encoding='utf8') as file_obj:
                json.dump(catalog, file_obj)
        else:
            with open(dest, 'w', encoding='utf8') as file_obj:
                file_obj.write('x')
        return True

    jsonl = str(tmp_path / 'data.jsonl')
    results, _datasets = extract_dcat(
        'https://example.com/data.json', jsonl, str(tmp_path),
        download=True, format_filter='csv', get_file_func=fake_get)
    downloaded = [os.path.basename(r['filename']) for r in results]
    assert 'a.csv' in downloaded
    assert 'a.json' not in downloaded
