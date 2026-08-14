# Datacrafter - NoSQL ETL Tool

**Datacrafter** is an open-source NoSQL ETL (Extract, Transform, Load) tool designed for data extraction, transformation, and loading with a focus on NoSQL data formats. It provides a command-line interface for building data pipelines that extract data from various sources, process it, and load it into different destinations.

> **Note:** This project is in alpha stage. Code migration from a closed repository is in progress, and documentation is being continuously improved.

## Features

- **NoSQL-first**: JSON Lines and BSON are the native intermediate formats
- **CLI-first YAML projects**: declare extract → process → load in `datacrafter.yml`
- **File and URL extraction**: CSV, JSON, JSONL, XML, XLS/XLSX, ZIP+XML, patterned HTML indexes, RSS/Atom, DCAT catalogs, APIBackuper, trusted Python `collect()` scripts
- **Record transforms**: `keymap`, `typemap`, custom Python `process(record)`, plus optional `autotype` (sample-based type inference) and `autoid` (stable `_id`)
- **Inspect**: `datacrafter schema` and `datacrafter metrics` read JSONL in `output/` (or `current/`)
- **Dry-run**: `datacrafter run --dry-run` validates config and prints a plan without downloading or writing
- **Destinations**: JSONL, BSON, CSV, Parquet (optional `pyarrow`), MongoDB, ArangoDB, CouchDB, Meilisearch
- **Open-data packaging**: `datapackage.json` beside file output; `${MONGO_URI}` / `${VAR:-default}` in YAML
- **Multiple extractors**: `extractors:` list sharing one processor and destination

Reserved in CLI but **not implemented yet**: `builds` / `push` / `ui`, automatic docs generation.

## Installation

### Using pip (Recommended)

```bash
pip install datacrafter
```

### From Source

```bash
git clone https://github.com/apicrafter/datacrafter.git
cd datacrafter
pip install -e .
```

### Requirements

- Python 3.9 or higher
- See [requirements.txt](requirements.txt) for full dependency list

## Quick Start

### 1. Initialize a Project

```bash
datacrafter init my-project
cd my-project
```

This creates a new project directory with a `datacrafter.yml` configuration file.

### 2. Configure Your Pipeline

Edit `datacrafter.yml` to define your data pipeline:

```yaml
version: "1"
project-name: "my-project"
project-id: "unique-id"

extractor:
  mode: "singlefile"
  type: "file-csv"
  method: "url"
  config:
    url: "https://example.com/data.csv"

processor:
  config:
    autotype: true
    autoid: true
    error_strategy: "skip"
  keymap:
    type: "names"
    fields:
      old_column: "new_column"

destination:
  type: "file-jsonl"
  fileprefix: "output"
```

### 3. Run Your Pipeline

```bash
datacrafter run
datacrafter run --dry-run
datacrafter schema
datacrafter metrics
```

### 4. Check Status

```bash
datacrafter status
```

## Command Reference

### Main Commands

- `datacrafter init [DIRECTORY] [--path PATH] [--name NAME]` - Initialize a new project
- `datacrafter run [--path PATH] [--verbose] [--quiet] [--dry-run]` - Execute the data pipeline (or print a plan)
- `datacrafter status [--path PATH]` - Show status of latest pipeline execution
- `datacrafter check [--path PATH]` - Validate configuration and environment
- `datacrafter clean [--path PATH] [--storage]` - Remove temporary files
- `datacrafter log [--path PATH] [--lines N]` - Show log of latest operations
- `datacrafter schema [--path PATH]` - Infer field types from output JSONL
- `datacrafter metrics [--path PATH]` - Record counts and field histograms
- `datacrafter version` - Show version information

### Configuration Commands

- `datacrafter config validate [--path PATH]` - Validate project configuration
- `datacrafter config schema` - Show expected configuration file schema

### Planned Commands

- `datacrafter builds` - Manage builds (create, remove, list)
- `datacrafter push` - Push data to remote storage
- `datacrafter ui` - Launch web user interface

## Core Concepts

### Extractors

Extractors pull data from various sources:

- **Local or remote files**: CSV, JSON, XML, XLS/XLSX, BSON, JSONL, ZIP
- **APIs and catalogs**:
  - APIBackuper ✅
  - RSS/Atom feeds ✅
  - DCAT catalogs ✅
  - REST API (generic HTTP beyond URL/file download: Work in progress)
- **CMS** (Planned): WordPress, Microsoft SharePoint
- **Common APIs** (Planned): Email, FTP, SFTP
- **Online services** (Planned): Yandex Metrika, Yandex.Webmaster

### Sources

Sources are files or databases created by extractors:

**File Sources:**
- JSON Lines ✅
- CSV ✅
- BSON ✅
- XLS/XLSX ✅
- XML ✅
- JSON ✅
- YAML (Work in progress)
- SQLite (Work in progress)

**Database Sources (Planned):**
- SQL databases via SQLAlchemy
- PostgreSQL, ClickHouse
- MongoDB, ArangoDB, ElasticSearch/OpenSearch

### Processors

Processors transform data during the pipeline:

- **Mappers**: Map data fields from one schema to another
  - `keymap`: Replace key/column names ✅
  - `typemap`: Convert data types ✅
- **Custom code**: Python scripts under the project directory ✅
- **Custom tools**: Command-line tools for data manipulation (Work in progress)
- **Enrichers**: Data and metadata enrichment (Planned)

### Destinations

Destinations store the processed data:

**File Destinations:**
- BSON ✅
- JSON Lines ✅
- CSV ✅
- Parquet ✅
- Frictionless Data Package (`datapackage.json` beside file output) ✅
- JSON (Work in progress)
- YAML (Planned)

**Database Destinations:**
- MongoDB ✅
- ArangoDB ✅
- CouchDB ✅
- Meilisearch ✅
- ClickHouse (Planned)
- Any SQL via SQLAlchemy (Planned)

**Storage Options (Planned):**
- Local filesystem ✅
- S3, FTP, SFTP
- WebDAV, Google Drive, Dropbox, Yandex.Disk

### Buzzers

Alerting mechanisms (Planned):
- Email alerts
- Other notification methods

## Configuration

### Project Structure

A datacrafter project typically has this structure:

```
my-project/
├── datacrafter.yml      # Project configuration
├── current/             # Extracted data
├── output/              # Processed output
├── state.json           # Execution state
└── datacrafter.log      # Execution logs
```

### Configuration Schema

See the full configuration schema:

```bash
datacrafter config schema
```

Or check the example below:

```yaml
version: "1"
project-name: "my-project"
project-id: "unique-id"

extractor:
  mode: "singlefile"           # singlefile, api, code
  type: "file-csv"             # file-csv, file-json, file-xml, etc.
  method: "url"                # url, urlbypattern, apibackuper
  force: true                  # Force re-download
  config:
    url: "https://example.com/data.csv"

processor:
  config:
    error_strategy: "skip"     # skip, fail, retry
    max_retries: 3
  keymap:                      # Optional field mapping
    type: "names"
    fields:
      old_name: "new_name"
  typemap:                     # Optional type conversion
    field_name: "int"          # int, float, date, datetime, bool
  custom:                      # Optional custom code
    type: "script"
    code: "path/to/script.py"

destination:
  type: "file-jsonl"           # file-jsonl, file-csv, file-bson, file-parquet, mongodb, arangodb, couchdb, meilisearch
  fileprefix: "output"
  compress: "gz"               # Optional: gz, bz2, xz, zip, zst
```

## Examples

Starter `datacrafter.yml` recipes live in [`examples/`](examples/README.md) (CSV URL, Excel, ZIP+XML, APIBackuper, RSS, DCAT). More recipes: https://github.com/apicrafter/datacrafter-examples

### Example: Extract CSV and Convert to JSONL

```yaml
version: "1"
project-name: "csv-to-jsonl"
project-id: "example-1"

extractor:
  mode: "singlefile"
  type: "file-csv"
  method: "url"
  config:
    url: "https://example.com/data.csv"

processor:
  config:
    error_strategy: "skip"

destination:
  type: "file-jsonl"
  fileprefix: "output"
```

### Example: Extract from API and Store in MongoDB

```yaml
version: "1"
project-name: "api-to-mongo"
project-id: "example-2"

extractor:
  mode: "api"
  type: "api"
  method: "apibackuper"
  config:
    endpoint: "https://api.example.com/data"

processor:
  keymap:
    type: "names"
    fields:
      api_id: "_id"
      api_name: "name"

destination:
  type: "mongodb"
  connstr: "mongodb://localhost:27017"
  dbname: "mydb"
  tablename: "mydata"
```

## Development

### Running Tests

```bash
# Install dev dependencies (includes pytest, coverage, pip-audit)
pip install -r requirements-dev.txt
pip install -e .

# Run the test suite with coverage (enforces a 50% floor in .coveragerc)
pytest

# Audit dependencies for known vulnerabilities
pip-audit -r requirements.txt
```

### Code Quality

```bash
# Linting with pylint
pylint datacrafter/

# Linting with ruff (also run via pre-commit)
ruff check datacrafter tests

# Type checking (if using mypy)
mypy datacrafter/
```

### Building & Packaging

The project uses modern PEP 621 packaging (`pyproject.toml`); `setup.py` is kept
only as a compatibility shim. Runtime dependencies are sourced from
`requirements.txt` (single source of truth).

```bash
python -m build       # produces wheel + sdist in dist/
```

CI runs the test matrix (Python 3.9–3.13), pip-audit, and publishes to PyPI on tag
via Trusted Publishing. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for setup,
testing, linting, branching conventions, and the pull-request process.

1. Fork the repository
2. Create a feature branch (`feat/...`) or fix branch (`fix/...`)
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - How to set up and contribute
- [Dependencies](DEPENDENCIES.md) - Dependency management guide
- [CHANGELOG.md](CHANGELOG.md) - Version history

## Security

**Trust model.** Datacrafter runs configuration files (`datacrafter.yml`) and
`code`-type extractor / custom processor scripts as **trusted** input — these can
execute arbitrary Python (via `runpy`) and should only come from a source you
control. Scripts MUST resolve inside the project directory. URLs, filenames,
and downloaded data are treated as **untrusted** and are never passed to a shell.
Secrets belong in the environment (`connstr: ${MONGO_URI}`), not in committed YAML.

- TLS certificate verification is **enabled by default** for all HTTPS downloads.
  Disable it only for trusted endpoints with a known self-signed cert (a warning is
  logged).
- To report a security vulnerability, please open a private advisory via
  [GitHub Security Advisories](https://github.com/apicrafter/datacrafter/security/advisories/new)
  rather than a public issue.

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Support

- **Issues**: https://github.com/apicrafter/datacrafter/issues
- **Examples**: https://github.com/apicrafter/datacrafter-examples

## Author

Ivan Begtin

---

**Status**: Alpha - Active development in progress
