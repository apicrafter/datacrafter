## ADDED Requirements

### Requirement: Parquet File Destination
The system SHALL register destination type `file-parquet`. Construction MUST work
when pyarrow is installed and MUST raise a clear ImportError when it is not.

#### Scenario: parquet is listed
- **WHEN** `list_destinations()` is called
- **THEN** the result includes `file-parquet`
