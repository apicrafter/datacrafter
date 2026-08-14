## 1. Implementation
- [x] 1.1 `cmds/project.py:287`: fix `str(e)` → `str(error)` in source-setup except handler
- [x] 1.2 `common/mappers.py:131`: remove unreachable `return string` after `return True`
- [x] 1.3 `common/mappers.py`: document `convert_to_bool` returns `None` for unrecognized input
- [x] 1.4 `common/converters.py:179`: fix `'__init__'` → `'__main__'`

## 2. Tests
- [x] 2.1 Add test: source-setup failure records the real error message, not `NameError`
- [x] 2.2 Add test: `convert_to_bool('true')`→True, `('false')`→False, `('maybe')`→None
- [x] 2.3 Confirm converters module imports cleanly (no syntax errors)

## 3. Verification
- [x] 3.1 `pytest tests/test_mappers.py tests/test_common.py`
- [x] 3.2 `openspec validate fix-latent-code-bugs --strict`
