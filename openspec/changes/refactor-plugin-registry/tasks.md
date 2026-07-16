## 1. Implementation
- [ ] 1.1 Create `datacrafter/sources/_registry.py` with `register_source`, `get_source`, `list_sources`, `UnknownSourceTypeError`
- [ ] 1.2 Create `datacrafter/destinations/_registry.py` (mirrored)
- [ ] 1.3 Apply `@register_source("file-csv")` etc. to each class in sources/*.py
- [ ] 1.4 Apply `@register_destination(...)` to each class in destinations/*.py
- [ ] 1.5 Rewrite `get_source_from_file()` to use registry lookup
- [ ] 1.6 Rewrite `get_destination_from_config()` to use registry lookup
- [ ] 1.7 Ensure all format modules imported in package `__init__`
- [ ] 1.8 Expose `list_sources()`/`list_destinations()` for config schema command

## 2. Tests
- [ ] 2.1 Test each documented config type resolves to the correct class
- [ ] 2.2 Test unknown type raises `UnknownSourceTypeError`/`UnknownDestinationTypeError` with helpful message
- [ ] 2.3 Test `list_sources()`/`list_destinations()` return all registered names

## 3. Verification
- [ ] 3.1 `pytest tests/test_sources.py tests/test_destinations.py`
- [ ] 3.2 `openspec validate refactor-plugin-registry --strict`
