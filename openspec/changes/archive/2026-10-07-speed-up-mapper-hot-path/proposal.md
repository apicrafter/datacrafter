# Change: Speed up the mapper hot path

## Why
The two `FIXME` markers in `common/mappers.py` sit on the per-record hot path:
`convert_to_date`/`convert_to_datetime` (`mappers.py:97-98`) retry every date pattern
via `strptime` for every value — and `infer_value_type` (`infer.py:35`) calls it too,
making schema inference O(patterns × values) — and `simple_typemap_object`
(`mappers.py:250-251`) walks dotted keys inefficiently per record. The October 2026
analysis flagged both as the top performance items. Phase 2 of the 2026-10 improvement
roadmap.

## What Changes
- Precompile/normalize date patterns once at module level; cache conversion results
  per distinct input string (`functools.lru_cache` or an explicit bounded dict) so
  repeated values (common in real data) cost one lookup.
- Optimize `simple_typemap_object`'s dotted-key traversal (single split pass, reuse of
  the fixed `set_dict_value` from the Phase 1 change).
- Demote per-value conversion failure logs from INFO to DEBUG (noise reduction at
  scale; also referenced by the error-handling change).
- Add a timing smoke test guarding the improvement.

## Impact
- Affected specs: `processors`
- Affected code: `datacrafter/common/mappers.py`, `datacrafter/common/infer.py`
- No behavior change for valid inputs; conversion results are identical.
