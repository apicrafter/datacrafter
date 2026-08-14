"""Example recipes should be valid datacrafter.yml files."""
from pathlib import Path

import yaml

from datacrafter.common.validation import validate_config

EXAMPLES = Path(__file__).resolve().parents[1] / 'examples'


def test_in_repo_recipes_exist():
    names = {path.parent.name for path in EXAMPLES.glob('*/datacrafter.yml')}
    assert {'csv-url', 'xlsx-registry', 'zip-xml', 'apibackuper', 'dcat', 'rss-feed'} <= names


def test_in_repo_recipes_validate():
    for path in sorted(EXAMPLES.glob('*/datacrafter.yml')):
        with open(path, encoding='utf8') as file_obj:
            config = yaml.safe_load(file_obj)
        ok, errors = validate_config(config)
        assert ok, f'{path}: {errors}'
