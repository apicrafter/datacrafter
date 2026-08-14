"""Write a Frictionless Data Package descriptor beside file output."""
import json
import os

from .infer import infer_field_types, iter_jsonl_path

FRICTIONLESS_TYPES = {
    'int': 'integer',
    'float': 'number',
    'bool': 'boolean',
    'date': 'date',
    'datetime': 'datetime',
    'string': 'string',
}


def schema_fields_from_types(field_types):
    """Convert inferred types to Table Schema field descriptors."""
    fields = []
    for name, kind in sorted(field_types.items()):
        fields.append({
            'name': name,
            'type': FRICTIONLESS_TYPES.get(kind, 'string'),
        })
    return fields


def build_datapackage(project_name, resource_path, field_types=None):
    """Return a Data Package dict for one resource file."""
    resource = {
        'name': os.path.splitext(os.path.basename(resource_path))[0] or 'data',
        'path': os.path.basename(resource_path),
        'format': os.path.splitext(resource_path)[1].lstrip('.') or 'jsonl',
    }
    if field_types:
        resource['schema'] = {'fields': schema_fields_from_types(field_types)}
    return {
        'profile': 'data-package',
        'name': project_name or 'datacrafter-output',
        'resources': [resource],
    }


def write_datapackage(output_dir, destination, project_name=None):
    """Write datapackage.json next to a file destination.

    Returns the written path, or None if the destination has no file.
    """
    filename = getattr(destination, '_filename', None) or getattr(
        destination, 'filename', None)
    if not filename or not output_dir:
        return None
    field_types = {}
    if filename.endswith('.jsonl') and os.path.isfile(filename):
        field_types = infer_field_types(iter_jsonl_path(filename))
    package = build_datapackage(
        project_name, filename, field_types=field_types)
    dest_path = os.path.join(output_dir, 'datapackage.json')
    with open(dest_path, 'w', encoding='utf8') as file_obj:
        json.dump(package, file_obj, indent=2, ensure_ascii=False)
        file_obj.write('\n')
    return dest_path
