"""Tests for common utility functions"""
import pytest

from datacrafter.common.common import (
    get_dict_value,
    get_dict_value_deep,
    set_dict_value,
    update_dict_values
)


class TestGetDictValue:
    """Tests for get_dict_value function"""
    
    def test_simple_key(self):
        """Test getting a simple key"""
        data = {'name': 'test', 'value': 42}
        assert get_dict_value(data, 'name') == 'test'
        assert get_dict_value(data, 'value') == 42
    
    def test_nested_key(self):
        """Test getting a nested key"""
        data = {'user': {'name': 'Alice', 'age': 30}}
        assert get_dict_value(data, 'user.name') == 'Alice'
        assert get_dict_value(data, 'user.age') == 30
    
    def test_missing_key(self):
        """Test getting a missing key raises KeyError"""
        data = {'name': 'test'}
        with pytest.raises(KeyError):
            get_dict_value(data, 'missing')


class TestGetDictValueDeep:
    """Tests for get_dict_value_deep function"""
    
    def test_simple_key(self):
        """Test getting a simple key"""
        data = {'name': 'test', 'value': 42}
        assert get_dict_value_deep(data, 'name') == 'test'
        assert get_dict_value_deep(data, 'value') == 42
    
    def test_nested_key(self):
        """Test getting a nested key"""
        data = {'user': {'name': 'Alice', 'age': 30}}
        assert get_dict_value_deep(data, 'user.name') == 'Alice'
        assert get_dict_value_deep(data, 'user.age') == 30
    
    def test_missing_key_returns_none(self):
        """Test getting a missing key returns None"""
        data = {'name': 'test'}
        assert get_dict_value_deep(data, 'missing') is None
    
    def test_list_access(self):
        """Test accessing values in a list"""
        data = [{'name': 'Alice'}, {'name': 'Bob'}]
        assert get_dict_value_deep(data, 'name') == 'Alice'
        assert get_dict_value_deep(data, 'name', as_array=True) == ['Alice', 'Bob']

    def test_nested_list_as_array(self):
        data = [{'user': {'name': 'Alice'}}, {'user': {'name': 'Bob'}}]
        assert get_dict_value_deep(data, 'user.name', as_array=True) == [
            'Alice', 'Bob']
        assert get_dict_value_deep(data, 'user.name') == 'Alice'


class TestSetDictValue:
    """Tests for set_dict_value function"""
    
    def test_simple_key(self):
        """Test setting a simple key"""
        data = {}
        result = set_dict_value(data, 'name', 'test')
        assert result['name'] == 'test'
        assert data['name'] == 'test'
    
    def test_nested_key(self):
        """Test setting a nested key"""
        data = {}
        result = set_dict_value(data, 'user.name', 'Alice')
        assert result['user']['name'] == 'Alice'
        assert data['user']['name'] == 'Alice'
    
    def test_build_path(self):
        """Test building path for nested keys"""
        data = {}
        result = set_dict_value(data, 'a.b.c', 'value')
        assert result['a']['b']['c'] == 'value'


class TestUpdateDictValues:
    """Tests for update_dict_values function"""
    
    def test_update_multiple_keys(self):
        """Test updating multiple keys"""
        data = {'name': 'old', 'value': 0}
        updates = {'name': 'new', 'value': 42}
        result = update_dict_values(data, updates)
        assert result['name'] == 'new'
        assert result['value'] == 42
    
    def test_update_nested_keys(self):
        """Test updating nested keys"""
        data = {'user': {'name': 'old'}}
        updates = {'user.name': 'new'}
        result = update_dict_values(data, updates)
        assert result['user']['name'] == 'new'

