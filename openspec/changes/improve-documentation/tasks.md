## 1. Implementation
- [ ] 1.1 Fix/remove broken `IMPROVEMENTS.md` references in README.md
- [ ] 1.2 Delete stale `README.rst_` from repo root
- [ ] 1.3 Create `CONTRIBUTING.md` (setup, tests, lint, branching, PR flow)
- [ ] 1.4 Fix `stale.yml` placeholder messages → real stale issue/PR text
- [ ] 1.5 Remove stale `dist/*.egg` (1.0.2 era) build artifacts
- [ ] 1.6 Add `node_modules/` to `docs/.gitignore`
- [ ] 1.7 Add "Security" / trust-model section to README.md
- [ ] 1.8 Update README Development section (pyproject.toml, CI, pip-audit references)

## 2. Verification
- [ ] 2.1 `markdown-link-check` or manual check: no broken internal links
- [ ] 2.2 `git status` confirms `README.rst_` removed, `dist/*.egg` removed
- [ ] 2.3 `openspec validate improve-documentation --strict`
