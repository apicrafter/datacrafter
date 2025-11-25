"""Pytest configuration and fixtures"""
import os
import tempfile
import shutil
from pathlib import Path

import pytest

from datacrafter.cmds.project import Project
from datacrafter.common.state import ProjectState


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_project(temp_dir):
    """Create a sample project in a temporary directory"""
    project = Project(temp_dir)
    project.init(name="test-project")
    return project


@pytest.fixture
def sample_config():
    """Sample project configuration"""
    return {
        'version': '1',
        'project-name': 'test-project',
        'project-id': 'test-id-123',
        'extractor': {
            'mode': 'singlefile',
            'type': 'file-csv',
            'method': 'url',
            'force': True,
            'config': {
                'url': 'https://example.com/data.csv'
            }
        },
        'processor': {
            'config': {
                'autoid': True,
                'autotype': False,
                'error_strategy': 'skip'
            }
        },
        'destination': {
            'type': 'file-jsonl',
            'fileprefix': 'output'
        }
    }


@pytest.fixture
def sample_jsonl_data():
    """Sample JSONL data for testing"""
    return [
        '{"id": 1, "name": "Alice", "age": 30}\n',
        '{"id": 2, "name": "Bob", "age": 25}\n',
        '{"id": 3, "name": "Charlie", "age": 35}\n'
    ]


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing"""
    return [
        'id,name,age\n',
        '1,Alice,30\n',
        '2,Bob,25\n',
        '3,Charlie,35\n'
    ]


@pytest.fixture
def jsonl_file(temp_dir, sample_jsonl_data):
    """Create a temporary JSONL file"""
    filepath = os.path.join(temp_dir, 'test.jsonl')
    with open(filepath, 'w', encoding='utf8') as f:
        f.writelines(sample_jsonl_data)
    return filepath


@pytest.fixture
def csv_file(temp_dir, sample_csv_data):
    """Create a temporary CSV file"""
    filepath = os.path.join(temp_dir, 'test.csv')
    with open(filepath, 'w', encoding='utf8') as f:
        f.writelines(sample_csv_data)
    return filepath


@pytest.fixture
def state_file(temp_dir):
    """Create a temporary state file"""
    return os.path.join(temp_dir, 'state.json')


@pytest.fixture
def empty_state(state_file):
    """Create an empty project state"""
    return ProjectState(filename=state_file, reset=True, autosave=False)

