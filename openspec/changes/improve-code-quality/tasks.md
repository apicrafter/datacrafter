## 1. Implementation
- [ ] 1.1 Remove duplicate `SUPPORTED_FILE_TYPES` from `destinations/base.py:10-12` (import from constants)
- [ ] 1.2 Remove duplicate `DEFAULT_MAX_RETRIES` from `common/collect.py:23` (import from constants)
- [ ] 1.3 Consolidate logging setup: one `basicConfig` location; remove redundant calls in `__main__.py`/`core.py`
- [ ] 1.4 Fix `project.py:81` tautology (`logging.DEBUG if ... else logging.DEBUG`)
- [ ] 1.5 Replace `except Exception: pass` at `destinations/base.py:186,195,214` with logged narrow handling
- [ ] 1.6 Fix typo `DEFAILT_CONFIG` → `DEFAULT_CONFIG` (`processors/base.py:225`)
- [ ] 1.7 Fix docstring typos (`destinations/base.py:238` "indexedr", etc.)
- [ ] 1.8 Add type hints to `BaseSource`/`BaseDestination`/`BaseFileSource`/`BaseFileDestination` protocols
- [ ] 1.9 Add type hints to pure helpers in `common/mappers.py`, `common/common.py`

## 2. Verification
- [ ] 2.1 `pytest` green
- [ ] 2.2 `pylint` no new errors; ideally fewer
- [ ] 2.3 `grep -rn "DEFAILT\|verify=False\|os.system" datacrafter/` returns nothing
- [ ] 2.4 `openspec validate improve-code-quality --strict`
