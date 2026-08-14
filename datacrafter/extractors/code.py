"""Trusted in-project Python script extractor."""
from .._registry import register_extractor
from .base import BaseExtractor


@register_extractor("code")
class CodeExtractor(BaseExtractor):
    """Execute ``collect(config)`` from a script under the project directory."""

    def run(self, update_state=True):
        self.validate()
        self.results = []
        self._run_code()
        self._commit(update_state)
