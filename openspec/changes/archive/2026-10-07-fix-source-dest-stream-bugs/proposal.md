# Change: Fix source/destination stream handling correctness bugs

## Why
The October 2026 repository analysis found four correctness bugs on the data hot path:
compressed non-JSONL sources read garbage (and leak the decompression stream), the
nested-dict setter returns after the first list element, `XMLSource` retains the whole
tree and cannot be iterated twice, and a garbage-collected ZIP destination is left
corrupt. Phase 1 of the 2026-10 improvement roadmap.

## What Changes
- Fix `set_dict_value` (`datacrafter/common/common.py:73-83`): move `return result` out
  of the `for` loop so all list elements are processed, and guard missing keys instead
  of raising a raw `KeyError`.
- Route the already-opened decompression stream into every text-based source in
  `get_source_from_file` (`datacrafter/sources/__init__.py:139-194`), or reject
  compression for formats that cannot consume a stream; the stream is never left
  unclosed either way.
- Make `XMLSource` a true streaming source: call `elem.clear()` while iterating and
  implement `reset()` so a second `__iter__` pass yields the same records.
- Make destination closure complete and idempotent: `BaseFileDestination.__del__`
  delegates to `close()`; `close()` also closes `archiveobj` and `_underlying_file`;
  add `__enter__`/`__exit__` to destinations; fix `ZIPSourceWrapper` leaving the
  previous member file open.
- Constructing a `BaseFileSource` with neither `filename` nor `stream` raises a clear
  `ValueError` at construction instead of `AttributeError` at `close()`
  (`datacrafter/sources/base.py:66-93`).

## Impact
- Affected specs: `common-helpers`, `source-dest-io` (new capability)
- Affected code: `datacrafter/common/common.py`, `datacrafter/sources/__init__.py`,
  `datacrafter/sources/xml.py`, `datacrafter/sources/zipped.py`,
  `datacrafter/sources/base.py`, `datacrafter/destinations/base.py`
