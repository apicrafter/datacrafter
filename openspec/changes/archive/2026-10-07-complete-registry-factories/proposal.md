# Change: Complete registry adoption with from_config constructors

## Why
The decorator registry is only half-adopted: after registry lookup resolves the class,
the factories still hand-code constructor kwargs through 8-branch `if stype == ...`
chains (`sources/__init__.py:151-197`, with a provably dead trailing raise;
`destinations/__init__.py:61-113`), and the five extractor subclasses contain
byte-identical `run()` bodies while all logic lives in `BaseExtractor._run_*`
(`extractors/base.py:99-191`). Adding a new plugin therefore requires editing a
factory, defeating the registry's purpose. Phase 3 of the 2026-10 improvement roadmap.

## What Changes
- Give each source and destination class a `from_config(filename, options)`
  classmethod that owns its own kwargs; factories shrink to registry lookup +
  validation + `from_config`.
- Delete the if/elif chains and the dead trailing raises in both factories.
- Make `BaseExtractor.run()` a template method dispatching to the registered mode;
  delete the five duplicated subclass `run()` bodies (each `_run_*` moves to its
  subclass or stays on the base — decided in design).
- `datacrafter config schema` output stays unchanged (same types listed).

## Impact
- Affected specs: `source-dest-registry`
- Affected code: `datacrafter/sources/*.py`, `datacrafter/destinations/*.py`,
  `datacrafter/sources/__init__.py`, `datacrafter/destinations/__init__.py`,
  `datacrafter/extractors/base.py`, `datacrafter/extractors/{file,rss,dcat,api,code}.py`
- Depends on: `fix-source-dest-stream-bugs` (compressed-source dispatch moves into
  `from_config`).
