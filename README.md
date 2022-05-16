# Datacrafter - NoSQL ETL

datacrafter is NoSQL open-source ETL. 

**This is alpha stage of project. Code migration from closed repository is in progress and documentation is in progress too**

Look at examples https://github.com/apicrafter/datacrafter-examples

# Core ideas

* NoSQL is basis. JSON lines and BSON default file formats
* Task chaining and data pipelines
* Command-line first
* Special features
** automated extraction data from API
** semantic types identification
** automatic documentation generation
** data discovery of data, formats and possible data transformation
** packaging data into NoSQL and flat data formats


# Base concepts

* extractors - extractor like API, databases, single files, websites
* sources - source types of the data created by extractors and used by processors
* processors - data processing procedures including mapping keys, type mapping, custom code and e.t.c.
* destinations - targets to store the data: local filesystems, S3 storage, databases
* buzzers (?) - alerting mechanics


## Extractors 

Code to extract data from certain online data source
Extractors could be:
* Local or remote file
* API
  - REST API - Work in progress
  - APIBackuper compatible - Done
  - RSS/Atom Feed - Work in progress
* CMS
  - Wordpress - Work in progress
  - Microsoft Sharepoint (?) 
* Common API - Planned 
  - Email - Planned
  - FTP - Planned
  - SFTP - Planned
* Online services - Planned
  - Yandex Metrika
  - Yandex.Webmaster - Planned


## Sources

Sources are files or databases available after work of extractor code

Most common sources:
* Files
  - JSON lines - Done
  - CSV - Done
  - BSON - Done
  - XLS/XLSX - Done
  - XML - Done
  - JSON - Work in progress
  - YAML - Work in progress
  - SQLite - Work in progress
* SQL Databases - Planned
  - Any SQL via SQL Alchemy
  - Postgres
  - Clickhouse
* NoSQL Databases - Planned
  - MongoDB
  - ArangoDB
  - ElasticSearch/OpenSearch



## Targets

Targets are destination of data collection and processing operations.
Target could be file or database, if it's file it could be located locally or remotely.
Target could support different operation modes, incremental updates or full reload, storing history and e.t.c.

Most common targets:
 
* Files
  - BSON - Done
  - JSON lines - Done
  - CSV - Done
  - Parquet - Work in progress
  - JSON - Work in progress
  - YAML - Planned
  - DataPackage (Frictionless Data) - Planned
* Data catalogs
  - CKAN (https://ckan.org) - Planned
* Databases
  - MongoDB - Work in progress
  - ArangoDB - Planned
  - Clickhouse - Planned
  - Any SQL (SQL Alchemy)
* Online DBs
  - Airtable - Planned
  - Google Spreadsheets - Planned

File targets could should have multiple storage support:
* Local filesystem
* S3
* FTP
* SFTP
* Any WebDAV
* Google Drive
* Dropbox
* Yandex.Disk


## Processors
* Mappers - map data fields from one scheme to another
** keymap - replaces key names (Done)
** typemap - replaces data types (Done)
* Custom code (Python scripts) - data manipulation with python code (Done)
* Custom tools (command line) - data manipulation with command line tools (Work in progress)
* Enrichers - data and metadata enrichment (Planned)


## Buzzers

* Email alert
* Other alerts

