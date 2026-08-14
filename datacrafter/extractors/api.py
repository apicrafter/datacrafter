"""APIBackuper-backed extractor."""
from .._registry import register_extractor
from .base import BaseExtractor


@register_extractor("api")
class ApiExtractor(BaseExtractor):
    """Run an APIBackuper project and export JSON Lines."""

    def run(self, update_state=True):
        self.validate()
        self.results = []
        self._run_api()
        self._commit(update_state)
