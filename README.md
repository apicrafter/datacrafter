# Datacrafter - NoSQL ETL Tool

**Datacrafter** is an open-source NoSQL ETL (Extract, Transform, Load) tool designed for data extraction, transformation, and loading with a focus on NoSQL data formats. It provides a command-line interface for building data pipelines that extract data from various sources, process it, and load it into different destinations.

> **Note:** This project is in alpha stage. Code migration from a closed repository is in progress, and documentation is being continuously improved.

## Features

- **NoSQL-first approach**: JSON Lines and BSON are default file formats
- **Task chaining and data pipelines**: Build complex ETL workflows
- **Command-line first**: Full CLI interface for automation and scripting
- **Automated data extraction**: Extract data from APIs, files, and web sources
- **Semantic type identification**: Automatic data type detection and conversion
- **Automatic documentation generation**: Generate documentation for your data pipelines
- **Data discovery**: Discover data formats and possible transformations
- **Multiple source and destination formats**: Support for various file formats and databases

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

- Python 3.8 or higher
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
    autoid: true
    autotype: true
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
```

### 4. Check Status

```bash
datacrafter status
```

## Command Reference

### Main Commands

- `datacrafter init [--path PATH] [--name NAME]` - Initialize a new project
- `datacrafter run [--path PATH] [--verbose] [--quiet]` - Execute the data pipeline
- `datacrafter status [--path PATH]` - Show status of latest pipeline execution
- `datacrafter check [--path PATH]` - Validate configuration and environment
- `datacrafter clean [--path PATH] [--storage]` - Remove temporary files
- `datacrafter log [--path PATH] [--lines N]` - Show log of latest operations
- `datacrafter version` - Show version information

### Configuration Commands

- `datacrafter config validate [--path PATH]` - Validate project configuration
- `datacrafter config schema` - Show expected configuration file schema

### Planned Commands

- `datacrafter schema` - Generate and print data schema
- `datacrafter metrics` - Show dataset statistics and analysis
- `datacrafter builds` - Manage builds (create, remove, list)
- `datacrafter push` - Push data to remote storage
- `datacrafter ui` - Launch web user interface

## Core Concepts

### Extractors

Extractors pull data from various sources:

- **Local or remote files**: CSV, JSON, XML, XLS/XLSX, BSON, JSONL
- **APIs**:
  - REST API (Work in progress)
  - APIBackuper compatible (Done)
  - RSS/Atom Feed (Work in progress)
- **CMS**:
  - WordPress (Work in progress)
  - Microsoft SharePoint (Planned)
- **Common APIs** (Planned):
  - Email, FTP, SFTP
- **Online services** (Planned):
  - Yandex Metrika, Yandex.Webmaster

### Sources

Sources are files or databases created by extractors:

**File Sources:**
- JSON Lines ✅
- CSV ✅
- BSON ✅
- XLS/XLSX ✅
- XML ✅
- JSON (Work in progress)
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
- **Custom code**: Python scripts for data manipulation ✅
- **Custom tools**: Command-line tools for data manipulation (Work in progress)
- **Enrichers**: Data and metadata enrichment (Planned)

### Destinations

Destinations store the processed data:

**File Destinations:**
- BSON ✅
- JSON Lines ✅
- CSV ✅
- Parquet (Work in progress)
- JSON (Work in progress)
- YAML (Planned)
- DataPackage/Frictionless Data (Planned)

**Database Destinations:**
- MongoDB (Work in progress)
- ArangoDB (Planned)
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
├── data/                # Extracted data
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
    autoid: true               # Auto-generate IDs
    autotype: false            # Auto-detect types
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
  type: "file-jsonl"           # file-jsonl, file-csv, file-bson, mongodb, etc.
  fileprefix: "output"
  compress: "gz"               # Optional: gz, bz2, xz, zip, zst
```

## Examples

For complete examples, see: https://github.com/apicrafter/datacrafter-examples

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
    autoid: true
    autotype: true

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
  config:
    autoid: true
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
pytest
```

### Code Quality

```bash
# Linting with pylint
pylint datacrafter/

# Linting with flake8
flake8 datacrafter/

# Type checking (if using mypy)
mypy datacrafter/
```

**Code Quality Status**: The codebase maintains a pylint score of 9.12/10, with comprehensive code quality improvements implemented in version 1.0.4.

### Contributing

Contributions are welcome! Please see the [IMPROVEMENTS.md](IMPROVEMENTS.md) file for areas that need work.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Documentation

- [Dependencies](DEPENDENCIES.md) - Dependency management guide
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Known issues and improvement suggestions
- [CHANGELOG.md](CHANGELOG.md) - Version history

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Support

- **Issues**: https://github.com/apicrafter/datacrafter/issues
- **Examples**: https://github.com/apicrafter/datacrafter-examples

## Author

Ivan Begtin

---

**Status**: Alpha - Active development in progress
