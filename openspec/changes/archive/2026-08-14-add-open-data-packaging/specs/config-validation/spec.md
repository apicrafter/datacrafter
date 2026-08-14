## ADDED Requirements

### Requirement: Extractors List
A project MAY declare `extractors` as a list of extractor objects instead of a
single `extractor`. Validation SHALL accept either form. At least one extractor
MUST be present.

#### Scenario: extractors list validates
- **WHEN** a config has `extractors` with two valid extractor objects and no singular `extractor`
- **THEN** validation succeeds

#### Scenario: neither extractor nor extractors
- **WHEN** a config omits both `extractor` and `extractors`
- **THEN** validation fails
