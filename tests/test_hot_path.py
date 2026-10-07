"""Hot-path performance guards: date caching and typemap throughput."""
import datetime
import time

import pytest

from datacrafter.common import mappers
from datacrafter.common.infer import infer_value_type
from datacrafter.common.mappers import (
    convert_to_date,
    convert_to_datetime,
    simple_typemap_object,
)

DATE_MATRIX = [
    # (input, expected converter result)
    ('2021-05-01', datetime.datetime(2021, 5, 1)),
    ('01.02.2021', datetime.datetime(2021, 2, 1)),
    ('20210501', datetime.datetime(2021, 5, 1)),
    # partial dates normalize to Jan 1
    ('20210000', datetime.datetime(2021, 1, 1)),
    ('2021-05-01 10:20:30', datetime.datetime(2021, 5, 1, 10, 20, 30)),
    ('', None),
    ('not-a-date', None),
    (None, None),
    (17, None),
]


@pytest.mark.parametrize('value,expected', DATE_MATRIX)
def test_convert_to_datetime_equivalence(value, expected):
    assert convert_to_datetime(value) == expected


@pytest.mark.parametrize('value,expected', [
    ('2021-05-01', datetime.datetime(2021, 5, 1)),
    ('05.01.2021', datetime.datetime(2021, 1, 5)),
    ('20210501', datetime.datetime(2021, 5, 1)),
    ('garbage', None),
    (None, None),
])
def test_convert_to_date_equivalence(value, expected):
    assert convert_to_date(value) == expected


def test_repeated_values_are_cache_hits():
    mappers._datetime_from_string.cache_clear()
    for _ in range(100):
        convert_to_datetime('2030-06-15')
    info = mappers._datetime_from_string.cache_info()
    assert info.hits >= 99
    assert info.misses == 1


def test_infer_value_type_shares_the_cache():
    mappers._datetime_from_string.cache_clear()
    convert_to_datetime('2031-07-04')
    info_before = mappers._datetime_from_string.cache_info()
    assert infer_value_type('2031-07-04') == 'date'
    info_after = mappers._datetime_from_string.cache_info()
    # No new miss: inference reused the converter cache entry.
    assert info_after.misses == info_before.misses


def test_converter_cache_is_bounded():
    for i in range(1000):
        convert_to_datetime(f'no-such-date-{i}')
    info = mappers._datetime_from_string.cache_info()
    assert info.maxsize == mappers.CONVERTER_CACHE_SIZE
    assert info.currsize <= mappers.CONVERTER_CACHE_SIZE


def test_schema_funcs_cached_not_rebuilt():
    schema = {'created': 'date'}
    simple_typemap_object({'created': '2021-01-01'}, schema)
    first = mappers._schema_funcs.cache_info().misses
    simple_typemap_object({'created': '2021-01-02'}, schema)
    assert mappers._schema_funcs.cache_info().misses == first


def test_typemap_throughput_smoke():
    """50k records through the dotted/flat typemap must stay well bounded.

    The bound is deliberately generous (CI-safe) yet catches order-of-
    magnitude regressions like per-value pattern sweeps without a cache.
    """
    schema = {'created': 'date', 'amount': 'float', 'code': 'int'}
    dates = ['2021-05-01', '2021-05-02', '2021-05-03', '2021-05-04']
    records = [
        {'created': dates[i % 4], 'amount': f'{i}.5', 'code': str(i)}
        for i in range(50000)
    ]
    start = time.monotonic()
    for record in records:
        simple_typemap_object(record, schema)
    elapsed = time.monotonic() - start
    assert elapsed < 30, f'typemap of 50k records took {elapsed:.1f}s'
