"""Shared validation for ``datacrafter.yml`` and environment preflight."""
import os

from .. import destinations as _destinations  # noqa: F401  populate registry
from .. import extractors as _extractors  # noqa: F401  populate registry
from .. import sources as _sources  # noqa: F401  populate registry
from .._registry import list_destinations, list_extractors, list_sources
from ..constants import ERROR_STRATEGY_FAIL, ERROR_STRATEGY_RETRY, ERROR_STRATEGY_SKIP
from ..extractors.base import FILEEXT_MAP

REQUIRED_TOP_LEVEL_KEYS = ('version', 'project-name')
EXTRACTOR_MODES = ('singlefile', 'api', 'code')
EXTRACTOR_FILE_TYPES = tuple(FILEEXT_MAP.keys())
EXTRACTOR_METHODS = ('url', 'urlbypattern', 'apibackuper')
KEYMAP_TYPES = ('names', 'position')
ERROR_STRATEGIES = (
    ERROR_STRATEGY_SKIP, ERROR_STRATEGY_FAIL, ERROR_STRATEGY_RETRY)
OPTIONAL_DEST_PACKAGES = {
    'mongodb': ('datacrafter.destinations.mongo', 'HAS_PYMONGO', 'pymongo'),
    'arangodb': ('datacrafter.destinations.arango', 'HAS_ARANGO', 'python-arango'),
    'couchdb': ('datacrafter.destinations.couchdb', 'HAS_PYCOUCHDB', 'pycouchdb'),
    'meilisearch': (
        'datacrafter.destinations.meilisearch', 'HAS_MEILISEARCH', 'meilisearch'),
    'file-parquet': (
        'datacrafter.destinations.parquet', 'HAS_PYARROW', 'pyarrow'),
}


def extractor_specs(config):
    """Return extractor dicts from singular or list form."""
    if not isinstance(config, dict):
        return []
    listed = config.get('extractors')
    if isinstance(listed, list):
        return listed
    extractor = config.get('extractor')
    if isinstance(extractor, dict):
        return [extractor]
    return []


def validate_config(config):
    """Validate a loaded project config.

    Returns ``(is_valid, errors)`` where ``errors`` is a list of human-readable
    messages. Unknown source/destination types are rejected using the plugin
    registry so the message lists registered names.
    """
    errors = []

    if not isinstance(config, dict):
        return False, ["Configuration must be a mapping"]

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in config:
            errors.append(f"Missing required key: '{key}'")

    extractor = config.get('extractor')
    extractors = config.get('extractors')
    specs = extractor_specs(config)
    if not specs:
        errors.append("Missing required key: 'extractor' (or 'extractors' list)")
    elif extractors is not None:
        if not isinstance(extractors, list):
            errors.append("'extractors' must be a list")
        else:
            for index, spec in enumerate(extractors):
                if not isinstance(spec, dict):
                    errors.append(f"'extractors[{index}]' must be a dictionary")
                else:
                    _validate_extractor(spec, errors)
    elif isinstance(extractor, dict):
        _validate_extractor(extractor, errors)
    elif 'extractor' in config:
        errors.append("'extractor' must be a dictionary")

    processor = config.get('processor')
    if 'processor' in config:
        if not isinstance(processor, dict):
            errors.append("'processor' must be a dictionary")
        else:
            _validate_processor(processor, errors)

    destination = config.get('destination')
    if 'destination' in config:
        if not isinstance(destination, dict):
            errors.append("'destination' must be a dictionary")
        else:
            _validate_destination(destination, errors)

    return len(errors) == 0, errors


def _validate_extractor(extractor, errors):
    mode = extractor.get('mode')
    stype = extractor.get('type')
    method = extractor.get('method')

    if 'mode' not in extractor:
        if stype not in ('rss', 'dcat', 'code'):
            errors.append("Missing required extractor key: 'mode'")
    elif mode not in EXTRACTOR_MODES:
        errors.append(
            f"Unknown extractor mode {mode!r}. "
            f"Supported modes: {', '.join(EXTRACTOR_MODES)}")

    if 'type' not in extractor:
        errors.append("Missing required extractor key: 'type'")
    elif stype not in list_extractors():
        errors.append(
            f"Unknown extractor type {stype!r}. "
            f"Supported types: {', '.join(list_extractors())}")

    if stype not in ('code', 'rss', 'dcat') and 'method' not in extractor:
        errors.append("Missing required extractor key: 'method'")
    elif method is not None and method not in EXTRACTOR_METHODS:
        errors.append(
            f"Unknown extractor method {method!r}. "
            f"Supported methods: {', '.join(EXTRACTOR_METHODS)}")

    config = extractor.get('config')
    if config is not None and not isinstance(config, dict):
        errors.append("'extractor.config' must be a dictionary")
        config = None
    config = config or {}

    if method == 'url' or stype in ('rss', 'dcat'):
        if method in (None, 'url') and 'url' not in config:
            errors.append("Extractor method 'url' requires config.url")
    if method == 'urlbypattern':
        for key in ('prefix', 'data_prefix'):
            if key not in config:
                errors.append(
                    f"Extractor method 'urlbypattern' requires config.{key}")
    if stype == 'api' and method not in (None, 'apibackuper'):
        errors.append("Extractor type 'api' requires method 'apibackuper'")
    if stype == 'code' and 'script' not in config:
        errors.append("Extractor type 'code' requires config.script")
    if stype in EXTRACTOR_FILE_TYPES and mode not in (None, 'singlefile'):
        errors.append(
            f"Extractor type {stype!r} expects mode 'singlefile'")


def _validate_processor(processor, errors):
    proc_config = processor.get('config')
    if proc_config is not None and not isinstance(proc_config, dict):
        errors.append("'processor.config' must be a dictionary")
        proc_config = None
    proc_config = proc_config or {}

    strategy = proc_config.get('error_strategy')
    if strategy is not None and strategy not in ERROR_STRATEGIES:
        errors.append(
            f"Unknown error_strategy {strategy!r}. "
            f"Supported: {', '.join(ERROR_STRATEGIES)}")

    source_type = proc_config.get('type')
    if source_type is not None and source_type not in list_sources():
        errors.append(
            f"Unknown processor source type {source_type!r}. "
            f"Registered source types: {', '.join(list_sources())}")

    keymap = processor.get('keymap')
    if keymap is not None:
        if not isinstance(keymap, dict):
            errors.append("'processor.keymap' must be a dictionary")
        else:
            keymap_type = keymap.get('type')
            if keymap_type not in KEYMAP_TYPES:
                errors.append(
                    f"Unknown keymap type {keymap_type!r}. "
                    f"Supported: {', '.join(KEYMAP_TYPES)}")
            if keymap_type == 'names' and 'fields' not in keymap:
                errors.append("keymap type 'names' requires 'fields'")
            if keymap_type == 'position' and 'keys' not in keymap:
                errors.append("keymap type 'position' requires 'keys'")

    typemap = processor.get('typemap')
    if typemap is not None and not isinstance(typemap, dict):
        errors.append("'processor.typemap' must be a dictionary")

    custom = processor.get('custom')
    if custom is not None:
        if not isinstance(custom, dict):
            errors.append("'processor.custom' must be a dictionary")
        elif 'code' not in custom:
            errors.append("'processor.custom' requires 'code' (script path)")


def _validate_destination(destination, errors):
    if 'type' not in destination:
        errors.append("'destination' must have a 'type' key")
        return
    dest_type = destination['type']
    registered = list_destinations()
    if dest_type not in registered:
        errors.append(
            f"Unknown destination type {dest_type!r}. "
            f"Registered destination types: {', '.join(registered)}")
        return
    if dest_type.startswith('file-') and 'fileprefix' not in destination:
        errors.append(
            f"Destination type {dest_type!r} requires 'fileprefix'")


def check_environment(config=None, project_path=None):
    """Return a list of environment issues (missing dirs or optional packages)."""
    issues = []
    config = config or {}

    if project_path:
        for dirname in ('current', 'output', 'temp'):
            dirpath = os.path.join(project_path, dirname)
            if not os.path.isdir(dirpath):
                issues.append(
                    f"Missing project directory '{dirname}/' "
                    "(run 'datacrafter init')")

    destination = config.get('destination')
    dest_type = None
    if isinstance(destination, dict):
        dest_type = destination.get('type')
    if dest_type in OPTIONAL_DEST_PACKAGES:
        module_name, flag_name, package = OPTIONAL_DEST_PACKAGES[dest_type]
        try:
            module = __import__(module_name, fromlist=[flag_name])
        except ImportError:
            issues.append(
                f"Destination type {dest_type!r} requires package '{package}'")
        else:
            if not getattr(module, flag_name, False):
                issues.append(
                    f"Destination type {dest_type!r} requires package '{package}'")

    extractor = config.get('extractor') if isinstance(config.get('extractor'), dict) else {}
    specs = extractor_specs(config) or ([extractor] if extractor else [])
    if any(
            spec.get('type') == 'api' or spec.get('method') == 'apibackuper'
            for spec in specs if isinstance(spec, dict)):
        try:
            from ..extractors.base import HAS_APIBACKUPER
            if not HAS_APIBACKUPER:
                issues.append(
                    "Extractor method 'apibackuper' requires package 'apibackuper'")
        except ImportError:
            issues.append(
                "Extractor method 'apibackuper' requires package 'apibackuper'")

    return issues
