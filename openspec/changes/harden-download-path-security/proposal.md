# Change: Harden feed download path handling and log hygiene

## Why
The October 2026 analysis found the only real code-level security gap: a malicious
RSS/DCAT enclosure or `downloadURL` ending in `/..` (or using backslashes on Windows)
escapes the `current/` directory by one level via `_basename_from_url`
(`datacrafter/extractors/feeds.py:90-93`). Relatedly, full URLs — which may carry API
keys in query strings — are logged to the persistent `datacrafter.log`
(`datacrafter/common/collect.py:69,100`), and the security options documented in
`docs/docs/configuration/security.md` (`verify_tls`, timeouts, `aria2`) are not
forwarded by the extractors, making them dead configuration. Phase 1 of the 2026-10
improvement roadmap.

## What Changes
- Sanitize filenames derived from enclosure/download URLs: reject empty, `.`, `..`,
  and any path separators before joining into `current/`.
- Redact URL query strings in log output (`get_file`, aria2 argv logging) unless
  debug verbosity is explicitly enabled.
- Plumb `verify_tls`, `timeout`, and `aria2`/`aria2path` options from extractor
  config into the download calls (`datacrafter/extractors/base.py:106-112`,
  `extractors/feeds.py`), so the documented security knobs are reachable; update
  validation to accept them.
- Add tests for the traversal cases (including a Windows-style backslash URL).

## Impact
- Affected specs: `data-collection`
- Affected code: `datacrafter/extractors/feeds.py`, `datacrafter/common/collect.py`,
  `datacrafter/extractors/base.py`, `datacrafter/common/validation.py`,
  `docs/docs/configuration/security.md`
