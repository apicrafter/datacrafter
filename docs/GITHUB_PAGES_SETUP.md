# GitHub Pages deployment setup

This document describes how Datacrafter documentation is deployed to GitHub
Pages at `https://apicrafter.github.io/datacrafter/`.

## Prerequisites

1. The repository `apicrafter/datacrafter`
2. GitHub Pages enabled in repository settings with **GitHub Actions** as the source

## Configuration

The documentation is configured in `docs/docusaurus.config.js` for project-site
deployment from this repository:

- **URL**: `https://apicrafter.github.io`
- **Base URL**: `/datacrafter/`
- **Organization**: `apicrafter`
- **Project**: `datacrafter`

The published site is available at `https://apicrafter.github.io/datacrafter/`.

## Setup steps

1. **Enable GitHub Pages**:
   - Go to the repository settings on GitHub
   - Navigate to **Pages** in the left sidebar
   - Under **Source**, select **GitHub Actions** as the source
   - This creates the `github-pages` environment

2. **Push to the main branch**:
   - The GitHub Actions workflow (`.github/workflows/deploy-docs.yml`) will:
     - Build the Docusaurus site when changes are pushed to `main`
     - Deploy to GitHub Pages
   - The workflow triggers on:
     - Pushes to `main` that affect files in `docs/`
     - Pull requests that change `docs/` (build only, no deploy)
     - Manual workflow dispatch

3. **Verify deployment**:
   - After the workflow completes, the site is available at
     `https://apicrafter.github.io/datacrafter/`
   - Deployment typically takes 1–2 minutes

## Moving to a custom domain or user site

If the documentation should later live at a root domain such as
`https://docs.datacrafter.io`, update `docusaurus.config.js`:

```javascript
url: 'https://docs.datacrafter.io',
baseUrl: '/',
organizationName: 'apicrafter',
projectName: 'datacrafter',
```

and configure the domain in the repository's Pages settings.

## Manual deployment

You can also deploy locally using the Docusaurus CLI:

```bash
cd docs
npm install
npm run build
npm run deploy
```

This requires a `GITHUB_TOKEN` with appropriate permissions.

## Troubleshooting

- **Environment error**: Enable GitHub Pages with **GitHub Actions** as the source
- **Build failures**: Check the GitHub Actions logs; `onBrokenLinks: 'throw'` fails the build on missing routes
- **404 errors**: Verify `baseUrl` in `docusaurus.config.js` is `/datacrafter/`
