"""RSS/Atom catalog extractor."""
import os

from .._registry import register_extractor
from ..common.collect import get_file
from .base import BaseExtractor
from .feeds import extract_rss


@register_extractor("rss")
class RssExtractor(BaseExtractor):
    """Parse an RSS or Atom feed into JSON Lines under ``current/``."""

    def _execute(self):
        jsonl_path = os.path.join(
            self.project.current, f'{self.resource_name}.jsonl')
        results, _items = extract_rss(
            self.config['url'], jsonl_path, self.project.current,
            download_enclosures=bool(self.config.get('download_enclosures')),
            get_file_func=get_file, **self._download_kwargs())
        self.results = [
            {
                'filename': os.path.relpath(item['filename']),
                'compressed': False,
                'type': 'file',
            }
            for item in results
        ]
