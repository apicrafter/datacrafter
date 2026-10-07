# documentation Specification

## Purpose
Contributor onboarding, security trust model, and accurate in-repo documentation links.
## Requirements
### Requirement: Contribution Guide
The repository SHALL include a `CONTRIBUTING.md` describing environment setup, how to
run tests and linters, branching/commit conventions, and the pull-request process.

#### Scenario: contributor onboarding
- **WHEN** a new contributor reads `CONTRIBUTING.md`
- **THEN** they find instructions to set up the project, run tests, and submit a PR

### Requirement: Security & Trust Model Documented
The README SHALL document the security trust model: configuration files and `code`-type
extractor scripts are treated as trusted, while URLs and filenames are untrusted and
must not flow into shell commands.

#### Scenario: trust model visible
- **WHEN** a user reads the README
- **THEN** a Security section explains what inputs are trusted and how to report vulnerabilities

### Requirement: Accurate Internal Documentation Links
The README SHALL contain only links to files that exist in the repository and MUST NOT
reference non-existent files (e.g. `IMPROVEMENTS.md`).

#### Scenario: no broken doc links
- **WHEN** the README's internal links are checked
- **THEN** every linked file exists in the repository

### Requirement: No Stale Repository Artifacts
The repository SHALL NOT contain stale backup files (e.g. `README.rst_`) or obsolete
build artifacts in `dist/`, and `docs/.gitignore` SHALL cover `node_modules/`.

#### Scenario: clean repo root
- **WHEN** the repository root is inspected
- **THEN** no `*.rst_` or stale `dist/*.egg` artifacts are present

### Requirement: In-Repo Pipeline Recipes
The repository SHALL include example `datacrafter.yml` recipes under `examples/`
covering CSV URL, Excel, ZIP+XML, and APIBackuper extraction, plus the existing
DCAT example. The examples README MUST describe these in-tree files rather than
only pointing at an external repository.

#### Scenario: recipe files exist
- **WHEN** a new user opens `examples/`
- **THEN** they find YAML recipes for CSV, XLSX, ZIP+XML, and APIBackuper in addition to DCAT

### Requirement: Docusaurus Documentation Website
The repository SHALL contain a Docusaurus 3 documentation site in `docs/`
that can be developed with `npm start` and built to static HTML with
`npm run build`. The site MUST use the classic preset, English locale,
and `routeBasePath: '/'`.

#### Scenario: local preview
- **WHEN** a contributor runs `npm install` and `npm start` in `docs/`
- **THEN** a local development server serves the documentation site

#### Scenario: production build
- **WHEN** a contributor runs `npm run build` in `docs/`
- **THEN** static files are written to `docs/build/` and the build fails if
  internal routes are broken

### Requirement: Undatum-Style Documentation Information Architecture
The documentation sidebar SHALL organize pages into Getting Started, Concepts,
Use Cases, CLI Reference, Configuration, and Development. A contents homepage
MUST link into those sections. Pages MUST describe implemented Datacrafter
behavior (YAML projects, extractors, processors, destinations, CLI) and MUST
NOT present unimplemented Meltano/ELT or missing reference routes as shipped
features.

#### Scenario: first-run path
- **WHEN** a new user opens the site homepage
- **THEN** they can reach installation, a quick-start pipeline, and the
  `datacrafter.yml` configuration reference from the contents grid or sidebar

#### Scenario: no stale product copy
- **WHEN** a reader follows Getting Started and Concepts pages
- **THEN** commands, extractor types, and destinations match the current CLI
  and plugin registry

