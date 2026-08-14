"""Extractor plugins for downloading and catalog-harvesting data."""
from .._registry import UnknownExtractorTypeError, get_extractor_class, list_extractors
from .api import ApiExtractor
from .base import FILEEXT_MAP, BaseExtractor, DataCrafterConfigurationError
from .code import CodeExtractor
from .dcat import DcatExtractor
from .file import FileExtractor
from .rss import RssExtractor

__all__ = [
    "UnknownExtractorTypeError",
    "get_extractor_class",
    "list_extractors",
    "get_extractor",
    "BaseExtractor",
    "DataCrafterConfigurationError",
    "FILEEXT_MAP",
    "ApiExtractor",
    "CodeExtractor",
    "DcatExtractor",
    "FileExtractor",
    "RssExtractor",
]


def get_extractor(project, extractor=None):
    """Construct the registered extractor for a project spec."""
    spec = extractor
    if spec is None:
        spec = (project.project or {}).get('extractor') or {}
    stype = spec.get('type')
    if not stype:
        raise UnknownExtractorTypeError(
            "Extractor config is missing the required 'type' key. "
            f"Registered extractor types: {list_extractors()}")
    cls = get_extractor_class(stype)
    return cls(project, extractor=spec)
