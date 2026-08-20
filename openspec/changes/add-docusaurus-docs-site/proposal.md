# Change: Add Docusaurus documentation website

## Why
The `docs/` directory is an incomplete Jekyll/GitLab Pages site with mixed
VuePress leftovers, broken collection links, and content that does not match
the current CLI. A Docusaurus site, organized like undatum, gives Datacrafter
a deployable documentation website and a clearer path from install to YAML
pipelines.

## What Changes
- Replace the Jekyll/Ruby docs site with a Docusaurus 3 classic site under `docs/`
- Reorganize content into Getting Started, Concepts, Use Cases, CLI Reference,
  Configuration, and Development (same information architecture as undatum)
- Update pages so they describe implemented extractors, processors, destinations,
  and CLI commands only
- Add a GitHub Pages workflow (`.github/workflows/deploy-docs.yml`) for future
  deployment to `https://apicrafter.github.io/datacrafter/`
- Point the README documentation section at the new site and local `npm start` flow

## Impact
- Affected specs: `documentation`, `continuous-integration`
- Affected code: `docs/**` (full rewrite), `.github/workflows/deploy-docs.yml`,
  `README.md`, `CHANGELOG.md`
- No runtime Python API or `datacrafter.yml` behavior changes
