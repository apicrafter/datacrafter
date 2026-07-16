# Change: General Code Quality Improvements

## Why
Several maintainability issues remain after the targeted fixes: type hints are
essentially absent package-wide (only ~4 functions in `core.py` annotated); constants
are duplicated (`SUPPORTED_FILE_TYPES` in both `constants.py` and `destinations/base.py`;
`DEFAULT_MAX_RETRIES` in both `constants.py` and `collect.py`); logging configuration
is triple-defined (`__main__.py`, `core.py`, `project.py`) with a no-op tautology at
`project.py:81`; broad `except Exception: pass` swallows errors silently
(`destinations/base.py:186,195,214`); minor typos (`DEFAILT_CONFIG`, docstring typos).

## What Changes
- De-duplicate constants into `constants.py` as the single source; remove the copies.
- Consolidate logging configuration into one place; fix the `project.py:81` tautology.
- Replace `except Exception: pass` with logged exceptions (or narrow exception types).
- Add type hints incrementally, starting with the base-class protocols
  (`BaseSource`, `BaseDestination`, `CommonProcessor`) and pure helper functions.
- Fix typos: `DEFAILT_CONFIG` → `DEFAULT_CONFIG`; docstring typos.

## Impact
- Affected specs: `code-quality`
- Affected code: `datacrafter/constants.py`, `datacrafter/destinations/base.py`,
  `datacrafter/common/collect.py`, `datacrafter/cmds/project.py`, `datacrafter/__main__.py`,
  `datacrafter/core.py`, base classes, typos throughout
- Risk: low–medium; mostly mechanical. Type hints are additive; constant de-dup must
  preserve values.
