# Change: Refactor Source/Destination Factories to Plugin Registry

## Why
`sources/__init__.py:85-193` and `destinations/__init__.py:37-98` are ~110- and
~60-line if/elif chains dispatching on config `type`. The code itself flags this:
*"Temporary function... Should be replaced in the future"* and *"#TODO Make me
pluginnable"*. Adding a new source/destination requires editing the factory in two
places, and the registry is not extensible by third-party plugins.

## What Changes
- Introduce a decorator-based registry pattern: `@register_source("file-csv")` and
  `@register_destination("file-jsonl")` that populate module-level dicts.
- Rewrite `get_source_from_file()` and `get_destination_from_config()` to look up the
  registry dict, raising a clear `UnknownSourceTypeError`/`UnknownDestinationTypeError`
  on unknown types (instead of falling through silently).
- Move each `register_*` call to the relevant module so a new format is added in one
  place. Ensure all source/destination modules are imported by the package `__init__`
  so decorators run at import time.
- Preserve the public API (`get_source_from_file`, `get_destination_from_config`).

## Impact
- Affected specs: `source-dest-registry`
- Affected code: `datacrafter/sources/__init__.py`, `datacrafter/destinations/__init__.py`,
  each `sources/*.py` and `destinations/*.py` (decorator addition)
- Risk: medium — touches the core dispatch path; must keep all existing types working.
