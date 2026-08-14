"""Parse RSS/Atom feeds and DCAT JSON catalogs into record lists."""
import json
import logging
import os
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

from ..common.collect import get_file


def _local_name(tag):
    if '}' in tag:
        return tag.rsplit('}', 1)[-1]
    return tag


def _child_text(element, name):
    for child in list(element):
        if _local_name(child.tag) == name:
            return (child.text or '').strip()
    return ''


def _link_href(element):
    for child in list(element):
        if _local_name(child.tag) != 'link':
            continue
        href = child.attrib.get('href') or child.attrib.get('url')
        if href:
            rel = child.attrib.get('rel', 'alternate')
            if rel in ('alternate', 'self', ''):
                return href
        if child.text and child.text.strip().startswith('http'):
            return child.text.strip()
    return _child_text(element, 'link')


def _enclosure_url(element):
    for child in list(element):
        lname = _local_name(child.tag)
        if lname == 'enclosure':
            return child.attrib.get('url') or child.attrib.get('href')
        if lname == 'link' and child.attrib.get('rel') == 'enclosure':
            return child.attrib.get('href')
    return None


def parse_feed(xml_text):
    """Return a list of feed item dicts from RSS or Atom XML."""
    root = ET.fromstring(xml_text)
    items = []
    for element in root.iter():
        name = _local_name(element.tag)
        if name not in ('item', 'entry'):
            continue
        items.append({
            'title': _child_text(element, 'title'),
            'link': _link_href(element),
            'published': (
                _child_text(element, 'pubDate')
                or _child_text(element, 'updated')
                or _child_text(element, 'published')),
            'summary': (
                _child_text(element, 'description')
                or _child_text(element, 'summary')),
            'enclosure': _enclosure_url(element),
        })
    return items


def parse_dcat(data):
    """Return dataset dicts from DCAT-US or a list of datasets."""
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    if isinstance(data.get('dataset'), list):
        return data['dataset']
    if isinstance(data.get('datasets'), list):
        return data['datasets']
    graph = data.get('@graph')
    if isinstance(graph, list):
        return [
            node for node in graph
            if isinstance(node, dict) and 'Dataset' in str(node.get('@type', ''))
        ]
    return [data] if 'title' in data or 'name' in data else []


def _basename_from_url(url, fallback):
    path = urlparse(url).path.rstrip('/')
    name = os.path.basename(path) if path else ''
    return name or fallback


def extract_rss(url, jsonl_path, current_dir, download_enclosures=False,
                get_file_func=None):
    """Download a feed, write JSONL items, optionally fetch enclosures."""
    downloader = get_file_func or get_file
    feed_path = os.path.join(os.path.dirname(jsonl_path), '.feed.xml')
    downloader(url, feed_path)
    with open(feed_path, 'r', encoding='utf8') as file_obj:
        items = parse_feed(file_obj.read())
    _write_jsonl(jsonl_path, items)
    results = [{'filename': jsonl_path, 'compressed': False, 'type': 'file'}]
    if download_enclosures:
        for index, item in enumerate(items):
            enclosure = item.get('enclosure')
            if not enclosure:
                continue
            dest = os.path.join(
                current_dir,
                _basename_from_url(enclosure, f'enclosure-{index}'))
            try:
                downloader(enclosure, dest)
                results.append(
                    {'filename': dest, 'compressed': False, 'type': 'file'})
            except Exception as error:
                logging.warning('Failed to download enclosure %s: %s', enclosure, error)
    return results, items


def extract_dcat(url, jsonl_path, current_dir, download=False, format_filter=None,
                 get_file_func=None):
    """Download a DCAT JSON catalog, write datasets, optionally fetch files."""
    downloader = get_file_func or get_file
    catalog_path = os.path.join(os.path.dirname(jsonl_path), '.catalog.json')
    downloader(url, catalog_path)
    with open(catalog_path, 'r', encoding='utf8') as file_obj:
        payload = json.load(file_obj)
    datasets = parse_dcat(payload)
    _write_jsonl(jsonl_path, datasets)
    results = [{'filename': jsonl_path, 'compressed': False, 'type': 'file'}]
    if not download:
        return results, datasets
    wanted = (format_filter or '').lower()
    index = 0
    for dataset in datasets:
        for dist in dataset.get('distribution') or []:
            if not isinstance(dist, dict):
                continue
            file_url = dist.get('downloadURL') or dist.get('accessURL')
            if not file_url:
                continue
            label = str(dist.get('format') or dist.get('mediaType') or file_url)
            if wanted and wanted not in label.lower() and wanted not in file_url.lower():
                continue
            dest = os.path.join(
                current_dir,
                _basename_from_url(file_url, f'distribution-{index}'))
            index += 1
            try:
                downloader(file_url, dest)
                results.append(
                    {'filename': dest, 'compressed': False, 'type': 'file'})
            except Exception as error:
                logging.warning(
                    'Failed to download distribution %s: %s', file_url, error)
    return results, datasets


def _write_jsonl(path, records):
    with open(path, 'w', encoding='utf8') as file_obj:
        for record in records:
            if isinstance(record, dict):
                file_obj.write(json.dumps(record, ensure_ascii=False, default=str))
                file_obj.write('\n')
