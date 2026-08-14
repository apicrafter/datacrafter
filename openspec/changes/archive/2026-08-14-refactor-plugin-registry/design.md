## Context
Sources and destinations are currently selected by long if/elif chains keyed on the
config `type` string. This is hard to extend and not discoverable. A registry pattern
decouples declaration from dispatch.

## Goals / Non-Goals
- Goals: single point of registration per format; clear errors on unknown types;
  identical public API; ability to list available types (for `config schema`).
- Non-Goals: runtime third-party plugin loading via entry points (deferred); changing
  the config YAML schema.

## Decisions
- **Decorator registry** (`@register_source(name)` / `@register_destination(name)`).
  Each format module applies the decorator at class level and is imported by the
  package `__init__` so registration happens on import.
- Registry stored in a module-level `dict` in a new `_registry.py` shared helper.
- Unknown types raise a typed exception with a message listing known types.

## Alternatives considered
- **Setuptools entry points:** allows external plugins but adds complexity; deferred.
- **Dict literal in `__init__.py`:** simpler than if/elif but still centralizes; rejected
  in favor of decorators so each format lives with its implementation.

## Risks / Trade-offs
- Must ensure import side-effects run: registry relies on all format modules being
  imported. Mitigation: `sources/__init__.py` explicitly imports every submodule.
- Decorator on class is slightly unusual; mitigation: thin wrapper returning the class
  unchanged.

## Migration Plan
1. Add `_registry.py` with `register_source`/`register_destination` + lookup funcs.
2. Add decorators to each existing source/destination class.
3. Rewrite the two factory functions to use lookup.
4. Run full suite; add a test that every documented type resolves.

## Open Questions
- Should we expose `list_sources()`/`list_destinations()` for `config schema` output?
  (Yes — cheap and useful; include in tasks.)
