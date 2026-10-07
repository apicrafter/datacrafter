## ADDED Requirements
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
