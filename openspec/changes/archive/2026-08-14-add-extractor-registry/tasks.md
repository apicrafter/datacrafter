## 1. Implementation
- [x] 1.1 Add extractor registry APIs next to source/destination registries
- [x] 1.2 Register file, api, code, rss, and dcat extractor classes
- [x] 1.3 Factory `get_extractor()` used by Project.collect/prepare
- [x] 1.4 Validation and `config schema` list live extractor types

## 2. Verification
- [x] 2.1 Tests for list/lookup/unknown extractor types
- [x] 2.2 Existing extractor tests pass via the factory
- [x] 2.3 `openspec validate add-extractor-registry --strict`
