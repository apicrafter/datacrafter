## ADDED Requirements

### Requirement: In-Repo Pipeline Recipes
The repository SHALL include example `datacrafter.yml` recipes under `examples/`
covering CSV URL, Excel, ZIP+XML, and APIBackuper extraction, plus the existing
DCAT example. The examples README MUST describe these in-tree files rather than
only pointing at an external repository.

#### Scenario: recipe files exist
- **WHEN** a new user opens `examples/`
- **THEN** they find YAML recipes for CSV, XLSX, ZIP+XML, and APIBackuper in addition to DCAT
