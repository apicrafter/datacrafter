---
title: "Projects"
description: At the core of the DataCrafter experience is a DataCrafter project.
layout: doc
weight: 1
---

<!-- The following is reproduced in docs/src/README.md#datacrafter-init -->

At the core of the DataCrafter experience is your DataCrafter project,
which represents the single source of truth regarding your ELT pipelines:
how data should be [integrated](/guide/integration) and [transformed](/guide/transformation).

DataCrafter project a directory with combination of subdirectories and configuration text-based files.
It's very similar to any software development project and could be stored in Git (Github or Gitlab for example).

You can initialize a new DataCrafter project using [`datacrafter init`](/reference/command-line-interface#init).

## <a name="datacrafter-yml-project-file"></a>`datacrafter.yml` project file

At a minimum, a DataCraftet project must contain a project file named `datacrafter.yml`,
which contains your project configuration and tells DataCraftet that a particular directory is a DataCraftet project.

The only required property is `version`, which currently always holds the value `1`.
The required properties are:
- `version`, which currently always holds the value `1`.
- `project-id` unique id of the project
- `project-name` name of the project

### Configuration

At the root of `datacrafter.yml`, and usually at the top of the file, you will find project-specific configuration.

To learn which settings are available, refer to the [Settings reference](/reference/settings).


#### Extractors

Extractor is a section of the project file used to configure settings of data extraction process.
In this section defined type of the data `type` setting that could be 'file-zip', 'file-jsonl', 'file-xml' and e.t.c
and the way how this file obtained.


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
`type` as file-bson, file-jsonl, file-csv.

```yaml
destination:
  type: file-bson
  compress: xz
  storage: local
  fileprefix: fnspaytax
```


## `.datacrafter` directory

DataCrafter stores various files for internal use inside a `.datacrafter` directory inside your project.

These files are specific to the environment DataCrafter is running in, and should not be checked into version control.
In a newly initialized project, this directory will be included in [`.gitignore`](#gitignore) by default.

While you would usually not want to modify files in this directory directly, knowing what's in there can aid in debugging:

- `.datacrafter/datacrafter.db`: The default SQLite [system database](#system-database).
- `.datacrafter/logs/elt/<run_id>/elt.log`, e.g. `.datacrafter/logs/elt/<UUID>/elt.log`: [`datacrafter elt`](/reference/command-line-interface#elt) output logs for the specified pipeline run.

