## 1. Implementation
- [x] 1.1 Precompile/normalize the date patterns once at module import; avoid
  re-deriving per call
- [x] 1.2 Add a bounded result cache keyed by the raw input string for
  `convert_to_date`/`convert_to_datetime`; ensure cache does not grow unbounded on
  high-cardinality data (cap or `lru_cache(maxsize=…)`)
- [x] 1.3 Reuse the cache from `infer_value_type` so sampling shares warm entries
- [x] 1.4 Streamline `simple_typemap_object` dotted-key traversal to a single pass,
  building on the fixed `set_dict_value`
- [x] 1.5 Demote per-value conversion failure logs to DEBUG

## 2. Tests
- [x] 2.1 Equivalence tests: conversion results unchanged for a matrix of date/datetime
  strings (parametrized), including previously-cached repeats
- [x] 2.2 Performance smoke test: processing N=50k records with autotype sampling
  completes under a generous CI-safe time bound (e.g. assert improvement vs. recorded
  baseline ratio, marked `slow`)
- [x] 2.3 Cache bound test: high-cardinality inputs do not exceed the configured cache
  size
