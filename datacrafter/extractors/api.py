"""APIBackuper-backed extractor."""
import logging
import os
import shutil

from .._registry import register_extractor
from .base import HAS_APIBACKUPER, BaseExtractor


@register_extractor("api")
class ApiExtractor(BaseExtractor):
    """Run an APIBackuper project and export JSON Lines."""

    def _execute(self):
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
        builder = self._project_builder(self.project.current)
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

    @staticmethod
    def _project_builder(current_dir):
        # Imported lazily; the optional-dependency probe (HAS_APIBACKUPER)
        # governs whether this path is reachable.
        # pylint: disable=import-outside-toplevel,import-error
        from apibackuper.cmds.project import ProjectBuilder
        return ProjectBuilder(current_dir)
