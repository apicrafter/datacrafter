## ADDED Requirements
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
