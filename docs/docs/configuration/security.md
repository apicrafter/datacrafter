---
title: "Security"
description: "Trust model for configs, scripts, URLs, and secrets"
---

# Security

Datacrafter runs configuration files (`datacrafter.yml`) and `code`-type
extractor / custom processor scripts as **trusted** input. They can execute
arbitrary Python (via `runpy`) and should only come from a source you control.
Scripts **must** resolve inside the project directory.

URLs, filenames, and downloaded data are **untrusted** and are never passed to
a shell.

## Secrets

Put credentials in the environment, not in committed YAML:

```yaml
connstr: "${MONGO_URI}"
connstr: "${MONGO_URI:-mongodb://localhost:27017}"
```

## TLS

Certificate verification is **enabled by default** for HTTPS downloads. Disable
it only for trusted endpoints with a known self-signed cert (a warning is
logged).

Download behaviour can be tuned per extractor in `datacrafter.yml`:

```yaml
extractor:
  type: file-csv
  method: url
  config:
    url: "https://example.com/data.csv"
    timeout: 60          # request timeout in seconds (default: 30)
    verify_tls: false    # only for trusted endpoints; logs a warning
    # aria2: true        # hand the download to aria2 (invoked without a shell)
    # aria2path: aria2c  # explicit aria2 binary path
```

URLs are logged with their query string redacted (query parameters may carry
API keys); the full URL appears only at DEBUG verbosity.

## Reporting vulnerabilities

Open a private advisory via
[GitHub Security Advisories](https://github.com/apicrafter/datacrafter/security/advisories/new)
rather than a public issue.
