## 1. Implementation
- [x] 1.1 Fix `set_dict_value` list branch: `return result` after the loop; use
  `v.get(prefix[0])`-style guarded access for missing keys
- [x] 1.2 Add `stream=` passthrough (or explicit rejection) for csv/json/xml/xls/xlsx/
  bson sources opened from compressed files in `get_source_from_file`
- [x] 1.3 Add `elem.clear()` to `XMLSource.read()` and a `reset()` override that
  re-creates the iterparse reader
- [x] 1.4 Change `BaseFileDestination.__del__` to delegate to `close()`; extend
  `close()` to close `archiveobj` and `_underlying_file`
- [x] 1.5 Add `__enter__`/`__exit__` to `BaseFileDestination` (Project.process keeps its
  existing `finally: close()`, which is now complete and idempotent)
- [x] 1.6 Close the previous member file in `ZIPSourceWrapper.__iter__`
  (`datacrafter/sources/zipped.py:49-53`)
- [x] 1.7 Raise a clear `ValueError` from `BaseFileSource.__init__` when both
  `filename` and `stream` are `None`

## 2. Tests
- [x] 2.1 `set_dict_value` unit test: list of 3 dicts, dotted key set on every element
- [x] 2.2 Compression matrix test: csv/jsonl/xml/json under `.gz` produce the same
  records as uncompressed; no `ResourceWarning` (run pytest with `-W error::ResourceWarning`)
- [x] 2.3 XML re-iteration test: two full passes over the same `XMLSource` yield
  identical record sequences
- [x] 2.4 Destination GC test: ZIP destination written and dropped without `close()`
  produces a valid archive (`zipfile.is_zipfile`)
- [x] 2.5 Context-manager smoke test for a file destination
