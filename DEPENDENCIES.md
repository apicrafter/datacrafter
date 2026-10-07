# Dependency Management

## Overview

This document describes the dependency management strategy for datacrafter.

## Dependency Files

- **requirements.txt** - Runtime dependencies with minimum versions (the single source of
  truth; `pyproject.toml` reads this via `tool.setuptools.dynamic.dependencies`)
- **requirements-dev.txt** - Development tools and test dependencies (also pulls in `requirements.txt`)
- **pyproject.toml** - Package metadata and build configuration; runtime deps sourced from
  `requirements.txt` so the two never drift

## Dependency Synchronization

Runtime dependencies live **only** in `requirements.txt`. The `pyproject.toml`
`[tool.setuptools.dynamic] dependencies = { file = ["requirements.txt"] }` declaration
reads that file at build time, so there is no second copy to keep in sync. To change a
dependency floor, edit `requirements.txt` only.

## Security Scanning

Regularly scan dependencies for security vulnerabilities:

```bash
# Install pip-audit
pip install pip-audit

# Scan for vulnerabilities
pip-audit -r requirements.txt

# Scan with detailed output
pip-audit -r requirements.txt --desc
```

## Updating Dependencies

### For Development
1. Update `requirements.txt` with new minimum versions (this is the single source)
2. Test with: `pip install -r requirements.txt`
3. `pyproject.toml` picks up the change automatically on the next build

### For Production
1. Resolve and install the updated floors in a clean environment
2. Test thoroughly before tagging a release
3. Document any breaking changes

## Dependency Categories

### Core Dependencies
- **typer** - CLI framework
- **pymongo** - MongoDB client (BSON support)
- **tqdm** - Progress bars
- **xlrd** - Excel file reading
- **openpyxl** - Excel file reading/writing

### Network & Web
- **requests** - HTTP library
- **beautifulsoup4** - HTML parsing
- **lxml** - XML/HTML processing

### Optional Extras
- **zstandard** (`pip install datacrafter[compression]`) - .zst compressed files
- **pyarrow** (`pip install datacrafter[parquet]`) - Parquet destination

### Configuration
- **pyyaml** - YAML parsing

### External Tools
- **apibackuper** - API backup tool integration

## Version Constraints

- Use `>=` minimum version floors in `requirements.txt`
- CI audits the resolved environment with pip-audit (PR-time and weekly)
- Regularly update to latest patch versions for security

## Adding New Dependencies

1. Add to `requirements.txt` with a `>=` minimum version (picks up in pyproject.toml automatically)
2. Document in this file
4. Run security scan: `pip-audit -r requirements.txt`

## Removing Dependencies

1. Remove from `requirements.txt`
2. Check for any remaining imports
3. Update this documentation

