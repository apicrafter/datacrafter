# Change: Fix Latent Code Bugs

## Why
Three latent bugs were found that cause wrong runtime behavior or hide real errors:
(1) `NameError` in an except handler in `cmds/project.py:287` (`str(e)` where only
`error` is bound) masks the original failure when setting up a source;
(2) unreachable `return string` after `return True` in `common/mappers.py:131`, and
`convert_to_bool` returns `None` for any non-canonical bool string;
(3) `if __name__ == '__init__'` in `common/converters.py:179` can never be true — the
CLI entry block is dead and never runs (should be `__main__`).

## What Changes
- `cmds/project.py:287`: change `str(e)` → `str(error)` so the caught exception is
  recorded instead of raising `NameError`.
- `common/mappers.py:131`: the unreachable `return string` is actually the intended
  fallback. Reimplement so unrecognized values return the original input unchanged
  (confirmed by `tests/test_mappers.py:42` which asserts `convert_to_bool("other") == "other"`).
- `common/converters.py:179`: fix `'__init__'` → `'__main__'` so the module is runnable
  as a CLI script when intended.

## Impact
- Affected specs: `common-helpers`
- Affected code: `datacrafter/cmds/project.py`, `datacrafter/common/mappers.py`,
  `datacrafter/common/converters.py`
- Risk: very low; pure bug fixes restoring intended behavior.
