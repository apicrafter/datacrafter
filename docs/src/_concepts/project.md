---
title: "Projects"
description: At the core of the DataCrafter experience is a DataCrafter project.
layout: doc
weight: 1
---

<!-- The following is reproduced in docs/src/README.md#datacrafter-init -->

At the core of the DataCrafter experience is your DataCrafter project,
which represents the single source of truth regarding your ETL pipelines:
how data should be extracted, transformed, and loaded.

DataCrafter project a directory with combination of subdirectories and configuration text-based files.
It's very similar to any software development project and could be stored in Git (Github or Gitlab for example).

You can initialize a new DataCrafter project using [`datacrafter init`](/reference/command-line-interface#init).

## <a name="datacrafter-yml-project-file"></a>`datacrafter.yml` project file

At a minimum, a DataCraftet project must contain a project file named `datacrafter.yml`,
which contains your project configuration and tells DataCraftet that a particular directory is a DataCraftet project.

The required properties are:
- `version`, which currently always holds the value `1`.
- `project-id` unique id of the project
- `project-name` name of the project
- `extractor` or `extractors:` — how data is obtained (required before `datacrafter run` / `check` succeed)

### Configuration

At the root of `datacrafter.yml`, and usually at the top of the file, you will find project-specific configuration.

To learn which settings are available, refer to the [Settings reference](/reference/settings).


#### Extractors

Extractor is a section of the project file used to configure data extraction.
`type` is a file type (`file-zip`, `file-csv`, `file-jsonl`, …), `api`, `code`,
`rss`, or `dcat`. `mode` is `singlefile`, `api`, or `code`. Use `extractors:`
(a list) when one project should pull more than one source.


```yml
extractor:
  type: file-zip
  method: urlbypattern
  mode: singlefile
  config:
    prefix: https://www.nalog.ru/opendata/7707329152-paytax/
    data_prefix: https://data.nalog.ru/opendata/7707329152-paytax/data-
```


#### Processor

Processor is a data transformation stage launched after data extraction task. It defines source configuration 
data transformation steps like `keymap` to rename data fields and `typemap` to change data fields types and custom code 
execution with `custom` steps.

```yaml
processor:
  config:
    type: zipxml
    tagname: Документ
  keymap:
    type: names
    fields:
      НаимОрг: orgname
      ИННЮЛ: inn
      СведНП: org
      СвУплСумНал: taxinfo
      СумУплНал: taxsumm
      НаимНалог: taxname
      ИдДок: id
      ДатаДок: date_doc
      ДатаСост: date_formed
  typemap:
#    taxinfo.taxsumm: float
    date_formed: datetime
    date_doc: datetime
```


##### Destinations

Destination is a result of processor work. it's a file or another data destination that could be one of the types
`type` as file-bson, file-jsonl, file-csv, file-parquet, mongodb, arangodb, couchdb, or meilisearch.

```yaml
destination:
  type: file-bson
  compress: xz
  storage: local
  fileprefix: fnspaytax
```


## Project directories

A Datacrafter project is a directory of config, extracted files, and outputs.
It can be stored in Git. Typical layout after `datacrafter init` and a run:

- `datacrafter.yml` — pipeline configuration
- `current/` — files produced by the extractor
- `output/` — processor destination files
- `temp/`, `builds/`, `storage/` — working directories
- `state.json` — last run stages
- `datacrafter.log` — execution log

There is no `.datacrafter` SQLite system database and no `datacrafter elt`
command. Use `datacrafter run`, `datacrafter status`, and `datacrafter log`.

