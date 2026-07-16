"""Tests for the tqdm fallback implementation in datacrafter.processors.base.

The processor module imports ``tqdm`` if available and otherwise defines a minimal
fallback that supports the operations datacrafter uses (``total=`` kwarg, iterator
wrapping, ``update``, ``set_postfix``, ``close``). These tests exercise both the
fallback path and the real-tqdm path (when installed), and guard against the original
bug where ``total=None`` crashed the fallback.
"""
import builtins
import importlib
import sys

import pytest


def _import_processor_base():
    """Import (or re-import) datacrafter.processors.base and return the module."""
    import importlib
    return importlib.import_module("datacrafter.processors.base")


@pytest.fixture
def fallback_module(monkeypatch):
    """Force the tqdm-fallback path by hiding the tqdm package, then reload
    datacrafter.processors.base so it picks up the fallback definition."""
    real_import = builtins.__import__

    def blocked_import(name, *args, **kwargs):
        if name == "tqdm" or name.startswith("tqdm."):
            raise ImportError("tqdm hidden by test fixture")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)
    # Drop cached modules so the reload exercises the import guard.
    for mod in [m for m in list(sys.modules) if m == "datacrafter.processors.base"
                or m.startswith("tqdm")]:
        monkeypatch.delitem(sys.modules, mod, raising=False)
    module = importlib.import_module("datacrafter.processors.base")
    importlib.reload(module)
    return module


class TestTqdmFallback:
    """The fallback progress bar used when tqdm is not installed."""

    def test_fallback_reports_unavailable(self, fallback_module):
        assert fallback_module.TQDM_AVAILABLE is False

    def test_fallback_progress_bar_with_total(self, fallback_module):
        """Fallback bar with an explicit total MUST work (the original bug)."""
        tqdm = fallback_module.tqdm
        pbar = tqdm(total=100, desc="Testing fallback")
        for _ in range(10):
            pbar.update(1)
        pbar.set_postfix(success=5)
        pbar.close()  # must not raise

    def test_fallback_iterator_wrapper(self, fallback_module):
        """Fallback bar wrapping an iterable MUST yield every item."""
        tqdm = fallback_module.tqdm
        data = [1, 2, 3, 4, 5]
        result = list(tqdm(data, desc="Iterating"))
        assert result == data

    def test_fallback_progress_bar_without_total(self, fallback_module):
        """Fallback bar with total=None MUST NOT crash (the original bug scenario)."""
        tqdm = fallback_module.tqdm
        pbar = tqdm(total=None, desc="No total")
        pbar.update(1)
        pbar.close()  # must not raise


class TestRealTqdm:
    """When tqdm is installed, the real implementation is used."""

    def test_real_tqdm_available(self):
        tqdm_installed = importlib.util.find_spec("tqdm") is not None
        if not tqdm_installed:
            pytest.skip("tqdm not installed")
        module = _import_processor_base()
        assert module.TQDM_AVAILABLE is True

    def test_real_progress_bar_with_total(self):
        if importlib.util.find_spec("tqdm") is None:
            pytest.skip("tqdm not installed")
        module = _import_processor_base()
        pbar = module.tqdm(total=100, desc="Testing")
        for _ in range(10):
            pbar.update(1)
        pbar.close()

    def test_real_iterator_wrapper(self):
        if importlib.util.find_spec("tqdm") is None:
            pytest.skip("tqdm not installed")
        module = _import_processor_base()
        data = [1, 2, 3]
        assert list(module.tqdm(data)) == data
