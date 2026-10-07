## ADDED Requirements
### Requirement: Hierarchical Set Applies to Every List Element
When `set_dict_value` assigns a dotted key into a list of dicts, it SHALL apply the
assignment to every element of the list and return the complete updated list, and MUST
NOT return after processing only the first element. Accessing a missing intermediate
key inside a list element SHALL skip that element (or populate it when `build_path` is
set) rather than raise `KeyError`.

#### Scenario: every list element is updated
- **WHEN** `set_dict_value` is called on `{"items": [{"a": 1}, {"a": 2}, {"a": 3}]}`
  with key `items.a.b` and value `"x"`
- **THEN** the returned structure contains `a.b == "x"` in all three elements of `items`

#### Scenario: missing key in one element does not abort the rest
- **WHEN** one list element lacks the intermediate key and `build_path` is true
- **THEN** the key path is created in that element and the remaining elements are still
  processed
