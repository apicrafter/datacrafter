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

### Requirement: Enclosure Filenames Confined to Destination Directory
Filenames derived from untrusted remote feed entries (RSS/Atom enclosures, DCAT
`downloadURL`) SHALL be sanitized before being joined into the project's `current/`
directory: empty names, `.`, `..`, and path separator characters (including
backslashes) MUST be rejected or stripped, so a crafted URL cannot cause a write
outside the destination directory.

#### Scenario: traversal via dot-dot suffix is blocked
- **WHEN** a feed enclosure URL ends with `/..`
- **THEN** the downloaded file is written inside `current/` under a safe name and no
  file is created outside it

#### Scenario: backslash separators are neutralized
- **WHEN** a DCAT `downloadURL` path contains backslash-separated segments
- **THEN** the resulting local filename contains no path separators

### Requirement: Query Strings Redacted in Persisted Logs
URLs logged at INFO level or above SHALL have their query strings redacted, because
query parameters may carry credentials; the full URL MAY be logged at DEBUG level.
Connection strings and secrets MUST NOT be written to the log file.

#### Scenario: API key not persisted at INFO
- **WHEN** a download URL containing `?api_key=secret` is retrieved with default
  verbosity
- **THEN** the persisted log line does not contain `secret`

### Requirement: Extractor Security Options Reach the Downloader
The extractor configuration keys `verify_tls`, `timeout`, and `aria2` SHALL be
forwarded to the underlying download functions, and MUST match the behavior documented
in `docs/docs/configuration/security.md`. TLS verification remains the default; an
explicit opt-out logs a warning.

#### Scenario: configured timeout is honored
- **WHEN** an extractor config sets `timeout: 10` and the download is mocked
- **THEN** the request is made with `timeout=10`

#### Scenario: verify opt-out from config is honored with warning
- **WHEN** an extractor config sets `verify_tls: false`
- **THEN** the request is made without certificate verification and a warning is logged

