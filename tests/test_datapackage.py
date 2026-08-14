"""Tests for Frictionless datapackage.json writing."""
import json
import os

from datacrafter.common.datapackage import write_datapackage
from datacrafter.destinations.jsonl import JSONLinesDestination


def test_write_datapackage_for_jsonl(temp_dir):
    filename = os.path.join(temp_dir, 'output.jsonl')
    dest = JSONLinesDestination(filename=filename)
    dest.write({'age': '30', 'name': 'Ada'})
    dest.close()
    path = write_datapackage(temp_dir, dest, project_name='demo')
    assert path == os.path.join(temp_dir, 'datapackage.json')
    with open(path, encoding='utf8') as file_obj:
        package = json.load(file_obj)
    assert package['name'] == 'demo'
    assert package['resources'][0]['path'] == 'output.jsonl'
    names = {
        field['name']: field['type']
        for field in package['resources'][0]['schema']['fields']}
    assert names['age'] == 'integer'
