## 1. Implementation
- [x] 1.1 Replace `_basename_from_url` with a sanitizing helper: reject `""`, `"."`,
  `".."`, strip `/` and `\` segments, and fall back to a hashed name when nothing safe
  remains
- [x] 1.2 Apply the helper at every join site in `extractors/feeds.py` (RSS enclosures
  and DCAT `downloadURL`)
- [x] 1.3 Redact query strings in `collect.py` INFO-level URL logging and in the aria2
  argv log line; keep full URL at DEBUG
- [x] 1.4 Forward `verify_tls`, `timeout`, `aria2`, `aria2path` from extractor config
  through `get_file` / `get_file_by_pattern` / feed downloads
- [x] 1.5 Accept the new keys in config validation and document them in
  `docs/docs/configuration/security.md`

## 2. Tests
- [x] 2.1 Traversal tests: enclosure URLs ending in `/..`, `/.`, and containing
  `..%2f`-style and backslash segments all resolve to a file inside `current/`
- [x] 2.2 Log redaction test: a URL with `?api_key=secret` appears in INFO logs with
  the query stripped and in full at DEBUG
- [x] 2.3 Config plumbing test: `verify_tls: false` in extractor config reaches the
  mocked `requests.get` call and logs the insecure warning
