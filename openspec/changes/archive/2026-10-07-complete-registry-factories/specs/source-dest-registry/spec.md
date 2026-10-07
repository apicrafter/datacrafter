## MODIFIED Requirements
### Requirement: Decorator-Based Source & Destination Registry
Sources and destinations SHALL register themselves via a decorator
(`@register_source` / `register_destination`) into a module-level registry. Each
registered class SHALL own its construction through a `from_config` classmethod that
validates its own required options, and the factory functions SHALL consist of
registry lookup plus delegation to `from_config` — they MUST NOT contain per-type
constructor branches (if/elif chains) or unreachable fallback raises.

#### Scenario: known type resolves
- **WHEN** `get_source_from_file` is called with `stype="csv"`
- **THEN** it returns an instance of the CSV source class registered under that name

#### Scenario: unknown type raises a clear error
- **WHEN** `get_source_from_file` is called with an unrecognized `stype`
- **THEN** it raises `UnknownSourceTypeError` whose message lists the registered source types

#### Scenario: new plugin needs no factory edit
- **WHEN** a new source class is defined with `@register_source("mytype")` and a
  `from_config` classmethod
- **THEN** it is constructible through the factory without modifying any factory code

## ADDED Requirements
### Requirement: Extractor Run Template Method
`BaseExtractor.run()` SHALL be a template method performing validation, result reset,
delegation to a subclass `_execute()` implementation, and state commit; each extractor
subclass SHALL own its mode's execution logic, and identical `run()` bodies MUST NOT
be duplicated across subclasses.

#### Scenario: each extractor type runs its own mode logic
- **WHEN** any registered extractor type runs
- **THEN** validation and state commit happen exactly once via the base template
  method and the type-specific execution logic lives in that extractor's class

#### Scenario: no duplicated run bodies
- **WHEN** extractor subclasses are inspected
- **THEN** none re-implement the validation/reset/commit sequence already provided by
  the base template method
