"""Tests for mapper functions"""
import datetime
import pytest

from datacrafter.common.mappers import (
    convert_to_datetime,
    convert_to_date,
    convert_to_int,
    convert_to_float,
    convert_to_bool,
    map_keys,
    map_document_fields,
    simple_typemap_object
)


class TestTypeConverters:
    """Tests for type conversion functions"""
    
    def test_convert_to_int(self):
        """Test converting string to integer"""
        assert convert_to_int("42") == 42
        assert convert_to_int("0") == 0
        assert convert_to_int("-10") == -10
        assert convert_to_int("") is None
        assert convert_to_int("invalid") is None
    
    def test_convert_to_float(self):
        """Test converting string to float"""
        assert convert_to_float("3.14") == 3.14
        assert convert_to_float("0.0") == 0.0
        assert convert_to_float("") is None
        assert convert_to_float("invalid") is None
    
    def test_convert_to_bool(self):
        """Test converting string to boolean"""
        assert convert_to_bool("true") is True
        assert convert_to_bool("True") is True
        assert convert_to_bool("false") is False
        assert convert_to_bool("False") is False
        assert convert_to_bool("1") is True
        assert convert_to_bool("0") is False
        assert convert_to_bool("other") == "other"  # Returns original if not recognized
    
    def test_convert_to_datetime(self):
        """Test converting string to datetime"""
        result = convert_to_datetime("2023-01-15")
        assert isinstance(result, datetime.datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 15
        
        result = convert_to_datetime("2023-01-15 10:30:00")
        assert isinstance(result, datetime.datetime)
        assert result.hour == 10
        assert result.minute == 30
    
    def test_convert_to_datetime_invalid(self):
        """Test converting invalid datetime string"""
        assert convert_to_datetime("invalid") is None
        assert convert_to_datetime("") is None
    
    def test_convert_to_date(self):
        """Test converting string to date"""
        result = convert_to_date("2023-01-15")
        assert isinstance(result, datetime.datetime)
        assert result.year == 2023


class TestMapKeys:
    """Tests for map_keys function"""
    
    def test_simple_keymapping(self):
        """Test simple key mapping"""
        keys = {'old_name': {'name': 'new_name'}}
        record = {'old_name': 'value', 'other': 'keep'}
        result = map_keys(record, keys)
        
        assert 'new_name' in result
        assert result['new_name'] == 'value'
        assert 'old_name' not in result
        assert 'other' in result  # Unmapped keys are kept
    
    def test_nested_keymapping(self):
        """Test nested key mapping"""
        keys = {
            'user': {
                'name': {'name': 'user_name'},
                'age': {'name': 'user_age'}
            }
        }
        record = {'user': {'name': 'Alice', 'age': 30}}
        result = map_keys(record, keys)
        
        assert 'user' in result
        assert result['user']['user_name'] == 'Alice'
        assert result['user']['user_age'] == 30


class TestSimpleTypemapObject:
    """Tests for simple_typemap_object function"""
    
    def test_type_conversion(self):
        """Test type conversion in typemap"""
        schema = {
            'age': 'int',
            'score': 'float',
            'active': 'bool'
        }
        record = {
            'age': '30',
            'score': '95.5',
            'active': 'true',
            'name': 'Alice'  # No conversion
        }
        result = simple_typemap_object(record, schema)
        
        assert isinstance(result['age'], int)
        assert result['age'] == 30
        assert isinstance(result['score'], float)
        assert result['score'] == 95.5
        assert isinstance(result['active'], bool)
        assert result['active'] is True
        assert result['name'] == 'Alice'  # Unchanged

    def test_nested_dotted_key(self):
        schema = {'user.age': 'int'}
        record = {'user': {'age': '30'}}
        result = simple_typemap_object(record, schema)
        assert result['user']['age'] == 30


class TestMapDocumentFields:
    def test_converts_listed_fields_and_nested_dicts(self):
        record = {
            'age': '30',
            'active': 'true',
            'score': '1.5',
            'nested': {'age': '21'},
            'tags': [{'age': '4'}, 'keep'],
            'empty': None,
        }
        result = map_document_fields(
            record, bool_fields=['active'], int_fields=['age'],
            float_fields=['score'])
        assert result['age'] == 30
        assert result['active'] is True
        assert result['score'] == 1.5
        assert result['nested']['age'] == 21
        assert result['tags'][0]['age'] == 4
        assert result['tags'][1] == 'keep'
        assert 'empty' not in result

