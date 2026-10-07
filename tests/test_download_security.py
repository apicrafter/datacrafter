"""Security regression tests for download paths and log hygiene."""
import logging
import os
from unittest import mock

import pytest

from datacrafter.common.collect import get_file, redact_url
from datacrafter.extractors.feeds import _basename_from_url, extract_dcat, extract_rss
from datacrafter.extractors.file import FileExtractor


class TestSafeBasename:
    def test_traversal_via_dot_dot_rejected(self):
        assert _basename_from_url('http://host/files/..', 'fallback') == 'fallback'

    def test_trailing_slash_dot_rejected(self):
        assert _basename_from_url('http://host/files/.', 'fallback') == 'fallback'

    def test_backslash_separators_neutralized(self):
        name = _basename_from_url('http://host/a\\..\\..\\evil.csv', 'fallback')
        assert name == 'evil.csv'

    def test_normal_name_preserved(self):
        assert _basename_from_url('http://host/data.csv', 'fallback') == 'data.csv'


class TestEnclosureConfinement:
    FEED = '<rss><channel><item><title>a</title></item></channel></rss>'

    def test_enclosure_downloads_stay_in_current_dir(self, tmp_path):
        current = tmp_path / 'current'
        current.mkdir()
        downloaded = []

        def fake_downloader(url, dest):
            downloaded.append(dest)

        with mock.patch('builtins.open', mock.mock_open(read_data=self.FEED)), \
             mock.patch('datacrafter.extractors.feeds.parse_feed') as parse:
            parse.return_value = [
                {'enclosure': 'http://host/files/..'},
                {'enclosure': 'http://host/x/../../escape.csv'},
            ]
            extract_rss(
                'http://host/feed.xml', str(tmp_path / 'feed.jsonl'),
                str(current), download_enclosures=True,
                get_file_func=fake_downloader)
        assert len(downloaded) == 3  # feed itself + two enclosures
        for dest in downloaded:
            rel = os.path.relpath(os.path.abspath(dest), str(tmp_path))
            assert not rel.startswith('..'), dest

    def test_dcat_distribution_paths_confined(self, tmp_path):
        current = tmp_path / 'current'
        current.mkdir()
        downloaded = []

        def fake_downloader(url, dest):
            downloaded.append(dest)

        catalog = {'dataset': [{'distribution': [
            {'downloadURL': 'http://host/pkg/../../escape.json', 'format': 'json'},
        ]}]}
        with mock.patch('builtins.open', mock.mock_open(
                read_data=__import__('json').dumps(catalog))):
            extract_dcat(
                'http://host/catalog.json', str(tmp_path / 'cat.jsonl'),
                str(current), download=True, get_file_func=fake_downloader)
        for dest in downloaded:
            rel = os.path.relpath(os.path.abspath(dest), str(tmp_path))
            assert not rel.startswith('..'), dest


class TestUrlRedaction:
    def test_redact_url_strips_query(self):
        assert redact_url('http://h/p?api_key=secret&x=1') == 'http://h/p'

    def test_redact_url_keeps_url_without_query(self):
        assert redact_url('http://h/p') == 'http://h/p'

    def test_query_not_logged_at_info(self, tmp_path, caplog):
        url = 'https://example.com/data.csv?api_key=secret'
        with mock.patch('requests.get') as req_get:
            resp = mock.Mock()
            resp.iter_content.return_value = [b'a']
            resp.raise_for_status.return_value = None
            req_get.return_value = resp
            with caplog.at_level(logging.INFO):
                get_file(url, str(tmp_path / 'out.csv'))
        assert 'secret' not in caplog.text
        assert 'example.com/data.csv' in caplog.text

    def test_query_logged_at_debug(self, tmp_path, caplog):
        url = 'https://example.com/data.csv?api_key=secret'
        with mock.patch('requests.get') as req_get:
            resp = mock.Mock()
            resp.iter_content.return_value = [b'a']
            resp.raise_for_status.return_value = None
            req_get.return_value = resp
            with caplog.at_level(logging.DEBUG):
                get_file(url, str(tmp_path / 'out.csv'))
        assert 'secret' in caplog.text


class TestExtractorDownloadOptions:
    def _extractor(self, config):
        project = mock.Mock()
        project.project = {
            'extractor': {
                'mode': 'singlefile', 'type': 'file-csv', 'method': 'url',
                'config': config}}
        project.current = '/tmp/current'
        project.temp = '/tmp/temp'
        return FileExtractor(project)

    def test_verify_tls_false_forwarded(self):
        extractor = self._extractor({
            'url': 'https://example.com/data.csv', 'verify_tls': False})
        with mock.patch('datacrafter.extractors.file.get_file') as get:
            extractor._execute()
        assert get.call_args.kwargs['verify_tls'] is False

    def test_timeout_forwarded(self):
        extractor = self._extractor({
            'url': 'https://example.com/data.csv', 'timeout': 10})
        with mock.patch('datacrafter.extractors.file.get_file') as get:
            extractor._execute()
        assert get.call_args.kwargs['timeout'] == 10

    def test_defaults_not_forwarded(self):
        extractor = self._extractor({'url': 'https://example.com/data.csv'})
        with mock.patch('datacrafter.extractors.file.get_file') as get:
            extractor._execute()
        assert 'verify_tls' not in get.call_args.kwargs
        assert 'timeout' not in get.call_args.kwargs
