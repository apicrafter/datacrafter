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

## Reporting vulnerabilities

Open a private advisory via
[GitHub Security Advisories](https://github.com/apicrafter/datacrafter/security/advisories/new)
rather than a public issue.
