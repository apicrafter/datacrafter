"""DCAT catalog extractor."""
from .._registry import register_extractor
from .base import BaseExtractor


@register_extractor("dcat")
class DcatExtractor(BaseExtractor):
    """Parse a DCAT catalog into JSON Lines under ``current/``."""

    def run(self, update_state=True):
        self.validate()
        self.results = []
        self._run_dcat()
        self._commit(update_state)
