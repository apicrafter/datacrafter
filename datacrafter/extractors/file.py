"""URL and pattern-based file extractors (CSV, JSON, XLSX, ZIP, …)."""
from .._registry import register_extractor
from .base import FILEEXT_MAP, BaseExtractor


@register_extractor(*FILEEXT_MAP)
class FileExtractor(BaseExtractor):
    """Download a single file into ``current/`` by URL or URL pattern."""

    def run(self, update_state=True):
        self.validate()
        self.results = []
        self._run_file()
        self._commit(update_state)
