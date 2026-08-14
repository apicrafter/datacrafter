## ADDED Requirements

### Requirement: Environment Variable Interpolation
After loading YAML with `safe_load`, the system SHALL replace `${VAR}` in string
values with the corresponding environment variable and `${VAR:-default}` with the
variable or the default. An unset `${VAR}` without a default MUST fail the load.

#### Scenario: secret from environment
- **WHEN** config contains `connstr: ${MONGO_URI}` and `MONGO_URI` is set
- **THEN** the loaded config uses the environment value, not the placeholder

#### Scenario: missing required variable
- **WHEN** config contains `${MISSING_SECRET}` and that variable is unset
- **THEN** loading the project file raises an error naming `MISSING_SECRET`
