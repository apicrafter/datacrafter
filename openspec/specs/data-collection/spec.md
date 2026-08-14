# data-collection Specification

## Purpose
Security constraints for downloading files and loading YAML project configuration.
## Requirements
### Requirement: Shell-Command-Free External Downloader Invocation
When an external download tool (aria2) is requested, the system SHALL invoke it via
an explicit argument list passed to `subprocess.run` with `shell=False`, and MUST NOT
build a shell string by interpolating URLs, directory paths, filenames, or tool paths.

#### Scenario: aria2 invoked with argument list
- **WHEN** a download is requested with `aria2=True` and a URL containing shell metacharacters (e.g. `; rm -rf /`)
- **THEN** the aria2 tool receives the URL as a single literal argument and no shell command is executed

#### Scenario: no os.system usage in data collection
- **WHEN** the data collection module is inspected
- **THEN** it contains no `os.system` calls

### Requirement: TLS Verification Enabled by Default
The system SHALL verify TLS certificates for all HTTPS downloads by default and MUST
NOT disable certificate verification unless the caller explicitly opts out.

#### Scenario: default download verifies TLS
- **WHEN** a file is downloaded from an HTTPS URL without explicit TLS configuration
- **THEN** the underlying request is made with certificate verification enabled (`verify=True`)

#### Scenario: explicit opt-out is honored
- **WHEN** a caller explicitly requests disabled verification (e.g. `verify_tls=False`)
- **THEN** the request proceeds without certificate verification and a warning is logged

### Requirement: Safe Configuration Loading
The system SHALL load YAML configuration files using `yaml.safe_load` and MUST NOT
use the unsafe full `Loader`/`CLoader` that can construct arbitrary Python objects.

#### Scenario: config with python object tags is rejected
- **WHEN** a `datacrafter.yml` contains a YAML tag that would construct an arbitrary Python object (e.g. `!!python/object/apply:os.system`)
- **THEN** loading raises a `yaml.constructor.ConstructorError` instead of executing the object

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

