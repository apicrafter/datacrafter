# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation updates
- Configuration validation command (`datacrafter config validate`)
- Configuration schema command (`datacrafter config schema`)
- Improved error handling and validation
- Support for structured JSON logging
- Quiet mode for reduced output
- Status command to check pipeline execution state
- Log command to view execution logs
- Check command for configuration and environment validation

### Fixed
- Dependency management: Synchronized dependencies between `setup.py` and `requirements.txt`
- Added missing `dictquery` dependency to requirements
- Created `requirements-pinned.txt` for production builds
- Created `DEPENDENCIES.md` documentation
- Improved logging configuration (default to INFO level)
- Better error messages with actionable suggestions

### Changed
- Default logging level changed from DEBUG to INFO
- Improved CLI structure and organization
- Enhanced configuration validation
- Better error handling throughout the codebase

### Documentation
- Updated README.md with comprehensive installation and usage instructions
- Added command reference section
- Added configuration examples
- Created DEPENDENCIES.md for dependency management
- Improved project documentation structure

## [1.0.2] - 2022-05-15

### Added
- First public release on PyPI
- Updated GitHub code repository
