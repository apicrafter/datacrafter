# catalog-extract Specification

## Purpose
RSS/Atom and DCAT catalog extractors, plus running a list of extractors in one project.
## Requirements
### Requirement: RSS and Atom Catalog Extractor
Extractor type `rss` SHALL download a feed URL, write item records as JSONL under
`current/`, and MAY download enclosure URLs when `config.download_enclosures` is true.

#### Scenario: rss items become jsonl
- **WHEN** an rss extractor runs against a feed document
- **THEN** `current/` contains JSONL records with title and link fields

### Requirement: DCAT Catalog Extractor
Extractor type `dcat` SHALL download a DCAT JSON catalog, write dataset records as
JSONL, and MAY download distribution `downloadURL`s when `config.download` is true.

#### Scenario: dcat datasets become jsonl
- **WHEN** a dcat extractor runs against a catalog object with a `dataset` array
- **THEN** `current/` contains JSONL records for those datasets

### Requirement: Multiple Extractors Run Sequentially
When `extractors` is a list, the project SHALL run each extractor and combine their
result files for the processor stage.

#### Scenario: two extractors contribute files
- **WHEN** `extractors` lists two url extractors that each produce a file
- **THEN** the extractor stage results include both filenames

