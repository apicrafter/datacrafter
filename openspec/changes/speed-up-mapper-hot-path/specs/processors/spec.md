## ADDED Requirements
### Requirement: Efficient Date Conversion With Caching
Date/datetime conversion SHALL compile its patterns once (not per value) and cache
conversion results per distinct input string with a bounded cache, while producing
results identical to the uncached per-value conversion. Schema inference (`autotype`
sampling) SHALL benefit from the same cache.

#### Scenario: repeated values convert once
- **WHEN** the same date string appears in many records (or in repeated inference
  samples)
- **THEN** the pattern-matching work is performed at most once per distinct string and
  subsequent conversions are cache hits

#### Scenario: results are unchanged
- **WHEN** a matrix of valid and invalid date/datetime strings is converted
- **THEN** outputs match the documented conversion semantics exactly (same values,
  same pass-through for unparseable strings)

### Requirement: Efficient Dotted-Key Typemap
Type mapping over dotted keys SHALL traverse each record in a single pass per mapping
and MUST NOT exhibit super-linear behavior in the number of mapped fields; processing
throughput for typical records SHALL remain within the bounds set by the performance
smoke test.

#### Scenario: throughput smoke test holds
- **WHEN** the marked performance test processes the reference batch with a typemap
- **THEN** it completes within the asserted time bound in CI
