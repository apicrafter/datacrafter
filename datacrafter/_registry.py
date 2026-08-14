"""Plugin registries for sources, destinations, and extractors.

Each plugin class registers itself with a decorator so the factory functions can
resolve a config ``type`` by registry lookup. The registries also expose
``list_sources()`` / ``list_destinations()`` / ``list_extractors()`` for tooling
(e.g. the ``config schema`` command) and raise a clear, typed error on unknown
types.

A decorator registry is used (rather than an if/elif chain) so adding a new
format only requires annotating its class in one place; the registry is populated
at import time, which is why the package ``__init__`` modules import every format
module.
"""
from typing import Callable, Dict, List, Type


class UnknownSourceTypeError(KeyError):
    """Raised when a source config ``type`` is not registered."""


class UnknownDestinationTypeError(KeyError):
    """Raised when a destination config ``type`` is not registered."""


class UnknownExtractorTypeError(KeyError):
    """Raised when an extractor config ``type`` is not registered."""


# name -> source class. Populated by @register_source decorators at import time.
_SOURCE_REGISTRY: Dict[str, Type] = {}
# name -> destination class.
_DESTINATION_REGISTRY: Dict[str, Type] = {}
# name -> extractor class.
_EXTRACTOR_REGISTRY: Dict[str, Type] = {}


def register_source(name: str) -> Callable[[Type], Type]:
    """Register a source class under ``name``.

    Usage::

        @register_source("file-csv")
        class CSVSource(BaseFileSource): ...
    """
    def decorator(cls: Type) -> Type:
        _SOURCE_REGISTRY[name] = cls
        return cls
    return decorator


def register_destination(name: str) -> Callable[[Type], Type]:
    """Register a destination class under ``name``.

    Usage::

        @register_destination("file-jsonl")
        class JSONLinesDestination(BaseFileDestination): ...
    """
    def decorator(cls: Type) -> Type:
        _DESTINATION_REGISTRY[name] = cls
        return cls
    return decorator


def register_extractor(*names: str) -> Callable[[Type], Type]:
    """Register an extractor class under one or more type names."""
    def decorator(cls: Type) -> Type:
        for name in names:
            _EXTRACTOR_REGISTRY[name] = cls
        return cls
    return decorator


def get_source_class(name: str) -> Type:
    """Return the registered source class for ``name`` or raise."""
    try:
        return _SOURCE_REGISTRY[name]
    except KeyError as exc:
        raise UnknownSourceTypeError(
            f"Unknown source type {name!r}. "
            f"Registered source types: {sorted(_SOURCE_REGISTRY)}"
        ) from exc


def get_destination_class(name: str) -> Type:
    """Return the registered destination class for ``name`` or raise."""
    try:
        return _DESTINATION_REGISTRY[name]
    except KeyError as exc:
        raise UnknownDestinationTypeError(
            f"Unknown destination type {name!r}. "
            f"Registered destination types: {sorted(_DESTINATION_REGISTRY)}"
        ) from exc


def list_sources() -> List[str]:
    """Return the sorted names of all registered source types."""
    return sorted(_SOURCE_REGISTRY)


def list_destinations() -> List[str]:
    """Return the sorted names of all registered destination types."""
    return sorted(_DESTINATION_REGISTRY)


def get_extractor_class(name: str) -> Type:
    """Return the registered extractor class for ``name`` or raise."""
    try:
        return _EXTRACTOR_REGISTRY[name]
    except KeyError as exc:
        raise UnknownExtractorTypeError(
            f"Unknown extractor type {name!r}. "
            f"Registered extractor types: {sorted(_EXTRACTOR_REGISTRY)}"
        ) from exc


def list_extractors() -> List[str]:
    """Return the sorted names of all registered extractor types."""
    return sorted(_EXTRACTOR_REGISTRY)
