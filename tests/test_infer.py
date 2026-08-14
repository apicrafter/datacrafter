"""Tests for type inference and JSONL analysis."""
from datacrafter.common.infer import (
    analyze_records, infer_field_types, infer_value_type, merge_types,
    stable_record_id)


def test_infer_value_types():
    assert infer_value_type('30') == 'int'
    assert infer_value_type('1.5') == 'float'
    assert infer_value_type('true') == 'bool'
    assert infer_value_type('2023-01-15') == 'date'
    assert infer_value_type('Ada') == 'string'
    assert infer_value_type(None) is None


def test_merge_widens_int_to_float():
    assert merge_types('int', 'float') == 'float'
    assert merge_types('date', 'datetime') == 'datetime'
    assert merge_types('int', 'bool') == 'string'


def test_infer_field_types_omits_string():
    types = infer_field_types([
        {'age': '30', 'name': 'Ada'},
        {'age': '25', 'name': 'Bob'},
    ])
    assert types == {'age': 'int'}


def test_stable_id_is_deterministic():
    rec = {'b': 2, 'a': 1}
    assert stable_record_id(rec) == stable_record_id({'a': 1, 'b': 2})
    assert stable_record_id(rec, fields=['a']) != stable_record_id(rec)


def test_analyze_records_counts():
    types, metrics = analyze_records([
        {'age': '30', 'name': 'Ada'},
        {'age': '30', 'name': 'Bob'},
    ])
    assert types['age'] == 'int'
    assert metrics['records'] == 2
    assert metrics['fields']['age']['count'] == 2
