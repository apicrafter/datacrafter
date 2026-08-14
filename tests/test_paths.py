"""Tests for trusted project-script path resolution."""
import os

import pytest

from datacrafter.common.paths import resolve_project_script


def test_relative_script_inside_project(temp_dir):
    script = os.path.join(temp_dir, 'collect.py')
    with open(script, 'w', encoding='utf8') as file_obj:
        file_obj.write('def collect(config):\n    return []\n')
    resolved = resolve_project_script(temp_dir, 'collect.py')
    assert os.path.samefile(resolved, script)


def test_rejects_script_outside_project(temp_dir):
    outside = os.path.join(os.path.dirname(temp_dir), 'outside.py')
    with open(outside, 'w', encoding='utf8') as file_obj:
        file_obj.write('# outside\n')
    try:
        with pytest.raises(ValueError, match='must live under the project'):
            resolve_project_script(temp_dir, outside)
    finally:
        os.remove(outside)


def test_rejects_missing_script(temp_dir):
    with pytest.raises(ValueError, match='not found'):
        resolve_project_script(temp_dir, 'missing.py')
