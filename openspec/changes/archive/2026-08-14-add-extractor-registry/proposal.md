# Change: Register extractors like sources and destinations

## Why
Extractors still dispatch on `type` with a long if/elif in `BaseExtractor.run`,
and `config schema` / validation use a hardcoded type list. Sources and
destinations already use a decorator registry.

## What Changes
- Add `@register_extractor` / `list_extractors()` / `UnknownExtractorTypeError`.
- Split file, API, code, RSS, and DCAT extractors into registered classes.
- Validate and `config schema` use `list_extractors()`.

## Impact
- Affected specs: `source-dest-registry` (or extractor-registry)
- Affected code: `_registry.py`, `extractors/`, `validation.py`, `cmds/project.py`, `core.py`
- Risk: low. YAML types stay the same; factory selects the class.
