---
title: "Code Quality Guide"
description: "Conventions and review checklist that keep the datacrafter package consistent"
---

# Code Quality Guide

This page distills the durable recommendations from the 1.0.4 code-quality
pass (originally in `notes/`, now retired) into a living checklist.

## Style and linting

- **Ruff** (in `pyproject.toml`) is the single owner of style linting:
  `ruff check datacrafter tests`. Line length is 88.
- **Pylint** runs in CI in errors-only mode (`pylint --errors-only datacrafter`)
  for a second opinion on real defects; style issues belong to ruff.
- No `print()` in package code — use `logging` with lazy `%s` formatting.
- Optional dependencies are guarded with `try/except ImportError` plus a
  `HAS_*` flag, and raise an actionable `ImportError` naming the package to
  install when used while missing.

## Error handling

- No bare `except:`; no `except Exception: pass`. Cleanup paths may catch
  narrowly (`AttributeError, OSError, IOError`) and log at DEBUG.
- Shared constants live in `constants.py` only — and only if something
  imports them. Dead constants, dead functions, and commented-out code are
  deleted, not archived in the tree.

## Resource management

- Sources and destinations own their streams: `close()` closes everything
  opened (including archive members), is idempotent, and `__del__` delegates
  to it. File destinations also work as context managers.
- Compressed inputs are opened as decompressed streams and handed to
  stream-capable sources; formats that need a real file must reject
  compression explicitly.

## Review checklist

1. Does the new code path have a test that fails without it?
2. Are repeated input grids expressed with `pytest.mark.parametrize`?
3. Do new public exceptions derive from `DataCrafterError`?
4. Would a fresh CI environment (missing optional deps) still collect the
   test suite cleanly (`pytest.importorskip` for optional modules)?
5. Are URLs with query strings logged redacted outside DEBUG?
