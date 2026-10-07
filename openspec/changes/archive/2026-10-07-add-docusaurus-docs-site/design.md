## Context
Datacrafter docs currently live in a Jekyll site (`docs/_config.yml`, Ruby
Gemfile, GitLab CI) with a leftover VuePress `package.json`. Content is a
getting-started page plus two concept articles, with many links to pages that
were never written (`/guide/installation`, `/reference/command-line-interface`).

undatum ships a Docusaurus 3 site in `docs/` with `routeBasePath: '/'`, a
contents homepage, sidebar categories, and GitHub Actions Pages deployment.
Datacrafter should follow that layout, adapted to YAML ETL projects rather
than a multi-command file toolkit.

## Goals / Non-Goals
- Goals:
  - Docusaurus 3 classic preset, Node 18+, same scripts as undatum
  - Sidebar IA: Getting Started, Concepts, Use Cases, CLI Reference,
    Configuration, Development
  - Production build with `onBrokenLinks: 'throw'`
  - GitHub Pages workflow ready; Pages source can be enabled later
- Non-Goals:
  - Custom domain (`docs.datacrafter.io`) cutover in this change
  - Algolia search, i18n, versioned docs, or a blog
  - Auto-generated CLI docs from Typer
  - Publishing the site until GitHub Pages is enabled in repo settings

## Decisions
- Decision: Keep the Docusaurus project inside `docs/` (not a separate `website/`
  folder) so the GitHub Pages workflow and local `cd docs && npm start` match
  undatum.
  Alternatives considered: repo-root Docusaurus (mixes Node tooling with the
  Python package); `website/` (breaks the undatum parallel the user asked for).
- Decision: `url: https://apicrafter.github.io`, `baseUrl: '/datacrafter/'` for
  project-site Pages. Custom domain is documented in `GITHUB_PAGES_SETUP.md`.
- Decision: Docs plugin `routeBasePath: '/'` so pages are `/getting-started/...`
  rather than `/docs/...`. Homepage is `src/pages/index.js` (contents grid).
- Decision: Rewrite content against live CLI/registry types; do not port
  Meltano/ELT/GitLab copy from the Jekyll site.
- Decision: Brand color from the existing wordmark (`#08329A`); reuse
  `docs/images/apicrafter-logo.svg` as `static/img/logo.svg`.

## Risks / Trade-offs
- Node toolchain in `docs/` → Mitigate with `docs/.gitignore` covering
  `node_modules/`, `.docusaurus/`, and `build/`; commit `package-lock.json`.
- GitHub Pages not enabled yet → Workflow is present; setup steps live in
  `docs/GITHUB_PAGES_SETUP.md`.
- Broken internal links fail CI once the workflow runs → `onBrokenLinks: 'throw'`
  and a local `npm run build` before merge.

## Migration Plan
1. Remove Jekyll/Ruby/GitLab artifacts from `docs/`.
2. Add Docusaurus config, sidebar, homepage, and markdown under `docs/docs/`.
3. Add `deploy-docs.yml`.
4. Update README/CHANGELOG.
5. Rollback: restore the previous `docs/` tree from git.

## Open Questions
- Whether to later bind `docs.datacrafter.io` as a custom domain (documented,
  not required for this change).
