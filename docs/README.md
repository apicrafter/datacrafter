# Datacrafter documentation

This directory contains the Docusaurus documentation site for Datacrafter.

## Development

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd docs
npm install
```

### Local development

Start the development server:

```bash
npm start
```

This starts a local development server and opens a browser window. Most changes
are reflected live without restarting the server.

### Build

Build the site for production:

```bash
npm run build
```

This generates static content into the `build` directory. Broken internal links
fail the build (`onBrokenLinks: 'throw'`).

### Serve

Serve the built site locally:

```bash
npm run serve
```

## Project structure

```
docs/
├── docusaurus.config.js    # Docusaurus configuration
├── sidebars.js             # Sidebar navigation
├── package.json            # Node.js dependencies
├── babel.config.js         # Babel configuration
├── src/
│   ├── css/custom.css      # Custom styles
│   ├── pages/index.js      # Homepage (documentation contents)
│   └── components/         # React components
├── static/img/             # Logo and favicon
└── docs/                   # Documentation content
    ├── getting-started/    # Installation, quick start, cookbook
    ├── concepts/           # Projects, ETL, extractors, processors
    ├── use-cases/          # End-to-end recipes
    ├── commands/           # CLI reference
    ├── configuration/      # datacrafter.yml
    ├── development/        # Contributing
    └── license.md
```

## Deployment

The documentation is deployed to GitHub Pages at
[apicrafter.github.io/datacrafter](https://apicrafter.github.io/datacrafter/)
when changes are pushed to `main`. The workflow lives in
`.github/workflows/deploy-docs.yml`.

### GitHub Pages setup

1. Open the repository settings on GitHub.
2. Navigate to **Pages**.
3. Under **Source**, select **GitHub Actions**.

See `GITHUB_PAGES_SETUP.md` for details.

## Documentation structure

- **Getting Started**: Installation, quick start, positioning, cookbook
- **Concepts**: YAML projects and the extract → process → load pipeline
- **Use Cases**: CSV, Excel, ZIP+XML, catalogs, databases
- **CLI Reference**: Command-by-command documentation
- **Configuration**: `datacrafter.yml` schema and security trust model
- **Development**: Contributing and community

## Contributing

When adding or updating documentation:

1. Edit the markdown files in `docs/docs/`.
2. Follow the existing frontmatter (`title`, `description`).
3. Test locally with `npm start`.
4. Confirm `npm run build` succeeds (broken links fail the build).
