"""URL and pattern-based file extractors (CSV, JSON, XLSX, ZIP, ...)."""
import logging
import os

from .._registry import register_extractor
from ..common.collect import get_file, get_file_by_pattern
from .base import FILEEXT_MAP, BaseExtractor


@register_extractor(*FILEEXT_MAP)
class FileExtractor(BaseExtractor):
    """Download a single file into ``current/`` by URL or URL pattern."""

    def _execute(self):
        file_ext = FILEEXT_MAP[self.sourcetype]
        fullpathname = os.path.join(
            self.project.current, f'{self.resource_name}.{file_ext}')
        result = None
        if self.method == 'url':
            logging.info('Extract single file %s', self.config['url'])
            result = get_file(
                self.config['url'], fullpathname, **self._download_kwargs())
        elif self.method == 'urlbypattern':
            logging.info('Extract file by url pattern %s', self.config['prefix'])
            result = get_file_by_pattern(
                self.project.current, self.project.temp, self.config['prefix'],
                self.config['data_prefix'], fullpathname, file_type=file_ext,
                force=True, **self._download_kwargs())
        if result:
            self.results = [{
                'filename': os.path.relpath(fullpathname),
                'compressed': False,
                'type': 'file',
            }]
