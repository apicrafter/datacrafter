## 1. Implementation
- [ ] 1.1 Replace `os.system(s)` aria2 invocation with `subprocess.run` arg list in `common/collect.py:89`
- [ ] 1.2 Add `import subprocess` at top of `common/collect.py`
- [ ] 1.3 Change `verify=False` → `verify=True` default in `get_file` (`collect.py:67`) and `_fetch_url_content` (`collect.py:114`)
- [ ] 1.4 Thread a `verify_tls=True` kwarg through `get_file`, `get_file_by_pattern`, `get_file_by_name`
- [ ] 1.5 Replace `yaml.load(..., Loader=Loader)` with `yaml.safe_load` in `cmds/project.py:28`
- [ ] 1.6 Remove the `CLoader`/`Loader` import block at `cmds/project.py:11-14`
- [ ] 1.7 Update README/config docs to note TLS is verified by default and the escape hatch

## 2. Tests
- [ ] 2.1 Add test that aria2 path invokes `subprocess.run` (mock) with an arg list, never a shell string
- [ ] 2.2 Add test that `get_file` passes `verify=True` to `requests.get` (mock requests)
- [ ] 2.3 Add test that `load_config` uses `safe_load` and rejects tagged python objects

## 3. Verification
- [ ] 3.1 Run `pytest tests/test_common.py` — no regressions
- [ ] 3.2 Run `pytest -k collect` for new tests
- [ ] 3.3 `openspec validate harden-data-ingestion-security --strict`
