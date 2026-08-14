## 1. Implementation
- [x] 1.1 Fix/remove broken `IMPROVEMENTS.md` references in README.md
- [x] 1.2 Delete stale `README.rst_` from repo root
- [x] 1.3 Create `CONTRIBUTING.md` (setup, tests, lint, branching, PR flow)
- [x] 1.4 Fix `stale.yml` placeholder messages → real stale issue/PR text
- [x] 1.5 Remove stale `dist/*.egg` (1.0.2 era) build artifacts
- [x] 1.6 Add `node_modules/` to `docs/.gitignore`
- [x] 1.7 Add "Security" / trust-model section to README.md
- [x] 1.8 Update README Development section (pyproject.toml, CI, pip-audit references)

## 2. Verification
- [x] 2.1 `markdown-link-check` or manual check: no broken internal links
- [x] 2.2 `git status` confirms `README.rst_` removed, `dist/*.egg` removed
- [x] 2.3 `openspec validate improve-documentation --strict`
