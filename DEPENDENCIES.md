# Dependency Management

## Overview

This document describes the dependency management strategy for datacrafter.

## Dependency Files

- **requirements.txt** - Runtime dependencies with minimum versions (the single source of
  truth; `pyproject.toml` reads this via `tool.setuptools.dynamic.dependencies`)
- **requirements-pinned.txt** - Production dependencies with exact versions (for reproducible builds)
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
1. Update `requirements-pinned.txt` with exact versions
2. Test thoroughly before deployment
3. Document any breaking changes

## Dependency Categories

### Core Dependencies
- **chardet** - Character encoding detection
- **typer** - CLI framework
- **jsonlines** - JSON Lines file handling
- **orjson** - Fast JSON parsing
- **pandas** - Data manipulation
- **pymongo** - MongoDB client
- **qddate** - Date parsing
- **tabulate** - Table formatting
- **tqdm** - Progress bars
- **validators** - Input validation
- **xlrd** - Excel file reading
- **openpyxl** - Excel file writing

### Network & Web
- **requests** - HTTP library
- **beautifulsoup4** - HTML parsing
- **lxml** - XML/HTML processing

### Data Processing
- **dictquery** - Dictionary querying (optional, for advanced queries)

### Configuration
- **pyyaml** - YAML parsing

### External Tools
- **apibackuper** - API backup tool integration

## Version Constraints

- Use `>=` for minimum versions in development (allows patch updates)
- Use `==` for exact versions in production (reproducible builds)
- Regularly update to latest patch versions for security

## Adding New Dependencies

1. Add to `requirements.txt` with a `>=` minimum version (picks up in pyproject.toml automatically)
2. Update `requirements-pinned.txt` with the resolved version if needed
3. Document in this file
4. Run security scan: `pip-audit -r requirements.txt`

## Removing Dependencies

1. Remove from `requirements.txt`
2. Remove from `requirements-pinned.txt`
3. Check for any remaining imports
4. Update this documentation

