"""Shared extractor state, validation, and file/API/code/catalog run helpers."""
import logging
import os
import shutil
from runpy import run_path

try:
    from apibackuper.cmds.project import ProjectBuilder
    HAS_APIBACKUPER = True
except ImportError:
    HAS_APIBACKUPER = False
    ProjectBuilder = None

from ..common.collect import get_file, get_file_by_pattern
from ..common.paths import resolve_project_script
from .feeds import extract_dcat, extract_rss

FILEEXT_MAP = {
    'file-zip': 'zip',
    'file-xls': 'xls',
    'file-csv': 'csv',
    'file-xml': 'xml',
    'file-json': 'json',
    'file-jsonl': 'jsonl',
    'file-xlsx': 'xlsx'
}
CATALOG_TYPES = ('rss', 'dcat')


class DataCrafterConfigurationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BaseExtractor:
    """Shared extractor configuration, validation, and run helpers.

    Concrete types register with ``@register_extractor`` and implement ``run``.
    """

    def __init__(self, project=None, extractor=None):
        self.project = project
        self.project_config = project.project
        spec = extractor if extractor is not None else project.project.get('extractor', {})
        self.spec = spec
        self.mode = spec.get('mode', 'singlefile')
        self.sourcetype = spec.get('type')
        self.method = spec.get('method')
        if self.sourcetype in CATALOG_TYPES and not self.method:
            self.method = 'url'
        self.force = spec.get('force', True)
        self.config = spec.get('config') or {}
        self.resource_name = spec.get('name') or 'data'
        self.results = []

    def validate(self):
        """Number of validation rules to make sure that config is right"""
        errors = []
        if self.project is None:
            errors.append("Can't run extractor without project data. Please provide it")
        if self.sourcetype != 'code' and self.method == 'url' and 'url' not in self.config.keys():
            errors.append(
                "An 'url' should be defined in config section for url method. "
                f"Available config keys: {list(self.config.keys())}")
        if self.method == 'urlbypattern':
            missing = []
            if 'data_prefix' not in self.config.keys():
                missing.append('data_prefix')
            if 'prefix' not in self.config.keys():
                missing.append('prefix')
            if missing:
                errors.append(
                    f"Missing required config keys for urlbypattern method: "
                    f"{', '.join(missing)}. "
                    f"Available config keys: {list(self.config.keys())}")

        if errors:
            error_msg = (
                "Extractor configuration errors:\n  - " +
                "\n  - ".join(errors))
            raise DataCrafterConfigurationError(error_msg)

    # Need to include type = 'api'
    #        if self.sourcetype not in FILEEXT_MAP.keys() :
    #            raise datacrafterConfigurationError("Source type in 'type' should be one of %s" % (','.join(FILEEXT_MAP.keys())))

    def run(self, update_state=True):
        """Run this extractor. Subclasses implement a type-specific path."""
        raise NotImplementedError(
            f"{type(self).__name__} must implement run(); "
            "use get_extractor() to construct a registered extractor")

    def _commit(self, update_state=True):
        status = 'fail' if self.results is None or len(self.results) == 0 else 'success'
        if update_state:
            self.project.state.add('extractor', status=status, results=self.results)

    def _run_file(self):
        file_ext = FILEEXT_MAP[self.sourcetype]
        fullpathname = os.path.join(
            self.project.current, f'{self.resource_name}.{file_ext}')
        result = None
        if self.method == 'url':
            logging.info('Extract single file %s', self.config['url'])
            result = get_file(self.config['url'], fullpathname)
        elif self.method == 'urlbypattern':
            logging.info('Extract file by url pattern %s', self.config['prefix'])
            result = get_file_by_pattern(
                self.project.current, self.project.temp, self.config['prefix'],
                self.config['data_prefix'], fullpathname, file_type=file_ext,
                force=True)
        if result:
            self.results = [{
                'filename': os.path.relpath(fullpathname),
                'compressed': False,
                'type': 'file',
            }]

    def _run_rss(self):
        jsonl_path = os.path.join(
            self.project.current, f'{self.resource_name}.jsonl')
        results, _items = extract_rss(
            self.config['url'], jsonl_path, self.project.current,
            download_enclosures=bool(self.config.get('download_enclosures')))
        self.results = [
            {
                'filename': os.path.relpath(item['filename']),
                'compressed': False,
                'type': 'file',
            }
            for item in results
        ]

    def _run_dcat(self):
        jsonl_path = os.path.join(
            self.project.current, f'{self.resource_name}.jsonl')
        results, _items = extract_dcat(
            self.config['url'], jsonl_path, self.project.current,
            download=bool(self.config.get('download')),
            format_filter=self.config.get('format'))
        self.results = [
            {
                'filename': os.path.relpath(item['filename']),
                'compressed': False,
                'type': 'file',
            }
            for item in results
        ]

    def _run_api(self):
        if self.method != 'apibackuper':
            return
        if not HAS_APIBACKUPER:
            raise ImportError(
                "apibackuper is required for apibackuper extraction method. "
                "Install it with: pip install apibackuper"
            )
        original_config = os.path.join(self.project.storage, 'apibackuper.cfg')
        if not os.path.exists(original_config):
            logging.info('APIBackuper config file not found')
            return
        for filename in ['apibackuper.cfg', 'params.json', 'url_params.json']:
            original = os.path.join(self.project.storage, filename)
            if os.path.exists(original):
                shutil.copy(original, os.path.join(self.project.current, filename))
        builder = ProjectBuilder(self.project.current)
        if not os.path.exists(os.path.join(builder.storagedir, 'storage.zip')) or self.force:
            builder.run(mode=self.mode)
            if self.config.get('follow') is True:
                logging.debug('Follow key found in configuration. Running follow')
                builder.follow(mode='continue')
            else:
                logging.debug(
                    'Follow key not found in configuration or set to False. '
                    'Not running follow')
        fullfilename = os.path.join(self.project.current, 'data.jsonl')
        builder.export(format='jsonl', filename=fullfilename)
        self.results = [{
            'filename': os.path.relpath(fullfilename),
            'compressed': False,
            'type': 'file',
        }]

    def _run_code(self):
        self.script = resolve_project_script(
            self.project.project_path, self.config['script'])
        script = run_path(self.script)
        self.__process_func = script['collect']
        self.results = self.__process_func(self.config)
