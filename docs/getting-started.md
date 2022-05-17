---
title: Getting Started
description: If you're ready to get started with DataCrafter and prepare abd run an ETL pipeline!
layout: doc
weight: 1
---

Welcome! Start with DataCrafter and [run an E(T)L pipeline](#run-a-data-integration-etl-pipeline)
with a [data extractor](#add-an-extractor-to-pull-data-from-a-source) and [destination](#add-a-destination).


## Install DataCrafter

Before you can get started with DataCrafter and the [`datacrafter` CLI](/reference/command-line-interface), you'll need to install it onto your system.

*To learn more about the different installation methods, refer to the [Installation guide](/guide/installation).*

### Local installation

If you're running Linux or macOS and have [Python](https://www.python.org/) 3.7, 3.8 or 3.9 installed,
we recommend installing DataCrafter into a dedicated [Python virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment)
inside the directory that will hold your [DataCrafter projects](/concepts/project).

1. Create and navigate to a directory to hold your DataCrafter projects:

    ```bash
    mkdir datacrafter-projects
    cd datacrafter-projects
    ```

1. Create and activate a virtual environment for DataCrafter inside the `.venv` directory:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

1. Install the [`datacrafter` package from PyPI](https://pypi.org/project/datacrafter/):

    ```bash
    pip3 install datacrafter
    ```

1. Optionally, verify that the [`datacrafter` CLI](/reference/command-line-interface) is now available by viewing the version:

    ```bash
    datacrafter version
    ```

If anything's not behaving as expected, refer to the ["Local Installation" section](/guide/installation#local-installation) of the [Installation guide](/guide/installation) for more details.

## Create your DataCrafter project

Now that you have a way of running the [`datacrafter` CLI](/reference/command-line-interface),
it's time to create a new [DataCrafter project](/concepts/project).

*To learn more about DataCrafter projects, refer to the [Projects concept doc](/concepts/project).*

1. Navigate to the directory that you'd like to hold your DataCrafter projects, if you didn't already do so earlier:

    ```bash
    mkdir datacrafter-projects
    cd datacrafter-projects
    ```

1. Initialize a new project in a directory of your choosing using [`datacrafter init`](/reference/command-line-interface#init):

   ```bash
    datacrafter init <project directory name>

    # For example:
    datacrafter init my-datacrafter-project
   ```

This will create a new directory with, among other things, your [`datacrafter.yml` project file](/concepts/project#datacrafter-yml-project-file):

    ```yml
    version: 1
    project-id: <random UUID>
    project-name: 
    ```

1. Navigate to the newly created project directory:

    ```bash
    cd <project directory>

    # For example:
    cd my-datacrafter-project
    ```
   
1. Optionally, if you'd like to version control your changes, initialize a [Git](https://git-scm.com/) repository and create an initial commit:

    ```bash
    git init
    git add --all
    git commit -m 'Initial DataCrafter project'
    ```

    This will allow you to use [`git diff`](https://git-scm.com/docs/git-diff)
    to easily check the impact of the [`datacrafter` commands](/reference/command-line-interface)
    you'll run below on your project files, most notably your [`datacrafter.yml` project file](/concepts/project#datacrafter-yml-project-file).

## Add an extractor to pull data from a source

Current implementation of DataCrafter include single extractor with several types of extraction types:

- _singlefile_ - extract data from single data file, dataset 
- _api_ - extract file from existing API endpoint.  
- _code_ - any code that extracts files and saves to project data folder

### Examples of extractors 

Extracts single JSON file from www.yota.ru website
```yml
extractor:
  type: file-json
  method: url
  mode: singlefile
  config:
    url: https://www.yota.ru/c/portal/sales-points

```

Extracts single file name as ZIP file, file found by prefix in _config.prefix_ settings and url prefix of the file defined in _config.data_prefix_.
```yml
extractor:
  type: file-zip
  method: urlbypattern
  mode: singlefile
  config:
    prefix: https://www.nalog.ru/opendata/7707329152-taxoffence/
    data_prefix: https://data.nalog.ru/opendata/7707329152-taxoffence/data-
```

Simple API extractor using [apibackuper](https://github.com/ruarxive/apibackuper) library. API specification defined in storage/apibackuper.cfg 
```yml
extractor:
  type: api
  method: apibackuper
  mode: full
```

After extractor job complete result stored in `<projectname>/current` directory and in file `state.json`

Result of the success extractor stage
```json
{
    "stages": [
        {
            "name": "extractor",
            "status": "success",
            "results": [
                {
                    "filename": "current\\data.zip",
                    "compressed": false,
                    "type": "file"
                }
            ]
        }
    ]
```

## Configure processor

Processor in DataCrafter in a key stage that takes data from source and transfer it to the destination.
Processor could include several steps and configuration

Processes XML data file from Russian tax agency. There is a data file produced by extractor, it's a ZIP file with XML 
files inside. Processor `config` section defines source charateristics that it's `zipxml` (ZIP file with XML) and that 
data is in `Документ` tag (cyrillic `Document`).
2 steps defined here: `keymap` and `typemap`. Keymap - renames data fields, typemap - converts data type.

```yml
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
For this example `type` was required since anything could be inside ZIP file. But it's not required if source type predefined by it's file extension.

Processes data from Excel file of Russian Federal medical insurance agency. Original data is an Excel file so we need 
to define such parameters as `start_line` and `keys` to lines to Python dict objects. 
```yml
processor:
  config:
    start_line: 1
    autoid: True
    autotype: True
    autoindex: True
    autoindex_mode: uniq,dict
    keys: territory,years,id,kpp,fullname,shortname,leader_surname,leader_firstname,leader_midname,phone,fax,email,numlic,lic_date,licend_date,functions,smoreg_date
  custom:
     type: script
     code: scripts/cleaner.py
```
Also this processor includes custom script with function called against each record.
This code include function `process` that accepts Python dict and returns Python dict.
```python
def process(r):
    r['years'] = r['years'].split()
    return r
```
This type it converts list of years as comma separated string into list of years as array. 


## Add destination

Destinations are targets of data transformation processes. Common destination is a local file, or it could be database 
or web service.

Destinations could have following types:

- `file-bson` - file as MongoDB BSON file 
- `file-json` - file as JSON lines (NDJSON) file format
- `file-csv` - file as CSV file

Example destination as BSON file
```yml
destination:
  type: file-bson
  compress: xz
  storage: local
  fileprefix: fnspaytax
```

Filename produced as `fileprefix + ext` where `ext` defined by type.
File could be compressed with `xz`, `gz`, `bz2`, `zip` file types.
Right now only `local` storage supported


# Run ETL pipeline

To run ETL pipeline use command `run` in the project directory with `datacrafter.yml` file inside.
   ```bash
   # Run datacrafter ETL verbosely
    datacrafter run -v
   ```
