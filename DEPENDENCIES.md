# Dependency Management

## Overview

This document describes the dependency management strategy for datacrafter.

## Dependency Files

- **requirements.txt** - Development dependencies with minimum versions (allows patch updates)
- **requirements-pinned.txt** - Production dependencies with exact versions (for reproducible builds)
- **requirements-dev.txt** - Development tools and test dependencies
- **setup.py** - Package installation dependencies (should match requirements.txt)

## Dependency Synchronization

The dependencies in `setup.py` should match `requirements.txt`. Both files are maintained manually and should be kept in sync.

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
1. Update `requirements.txt` with new minimum versions
2. Update `setup.py` to match
3. Test with: `pip install -r requirements.txt`

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

1. Add to `requirements.txt` with minimum version
2. Add to `setup.py` `install_requires`
3. Update `requirements-pinned.txt` if needed
4. Document in this file
5. Run security scan: `pip-audit -r requirements.txt`

## Removing Dependencies

1. Remove from `requirements.txt`
2. Remove from `setup.py`
3. Remove from `requirements-pinned.txt`
4. Check for any remaining imports
5. Update this documentation

