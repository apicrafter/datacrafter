# source-dest-io Specification

## Purpose
TBD - created by archiving change fix-source-dest-stream-bugs. Update Purpose after archive.
## Requirements
### Requirement: Compressed Sources Parse Correctly
When a resource file with a supported compression suffix (`.gz`, `.bz2`, `.xz`, `.zst`)
is opened for any text-based source type (csv, json, jsonl, xml, and any other type
that reads the file as text), the source SHALL read the decompressed content, and the
decompression stream SHALL be owned by the source and closed with it. Formats that
cannot consume a text stream (e.g. binary `bson`, `xls`/`xlsx` workbooks) MUST raise a
clear configuration error when compression is requested instead of silently reading
compressed bytes.

#### Scenario: gzipped CSV reads as CSV
- **WHEN** `get_source_from_file` opens a `data.csv.gz` with `stype="csv"`
- **THEN** the returned source yields the same records as the uncompressed `data.csv`

#### Scenario: unsupported compression combination fails clearly
- **WHEN** compression is requested for a source type that cannot read a decompressed
  text stream
- **THEN** a configuration error naming the type and compression is raised, and no
  stream is left open

### Requirement: Streaming Sources Are Re-Iterable Without Unbounded Memory
Every file source SHALL support at least two full iteration passes over the same
instance yielding identical record sequences, and streaming XML iteration MUST release
parsed elements (`elem.clear()` or equivalent) so memory does not grow with file size.

#### Scenario: second pass yields the same records
- **WHEN** a source instance is iterated to completion and then iterated again
- **THEN** the second pass yields the same record sequence as the first

#### Scenario: large XML memory stays bounded
- **WHEN** an XML source iterates a file with many repeating tag entries
- **THEN** parsed elements are released during iteration and memory usage does not
  grow proportionally to the record count

### Requirement: Complete and Idempotent Stream Closure
File destinations SHALL close every stream they own — the output file, the archive
object, and any underlying wrapped file — exactly once, and `__del__` MUST delegate to
the same `close()` path so an instance garbage-collected without explicit `close()`
still produces a valid archive. Destinations SHALL also be usable as context managers.
Sources constructed without a usable input (`filename` and `stream` both `None`) MUST
raise a clear configuration error at construction time.

#### Scenario: garbage-collected ZIP destination stays valid
- **WHEN** a ZIP destination receives records and is garbage-collected without an
  explicit `close()`
- **THEN** the archive on disk is valid and contains the written entries

#### Scenario: destination as context manager
- **WHEN** a destination is used in a `with` block and records are written
- **THEN** all owned streams are closed on block exit without an explicit `close()` call

#### Scenario: invalid source construction fails fast
- **WHEN** a file source is constructed with neither `filename` nor `stream`
- **THEN** construction raises a `ValueError` naming the missing input

