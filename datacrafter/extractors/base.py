"""Shared extractor state, validation, and the run() template method."""
from ..errors import DataCrafterError

try:
    from apibackuper.cmds.project import ProjectBuilder
    HAS_APIBACKUPER = True
except ImportError:
    HAS_APIBACKUPER = False
    ProjectBuilder = None

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


class DataCrafterConfigurationError(DataCrafterError):
    """Raised when an extractor configuration is invalid."""
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

    def run(self, update_state=True):
        """Template method: validate, reset results, execute, commit state.

        Subclasses implement :meth:`_execute` with their type-specific logic
        and must not re-implement this sequence.
        """
        self.validate()
        self.results = []
        self._execute()
        self._commit(update_state)

    def _execute(self):
        """Type-specific extraction logic; must be overridden."""
        raise NotImplementedError(
            f"{type(self).__name__} must implement _execute()")

    def _commit(self, update_state=True):
        status = 'fail' if self.results is None or len(self.results) == 0 else 'success'
        if update_state:
            self.project.state.add('extractor', status=status, results=self.results)

    def _download_kwargs(self):
        """Map extractor config keys to downloader options (get_file & feeds).

        Only keys present in the config are forwarded so downloader defaults
        (TLS verification on, default timeout) stay in effect when unset.
        """
        kwargs = {}
        if self.config.get('timeout') is not None:
            kwargs['timeout'] = self.config['timeout']
        if 'verify_tls' in self.config:
            kwargs['verify_tls'] = bool(self.config['verify_tls'])
        if self.config.get('aria2'):
            kwargs['aria2'] = True
            if self.config.get('aria2path'):
                kwargs['aria2path'] = self.config['aria2path']
        return kwargs
