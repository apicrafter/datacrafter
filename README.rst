========================================================================================
pumpilo -- a data extraction and packaging tool with autodocumentation and NoSQL support
========================================================================================


pumpilo is a command line tool that helps to extract data from data sources and to package it for future use.
Its goal is to make ETL tool with advanced features like automatic documentation, type conversion and so on.
It provides a simple ``pumpilo`` command that allows run pipelines and to extract data from files and API, autodocument and process it.


.. contents::

.. section-numbering::



Main features
=============




Installation
============


macOS
-----


On macOS, pumpilo can be installed via `Homebrew <https://brew.sh/>`_
(recommended):

.. code-block:: bash

    $ brew install pumpilo


A MacPorts *port* is also available:

.. code-block:: bash

    $ port install pumpilo

Linux
-----

Most Linux distributions provide a package that can be installed using the
system package manager, for example:

.. code-block:: bash

    # Debian, Ubuntu, etc.
    $ apt install pumpilo

.. code-block:: bash

    # Fedora
    $ dnf install pumpilo

.. code-block:: bash

    # CentOS, RHEL, ...
    $ yum install pumpilo

.. code-block:: bash

    # Arch Linux
    $ pacman -S pumpilo


Windows, etc.
-------------

A universal installation method (that works on Windows, Mac OS X, Linux, вЂ¦,
and always provides the latest version) is to use pip:


.. code-block:: bash

    # Make sure we have an up-to-date version of pip and setuptools:
    $ pip install --upgrade pip setuptools

    $ pip install --upgrade pumpilo


(If ``pip`` installation fails for some reason, you can try
``easy_install pumpilo`` as a fallback.)


Python version
--------------

Python version 3.6 or greater is required.



Usage
=====


Synopsis:

.. code-block:: bash

    $ pumpilo [flags] [command] inputfile


See also ``pumpilo --help``.


Examples
--------

Get headers from file as `headers command`_,  `JSONl`_ data:

.. code-block:: bash

    $ pumpilo headers examples/ausgovdir.jsonl


Analyze file and generate statistics `stats command`_:

.. code-block:: bash

    $ pumpilo stats examples/ausgovdir.jsonl


Get `frequency command`_ of values for field GovSystem in the list of Russian federal government domains from  `govdomains repository <https://github.com/infoculture/govdomains/tree/master/refined>`_

.. code-block:: bash

    $ pumpilo frequency examples/feddomains.csv --fields GovSystem


Get all unique values using `uniq command`_ of the *item.type* field

.. code-block:: bash

    $ pumpilo uniq --fields item.type examples/ausgovdir.jsonl

`convert command`_ from XML to JSON lines file on tag *item*:

.. code-block:: bash

    $ pumpilo convert --tagname item examples/ausgovdir.xml examples/ausgovdir.jsonl


Validate data with `validate command`_ against validation rule *ru.org.inn* and field *VendorINN* in  data file. Output is statistcs only :

.. code-block:: bash

    $ pumpilo validate -r ru.org.inn --mode stats --fields VendorINN examples/roszdravvendors_final.jsonl > inn_stats.json

Validate data with `validate command`_ against validation rule *ru.org.inn* and field *VendorINN* in  data file. Output all invalid records :

.. code-block:: bash

    $ pumpilo validate -r ru.org.inn --mode invalid --fields VendorINN examples/roszdravvendors_final.jsonl > inn_invalid.json

Commands
========

Frequency command
-----------------
Field value frequency calculator. Returns frequency table for certain field.
This command autodetects delimiter and encoding of CSV files and encoding of JSON lines files by default. You may override it providng "-d" delimiter and "-e" encoding parameters.

Get frequencies of values for field *GovSystem* in the list of Russian federal government domains

.. code-block:: bash

    $ pumpilo frequency examples/feddomains.csv --fields GovSystem




Uniq command
-------------

Returns all unique files of certain field(s). Accepts parameter *fields* with comma separated fields to gets it unique values.
Provide single field name to get unique values of this field or provide list of fields to get combined unique values.
This command autodetects delimiter and encoding of CSV files and encoding of JSON lines files by default. You may override it providng "-d" delimiter and "-e" encoding parameters


Returns all unique values of field *regions* in selected JSONl file

.. code-block:: bash

    $ pumpilo uniq --fields region examples/reestrgp_final.jsonl

Returns all unique combinations of fields *status* and *regions* in selected JSONl file

.. code-block:: bash

    $ pumpilo uniq --fields status,region examples/reestrgp_final.jsonl


Convert command
---------------

Converts data from one format to another. Supports most common data files
Supports conversions:

* XML to JSON lines
* CSV to JSON lines
* XLS to JSON lines
* XLSX to JSON lines
* XLS to CSV
* CSV to BSON
* XLS to BSON
* JSON lines to CSV
* CSV to Parquet
* JSON lines to Parquet

Conversion between XML and JSON lines require flag *tagname* with name of tag which should be converted into single JSON record.

Converts XML ausgovdir.xml with tag named *item* to ausgovdir.jsonl

.. code-block:: bash

    $ pumpilo convert --tagname item examples/ausgovdir.xml examples/ausgovdir.jsonl

Converts JSON lines file roszdravvendors_final.jsonl to CSV file roszdravvendors_final.csv

.. code-block:: bash

    $ pumpilo convert examples/roszdravvendors_final.jsonl examples/roszdravvendors_final.csv

Converts CSV file feddomains.csv to Parquet file feddomains.parquet

.. code-block:: bash

    $ pumpilo convert examples/feddomains.csv examples/feddomains.parquet


Validate command
----------------

*Validate* command used to check every value of of field against validation rules like rule to validate email or url.

Current supported rules:

* *common.email* - checks if value is email
* *common.url* - checks if value is url
* *ru.org.inn* - checks if value is russian organization INN identifier
* *ru.org.ogrn* - checks if value if russian organization OGRN identifier

Validate data with `validate command`_ against validation rule *ru.org.inn* and field *VendorINN* in  data file. Output all invalid records :

.. code-block:: bash

    $ pumpilo validate -r ru.org.inn --mode invalid --fields VendorINN examples/roszdravvendors_final.jsonl > inn_invalid.json


Headers command
---------------
Returns fieldnames of the file. Supports CSV, JSON, BSON file types.
For CSV file it takes first line of the file and for JSON lines and BSON files it processes number of records provided as *limit* parameter with default value 10000.
This command autodetects delimiter and encoding of CSV files and encoding of JSON lines files by default. You may override it providng "-d" delimiter and "-e" encoding parameters

Returns headers of JSON lines file with top 10 000 records (default value)

.. code-block:: bash

    $ pumpilo headers examples/ausgovdir.jsonl


Returns headers of JSON lines file using top 50 000 records

.. code-block:: bash

    $ pumpilo headers --limit 50000 examples/ausgovdir.jsonl

Stats command
-------------
Collects statistics about data in dataset. Supports BSON, CSV an JSON lines file types.

Returns table with following data:

* *key* - name of the key
* *ftype* - data type of the values with this key
* *is_dictkey* - if True, than this key is identified as dictionary value
* *is_uniq* - if True, identified as unique field
* *n_uniq* - number of unique values
* *share_uniq* - share of unique values among all values
* *minlen* - minimal length of the field
* *maxlen* - maximum length of the field
* *avglen* - average length of the field

Returns stats for JSON lines file

.. code-block:: bash

    $ pumpilo stats examples/ausgovdir.jsonl

Analysis of JSON lines file and verifies each field that it's date field, detects date format:

.. code-block:: bash

    $ pumpilo stats --checkdates examples/ausgovdir.jsonl

Analyze command
---------------

Analyzes data format and provides human-readable information.


.. code-block:: bash

    $ pumpilo analyze examples/ausgovdir.jsonl


Returned values will include:

* Filename - name of the file
* File type - type of the file, could be: jsonl, xml, csv, json, bson
* Encoding - file encoding
* Delimiter - file delimiter if CSV file
* File size - size of the file, bytes
* Objects count - number of objects in file
* Fields - list of file fields

Also for XML AND JSON files:

* Miltiple tables exists - True or False, if multiple data tables in XML files
* Full data key - full path to data key (field with list of objects) in XML file
* Short data key - final name of field with objects in XML file

For JSON files: JSON type - could be "objects list", "objects list with key" and "single object"
For XML, JSON lines and JSON files: Is flat table? - True if table is flat and could be converted to CSV, False if not convertable
For CSV and JSON lines: Number of lines - number of lines in file


Split command
-------------
Splits dataset into number of datasets based on number of records or field value.
Chunksize parameter *-c* used to set size of chunk if dataset should be splitted by chunk size rule.
If dataset should be splitted by field value than *--fields* parameter used.

Split dataset as 10000 records chunks, procuces files like filename_1.jsonl, filename_2.jsonl where *filename* is name of original file except extension.

.. code-block:: bash

    $ pumpilo split -c 10000 examples/ausgovdir.jsonl


Split dataset as number of files based of field *item.type", generates files filename_value1.jsonl, filename_value2.jsonl and e.t.c.
There are *[filename]* - ausgovdir and *[value1]* - certain unique value from *item.type* field

.. code-block:: bash

    $ pumpilo split --fields item.type examples/ausgovdir.jsonl



Select command
--------------

Select or re-order columns from file. Supports CSV, JSON lines, BSON

Returns columns *item.title* and *item.type* from ausgovdir.jsonl

.. code-block:: bash

    $ pumpilo select --fields item.title,item.type examples/ausgovdir.jsonl


Returns columns *item.title* and *item.type* from ausgovdir.jsonl and stores result as selected.jsonl

.. code-block:: bash

    $ pumpilo select --fields item.title,item.type -o selected.jsonl examples/ausgovdir.jsonl

Flatten command
---------------

Flatten data records. Write them as one value per row

Returns all columns as flattened key,value

.. code-block:: bash

    $ pumpilo flatten examples/ausgovdir.jsonl


Advanced
========

Filtering
---------

You could filter values of any file record by using *filter* attr for any command where it's suported.

Returns columns item.title and item.type filtered with *item.type* value as *role*. Note: keys should be surrounded by "`" and text values by "'".

.. code-block:: bash

    $ pumpilo select --fields item.title,item.type --filter "`item.type` == 'role'" examples/ausgovdir.jsonl

Data containers
---------------

Sometimes, to keep keep memory usage as low as possible to process huge data files.
These files are inside compressed containers like .zip, .gz, .bz2 or .tar.gz files.
*pumpilo* could process compressed files with little memory footprint, but it could slow down file processing.

Returns headers from subs_dump_1.jsonl file inside subs_dump_1.zip file. Require parameter *-z* to be set and *--format-in* force input file type.

.. code-block:: bash

    $ pumpilo headers --format-in jsonl -z subs_dump_1.zip


Date detection
--------------
JSON, JSON lines and CSV files do not support date and datetime data types.
If you manually prepare your data, than you could define datetime in JSON schema for example.B
But if data is external, you need to identify these fields.

pumpilo supports date identification via `qddate <https://github.com/ivbeg/qddate>`_ python library with automatic date detection abilities.

.. code-block:: bash

    $ pumpilo stats --checkdates examples/ausgovdir.jsonl


Data types
==========

JSONl
-----

JSON lines is a replacement to CSV and JSON files, with JSON flexibility and ability to process data line by line, without loading everything into memory.
