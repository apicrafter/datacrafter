"""Common utility functions for dictionary operations."""
from typing import Any, Dict, List, Optional, Union

Nested = Union[Dict[str, Any], List[Any]]


def get_dict_value(adict: dict, key: str, prefix: Optional[list] = None) -> Any:
    """Get value from nested dictionary using dot-separated key path."""
    if prefix is None:
        prefix = key.split('.')
    if len(prefix) == 1:
        return adict[prefix[0]]
    return get_dict_value(adict[prefix[0]], key, prefix=prefix[1:])


def get_dict_value_deep(
        adict: Nested, key: str, prefix: Optional[list] = None,
        as_array: bool = False, splitter: str = '.') -> Any:
    """Get value from hierarchical dicts in python with params with dots as splitter"""
    if prefix is None:
        prefix = key.split(splitter)
    if len(prefix) == 1:
        if isinstance(adict, dict):
            if prefix[0] not in adict.keys():
                return None
            if as_array:
                return [adict[prefix[0]], ]
            return adict[prefix[0]]
        if isinstance(adict, list):
            if as_array:
                result = []
                for v in adict:
                    if prefix[0] in v.keys():
                        result.append(v[prefix[0]])
                return result
            if len(adict) > 0 and prefix[0] in adict[0].keys():
                return adict[0][prefix[0]]
        return None
    if isinstance(adict, dict):
        if prefix[0] in adict.keys():
            return get_dict_value_deep(
                adict[prefix[0]], key, prefix=prefix[1:], as_array=as_array)
    if isinstance(adict, list):
        if as_array:
            result = []
            for v in adict:
                res = get_dict_value_deep(
                    v[prefix[0]], key, prefix=prefix[1:], as_array=as_array)
                if res:
                    result.extend(res)
            return result
        return get_dict_value_deep(
            adict[0][prefix[0]], key, prefix=prefix[1:], as_array=as_array)
    return None


def set_dict_value(
        adict: Nested, key: str, value: Any, prefix: Optional[list] = None,
        splitter: str = '.', build_path: bool = True) -> Any:
    """Set value in hierarchical dicts in python with params with dots as splitter"""
    if prefix is None:
        prefix = key.split(splitter)
    if len(prefix) == 1:
        if isinstance(adict, dict):
            adict[prefix[0]] = value
        return adict
    if isinstance(adict, dict):
        if build_path and prefix[0] not in adict.keys():
            adict[prefix[0]] = {}
        adict[prefix[0]] = set_dict_value(
            adict[prefix[0]], key, value, prefix=prefix[1:],
            build_path=build_path)
        return adict
    if isinstance(adict, list):
        for v in adict:
            if not isinstance(v, dict):
                continue
            if prefix[0] not in v:
                if not build_path:
                    continue
                v[prefix[0]] = {}
            set_dict_value(
                v[prefix[0]], key, value, prefix=prefix[1:],
                build_path=build_path)
        return adict
    return None
