# Change: Harden Data Ingestion Security

## Why
The URL/file ingestion layer in `datacrafter/common/collect.py` and the YAML config
loader in `datacrafter/cmds/project.py` have three security vulnerabilities that make
the tool unsafe to point at untrusted URLs or open attacker-supplied config:
(1) command injection via `os.system` with interpolated URL/filename strings,
(2) TLS certificate verification disabled by default (`verify=False`),
(3) unsafe `yaml.load` with the full loader (arbitrary object construction).

## What Changes
- Replace `os.system(aria2cmd)` with `subprocess.run([...], shell=False)` using an
  explicit argument list (no shell interpolation) in `common/collect.py:82-89`.
- Change the default of TLS verification to **enabled** (`verify=True`) in both
  `get_file` (`collect.py:67`) and `_fetch_url_content` (`collect.py:114`). Add an
  opt-in `verify_tls` parameter (default `True`) threaded from config.
- Replace `yaml.load(file_obj, Loader=Loader)` with `yaml.safe_load` in
  `cmds/project.py:28` and remove the unsafe `CLoader` import (`project.py:11-14`).
- **BREAKING (behavior):** untrusted HTTPS endpoints with invalid certs will now
  fail by default instead of silently connecting. Document the escape hatch.

## Impact
- Affected specs: `data-collection`
- Affected code: `datacrafter/common/collect.py`, `datacrafter/cmds/project.py`
- Risk: low; behavior change is security-correct. `get_file`/`get_file_by_pattern`/
  `get_file_by_name` signatures gain a `verify_tls` kwarg (backward-compatible default).
