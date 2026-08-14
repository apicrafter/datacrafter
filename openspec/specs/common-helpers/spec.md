# common-helpers Specification

## Purpose
Defined behavior for type-conversion helpers and accurate source-setup error reporting.
## Requirements
### Requirement: Convert to Bool Has Defined Behavior for All Inputs
The `convert_to_bool` helper SHALL return `True` for canonical truthy strings (`"1"`, `"true"`), `False` for canonical falsy strings (`"0"`, `"false"`), and the original input unchanged for any other value. It MUST NOT contain unreachable code after a return statement.

#### Scenario: canonical true values
- **WHEN** `convert_to_bool` is called with `"1"` or `"true"` (any case)
- **THEN** it returns `True`

#### Scenario: canonical false values
- **WHEN** `convert_to_bool` is called with `"0"` or `"false"` (any case)
- **THEN** it returns `False`

#### Scenario: unrecognized value passes through
- **WHEN** `convert_to_bool` is called with any other string (e.g. `"other"`)
- **THEN** it returns the original string unchanged

### Requirement: Source Setup Error Reporting
When instantiating a source for a resource fails, the orchestrator SHALL record the
actual caught exception in the failed-files report and MUST NOT raise a secondary
`NameError` by referencing an unbound variable.

#### Scenario: source setup fails
- **WHEN** `get_source_from_file` raises an exception for a given resource filename
- **THEN** the failed-files list contains an entry with `error` set to the string of the caught exception, and no `NameError` is raised

