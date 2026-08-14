"""Infer field types and summarize JSONL records for schema/metrics."""
import hashlib
import json
import os
from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from .mappers import convert_to_datetime

BOOL_STRINGS = {'true', 'false'}


def infer_value_type(value: Any) -> Optional[str]:
    """Return a type name for one value, or None to ignore (null/empty)."""
    if value is None:
        return None
    if isinstance(value, bool):
        return 'bool'
    if isinstance(value, int):
        return 'int'
    if isinstance(value, float):
        return 'float'
    if isinstance(value, datetime):
        return 'datetime'
    if isinstance(value, date):
        return 'date'
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == '':
            return None
        lowered = stripped.lower()
        if lowered in BOOL_STRINGS:
            return 'bool'
        if convert_to_datetime(stripped) is not None:
            if ' ' in stripped or 'T' in stripped:
                return 'datetime'
            return 'date'
        if _is_int_string(stripped):
            return 'int'
        if _is_float_string(stripped):
            return 'float'
        return 'string'
    return 'string'


def _is_int_string(value: str) -> bool:
    if value.startswith(('+', '-')):
        value = value[1:]
    return value.isdigit()


def _is_float_string(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return '.' in value or 'e' in value.lower()


def merge_types(left: Optional[str], right: Optional[str]) -> Optional[str]:
    """Widen two inferred types; incompatible pairs become string."""
    if left is None:
        return right
    if right is None:
        return left
    if left == right:
        return left
    pair = {left, right}
    if pair <= {'int', 'float'}:
        return 'float'
    if pair <= {'date', 'datetime'}:
        return 'datetime'
    return 'string'


def infer_field_types(records: Iterable[dict]) -> Dict[str, str]:
    """Infer a flat field→type map from sample records.

    Nested dict/list values are treated as string (no conversion). Empty/null
    values are ignored. Fields that only appear as string stay omitted so
    callers can skip no-op conversions.
    """
    types: Dict[str, Optional[str]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        for key, value in record.items():
            if isinstance(value, (dict, list)):
                types[key] = merge_types(types.get(key), 'string')
                continue
            inferred = infer_value_type(value)
            if inferred is None:
                continue
            types[key] = merge_types(types.get(key), inferred)
    return {key: kind for key, kind in types.items() if kind and kind != 'string'}


def stable_record_id(record: dict, fields: Optional[List[str]] = None) -> str:
    """Stable hex digest from selected fields or canonical JSON."""
    if fields:
        payload = '|'.join(str(record.get(name, '')) for name in fields)
    else:
        payload = json.dumps(
            record, sort_keys=True, default=str, separators=(',', ':'),
            ensure_ascii=True)
    return hashlib.sha256(payload.encode('utf8')).hexdigest()


def iter_jsonl_path(path: str) -> Iterator[dict]:
    """Yield objects from an uncompressed JSONL file."""
    with open(path, 'r', encoding='utf8') as file_obj:
        for line in file_obj:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                yield row


def find_jsonl_files(directory: str) -> List[str]:
    """Return uncompressed .jsonl files in directory (not .jsonl.gz etc.)."""
    if not directory or not os.path.isdir(directory):
        return []
    names = []
    for name in sorted(os.listdir(directory)):
        if name.endswith('.jsonl') and not name.startswith('.'):
            names.append(os.path.join(directory, name))
    return names


def project_jsonl_files(project_path: str) -> List[str]:
    """Prefer output/*.jsonl, then current/*.jsonl."""
    output = find_jsonl_files(os.path.join(project_path, 'output'))
    if output:
        return output
    return find_jsonl_files(os.path.join(project_path, 'current'))


def analyze_records(
        records: Iterable[dict],
        top_n: int = 10) -> Tuple[Dict[str, str], dict]:
    """Return (field_types, metrics) for an iterable of dict records."""
    total = 0
    nulls = Counter()
    values = defaultdict(Counter)
    present = Counter()
    sample = []
    for record in records:
        if not isinstance(record, dict):
            continue
        total += 1
        if len(sample) < 100:
            sample.append(record)
        for key, value in record.items():
            present[key] += 1
            if value is None or value == '':
                nulls[key] += 1
                continue
            if isinstance(value, (dict, list)):
                continue
            values[key][repr(value) if not isinstance(value, (str, int, float, bool)) else value] += 1
        for key in list(present):
            if key not in record:
                nulls[key] += 1
    field_types = infer_field_types(sample)
    fields = {}
    for key in sorted(present):
        hist = values[key].most_common(top_n)
        fields[key] = {
            'count': present[key],
            'nulls': nulls[key],
            'unique': len(values[key]),
            'type': field_types.get(key, 'string'),
            'top': [{'value': item, 'count': count} for item, count in hist],
        }
    metrics = {
        'records': total,
        'fields': fields,
    }
    return field_types, metrics
