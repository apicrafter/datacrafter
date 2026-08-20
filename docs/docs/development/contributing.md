---
title: "Contributing"
description: "Set up a development environment and submit a pull request"
---

# Contributing

Thanks for your interest in contributing. Full details live in
[`CONTRIBUTING.md`](https://github.com/apicrafter/datacrafter/blob/main/CONTRIBUTING.md)
in the repository.

## Development setup

```bash
git clone https://github.com/apicrafter/datacrafter.git
cd datacrafter
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

Python 3.9+ is required.

## Tests and lint

```bash
pytest
pylint datacrafter/
ruff check datacrafter tests
pip-audit -r requirements.txt
```

Coverage is gated (currently 80%). External databases must be mocked.

## Documentation site

```bash
cd docs
npm install
npm start
npm run build
```

Edit markdown under `docs/docs/`. Broken internal links fail `npm run build`.

## Git workflow

Branch off `main` as `feat/<topic>`, `fix/<topic>`, or `docs/<topic>`. Open a
pull request against `main`. CI must be green before merge.

By contributing, you agree your contributions are licensed under Apache 2.0.
