"""Trusted in-project Python script extractor."""
from runpy import run_path

from .._registry import register_extractor
from ..common.paths import resolve_project_script
from .base import BaseExtractor


@register_extractor("code")
class CodeExtractor(BaseExtractor):
    """Execute ``collect(config)`` from a script under the project directory."""

    def _execute(self):
        self.script = resolve_project_script(
            self.project.project_path, self.config['script'])
        script = run_path(self.script)
        self.__process_func = script['collect']
        self.results = self.__process_func(self.config)
