## Context
`_registry.py` already provides decorator registration and typed unknown-type errors,
but per-type construction kwargs live in factory if/elif chains
(`sources/__init__.py:151-197`, `destinations/__init__.py:61-113`), and extractors
duplicate an identical 5-line `run()` across five subclasses while the base class
carries five `_run_*` mode implementations (`extractors/base.py:99-191`).

## Goals / Non-Goals
- Goals: adding a plugin = writing one class + decorator; factories contain no
  per-type branches; extractor run logic lives with its extractor.
- Non-Goals: config schema/DSL changes, new plugin types, entry-point-based external
  plugin loading (possible future extension of the same registry).

## Decisions
- Decision: `from_config(filename=None, stream=None, options=None)` classmethod on each
  plugin class. The class owns validation of its required options (shared
  `require_options(options, [...])` helper), so the factory is only
  lookup → `from_config`.
  - Alternatives: dataclass-based config descriptors (more machinery than the 8 plugin
    types warrant today); keeping kwargs in factories (status quo — every new type
    edits two places).
- Decision: extractors get a template method `run()` on the base that calls
  `self.validate()`, resets results, dispatches to an overridable `_execute()` (default
  per mode), and commits state. Each subclass implements `_execute()` with the logic
  currently in `BaseExtractor._run_file/_run_rss/_run_dcat/_run_api/_run_code`.
  - Alternatives: keep `_run_*` on the base (mode logic stays remote from subclasses);
    full command-pattern objects (over-engineering at five modes).
- Decision: compressed-stream opening moves into the source `from_config`
  implementations (building on Phase 1's stream ownership fix), so the factory no
  longer pre-opens streams.

## Risks / Trade-offs
- Subtle behavior drift while moving kwargs → covered by running existing factory
  tests unchanged (2.1) as a compatibility gate.
- `from_config` becomes an implicit plugin contract — document it on the base ABCs
  once typing lands (ties into the typing change).

## Migration Plan
1. Add `from_config` to sources + rewrite source factory (destinations untouched).
2. Same for destinations.
3. Extractor template method.
Each step ships green independently; rollback is per-step revert.

## Open Questions
- Should `from_config` also absorb the `compress`/`compression` destination option
  parsing currently spread between factory and `BaseFileDestination.__init__`?
