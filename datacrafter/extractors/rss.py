"""RSS/Atom catalog extractor."""
from .._registry import register_extractor
from .base import BaseExtractor


@register_extractor("rss")
class RssExtractor(BaseExtractor):
    """Parse an RSS or Atom feed into JSON Lines under ``current/``."""

    def run(self, update_state=True):
        self.validate()
        self.results = []
        self._run_rss()
        self._commit(update_state)
