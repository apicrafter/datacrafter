---
title: "init"
description: "Initialize a Datacrafter project"
---

# init

```bash
datacrafter init [DIRECTORY] [--path PATH] [--name NAME] [--verbose]
```

Creates a project directory and a starter `datacrafter.yml`. Pass either a
directory argument or `--path`, not both. If `--name` is omitted, the project
name defaults to the directory basename.

```bash
datacrafter init my-project
cd my-project
```

Then add an extractor (and optional processor/destination) and run
[`datacrafter check`](/commands/check). See [Projects](/concepts/projects).
