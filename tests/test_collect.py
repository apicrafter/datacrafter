"""Tests for the data collection module (common/collect.py).

These tests cover the security-sensitive behavior:
- aria2 is invoked via ``subprocess.run`` with an argument list (no shell string)
- TLS verification is enabled by default
- ``get_file_by_pattern``/``get_file_by_name`` thread ``verify_tls`` through
- ``load_config`` uses ``yaml.safe_load``
No real network calls are made; ``requests`` and ``subprocess`` are mocked.
"""
import os
import subprocess
from unittest import mock

import pytest

from datacrafter.common import collect
from datacrafter.cmds.project import load_config


class _FakeResponse:
    """Minimal stand-in for a requests.Response used by the download path."""

    def __init__(self, content=b"data", status_code=200):
        self.content = content
        self.status_code = status_code

    def iter_content(self, chunk_size=1):
        yield self.content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"status {self.status_code}")

    def close(self):
        pass


@pytest.fixture
def temp_output(tmp_path):
    return str(tmp_path / "downloaded.bin")


class TestGetFileSecurity:
    """get_file: command injection + TLS hardening."""

    def test_aria2_uses_subprocess_run_with_arg_list(self, temp_output):
        """aria2 MUST be invoked via subprocess with an explicit arg list, never a
        shell string, so URLs containing shell metacharacters are safe."""
        malicious_url = "http://example.com/file; rm -rf /"
        completed = subprocess.CompletedProcess(args=[], returncode=0)
        with mock.patch("datacrafter.common.collect.subprocess.run",
                        return_value=completed) as run_mock, \
                mock.patch("datacrafter.common.collect.requests.get",
                           return_value=_FakeResponse()):
            collect.get_file(malicious_url, temp_output, aria2=True,
                             aria2path="aria2c")
        # subprocess.run must have been called exactly once ...
        run_mock.assert_called_once()
        args, kwargs = run_mock.call_args
        cmd = args[0] if args else kwargs.get("args")
        # ... with shell disabled ...
        assert kwargs.get("shell") is False or "shell" not in kwargs
        # ... and the malicious URL appears as a single literal argument, not split.
        assert malicious_url in cmd
        # The command is a list of literal args, not a string passed to a shell.
        assert isinstance(cmd, list)
        assert any(part == malicious_url for part in cmd)

    def test_get_file_verifies_tls_by_default(self, temp_output):
        """Default download MUST verify TLS certificates (verify=True)."""
        with mock.patch("datacrafter.common.collect.requests.get",
                        return_value=_FakeResponse()) as get_mock:
            collect.get_file("https://example.com/data", temp_output)
        _, kwargs = get_mock.call_args
        assert kwargs.get("verify") is True

    def test_get_file_explicit_verify_false_warns(self, temp_output, caplog):
        """Explicit opt-out is honored and logs a warning."""
        with mock.patch("datacrafter.common.collect.requests.get",
                        return_value=_FakeResponse()) as get_mock:
            with caplog.at_level("WARNING"):
                collect.get_file("https://example.com/data", temp_output,
                                 verify_tls=False)
        _, kwargs = get_mock.call_args
        assert kwargs.get("verify") is False
        assert any("TLS certificate verification disabled" in r.message
                   for r in caplog.records)


class TestFetchUrlContent:
    def test_fetch_url_content_verifies_tls_by_default(self):
        """_fetch_url_content MUST verify TLS by default."""
        with mock.patch("datacrafter.common.collect.requests.Session") as Session:
            session = Session.return_value
            session.get.return_value = _FakeResponse(content=b"html")
            collect._fetch_url_content("https://example.com")
        _, kwargs = session.get.call_args
        assert kwargs.get("verify") is True

    def test_get_file_by_pattern_threads_verify_tls(self, tmp_path):
        """get_file_by_pattern MUST pass verify_tls down to _fetch_url_content."""
        fake = _FakeResponse(content=b"<html><body></body></html>")
        with mock.patch("datacrafter.common.collect._fetch_url_content",
                        return_value=b"<html></html>") as fetch_mock, \
                mock.patch("datacrafter.common.collect.requests.get",
                           return_value=fake), \
                mock.patch(
                    "datacrafter.common.collect.BeautifulSoup") as bs_class:
            bs_class.return_value.find_all.return_value = []
            collect.get_file_by_pattern(
                str(tmp_path), str(tmp_path), "https://example.com",
                "prefix", str(tmp_path / "out.bin"), verify_tls=False)
        _, kwargs = fetch_mock.call_args
        assert kwargs.get("verify_tls") is False

    def test_get_file_retries_then_succeeds(self, temp_output, monkeypatch):
        import requests as requests_mod
        calls = {'n': 0}

        def flaky(*_args, **_kwargs):
            calls['n'] += 1
            if calls['n'] < 2:
                raise requests_mod.exceptions.ConnectionError('temp fail')
            return _FakeResponse()

        monkeypatch.setattr(collect.time, 'sleep', lambda _s: None)
        monkeypatch.setattr(collect.requests, 'get', flaky)
        collect.get_file('https://example.com/data', temp_output)
        assert calls['n'] == 2
        assert os.path.exists(temp_output)

    def test_get_file_by_pattern_downloads_matching_link(
            self, tmp_path, monkeypatch):
        html = (
            b'<html><a href="data-2026.csv">csv</a>'
            b'<a href="other.json">json</a></html>'
        )
        downloaded = {}

        def fake_get(url, filename, **_kwargs):
            downloaded['url'] = url
            downloaded['filename'] = filename
            with open(filename, 'wb') as file_obj:
                file_obj.write(b'id,name\n')
            return filename

        monkeypatch.setattr(
            collect, '_fetch_url_content', lambda *_a, **_k: html)
        monkeypatch.setattr(collect, 'get_file', fake_get)
        out = str(tmp_path / 'out.csv')
        result = collect.get_file_by_pattern(
            str(tmp_path), str(tmp_path), 'https://example.com/list',
            'data-', out, file_type='csv', force=True)
        assert result == out
        assert downloaded['url'] == 'https://example.com/data-2026.csv'

    def test_get_file_by_name_joins_relative_href(
            self, tmp_path, monkeypatch):
        html = b'<html><a href="files/data.csv">dataset</a></html>'
        monkeypatch.setattr(
            collect, '_fetch_url_content', lambda *_a, **_k: html)

        def fake_get(url, filename, **_kwargs):
            with open(filename, 'wb') as file_obj:
                file_obj.write(b'ok')
            return filename

        monkeypatch.setattr(collect, 'get_file', fake_get)
        result = collect.get_file_by_name(
            str(tmp_path), str(tmp_path), 'https://example.com/page',
            name='dataset', file_prefix='gov', file_type='csv')
        assert result.endswith('gov_current.csv')
        assert os.path.exists(result)


class TestLoadConfigSafe:
    def test_load_config_uses_safe_load(self, tmp_path):
        """load_config MUST use yaml.safe_load (not the unsafe full loader)."""
        config = tmp_path / "datacrafter.yml"
        config.write_text("project-name: test\nversion: '1'\n", encoding="utf8")
        data = load_config(str(config))
        assert data["project-name"] == "test"
        assert data["version"] == "1"

    def test_load_config_rejects_python_object_tags(self, tmp_path):
        """A YAML tag that would construct an arbitrary Python object MUST be
        rejected by safe_load rather than executed."""
        config = tmp_path / "evil.yml"
        # !!python/object/apply:os.system [...] is the classic unsafe load exploit.
        config.write_text(
            "value: !!python/object/apply:os.system ['echo pwned']\n",
            encoding="utf8")
        import yaml
        with pytest.raises(yaml.YAMLError):
            load_config(str(config))
