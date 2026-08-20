## ADDED Requirements
### Requirement: Documentation Site Deployment Workflow
The repository SHALL include a GitHub Actions workflow that builds the
Docusaurus site from `docs/` and deploys it to GitHub Pages when documentation
changes are pushed to `main` (or when the workflow is dispatched). The workflow
MUST use Node 20, `npm ci`, and the official Pages deploy actions.

#### Scenario: docs change on main
- **WHEN** a commit that changes `docs/**` is pushed to `main` and GitHub Pages
  is enabled with GitHub Actions as the source
- **THEN** CI builds the site and publishes it to
  `https://apicrafter.github.io/datacrafter/`
