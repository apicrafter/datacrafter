"""Tests for the package entry point."""
import pytest

from datacrafter import __main__ as main_mod


def test_main_invokes_cli(monkeypatch):
    called = []
    monkeypatch.setattr('datacrafter.core.cli', lambda: called.append(True))
    main_mod.main()
    assert called == [True]


def test_main_keyboard_interrupt(monkeypatch):
    def boom():
        raise KeyboardInterrupt

    monkeypatch.setattr('datacrafter.core.cli', boom)
    with pytest.raises(SystemExit) as exc_info:
        main_mod.main()
    assert exc_info.value.code == 130


def test_main_fatal_error(monkeypatch):
    def boom():
        raise RuntimeError('boom')

    monkeypatch.setattr('datacrafter.core.cli', boom)
    with pytest.raises(SystemExit) as exc_info:
        main_mod.main()
    assert exc_info.value.code == 1
