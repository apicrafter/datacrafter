## 1. Implementation
- [x] 1.1 Create `datacrafter/_registry.py` with `register_source`, `get_source_class`, `list_sources`, `UnknownSourceTypeError`
- [x] 1.2 Create destination registry (same module: `register_destination`, `list_destinations`)
- [x] 1.3 Apply `@register_source(...)` to each class in sources/*.py
- [x] 1.4 Apply `@register_destination(...)` to each class in destinations/*.py (including couchdb)
- [x] 1.5 Rewrite `get_source_from_file()` to construct instances from the registry class (still if/elif kwargs)
- [x] 1.6 Rewrite `get_destination_from_config()` to construct instances from the registry class (still if/elif kwargs)
- [x] 1.7 Ensure all format modules imported in package `__init__`
- [x] 1.8 Expose `list_sources()`/`list_destinations()` for config schema command

## 2. Tests
- [x] 2.1 Test each documented config type resolves to the correct class
- [x] 2.2 Test unknown type raises `UnknownSourceTypeError`/`UnknownDestinationTypeError` with helpful message
- [x] 2.3 Test `list_sources()`/`list_destinations()` return all registered names

## 3. Verification
- [x] 3.1 `pytest tests/test_sources.py tests/test_destinations.py`
- [x] 3.2 `openspec validate refactor-plugin-registry --strict`
