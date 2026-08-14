"""Interpolate ${VAR} and ${VAR:-default} in loaded YAML values."""
import os
import re

ENV_PATTERN = re.compile(
    r'\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}'
)


class MissingEnvVarError(ValueError):
    """Raised when a required ${VAR} has no environment value and no default."""


def interpolate_env(value, environ=None):
    """Return a copy of value with environment placeholders expanded."""
    environ = os.environ if environ is None else environ
    missing = []
    result = _walk(value, environ, missing)
    if missing:
        names = ', '.join(sorted(set(missing)))
        raise MissingEnvVarError(
            f"Missing environment variable(s): {names}. "
            "Set them or use ${VAR:-default} in datacrafter.yml.")
    return result


def _walk(value, environ, missing):
    if isinstance(value, str):
        return _interp_string(value, environ, missing)
    if isinstance(value, list):
        return [_walk(item, environ, missing) for item in value]
    if isinstance(value, dict):
        return {key: _walk(item, environ, missing) for key, item in value.items()}
    return value


def _interp_string(text, environ, missing):
    def replacer(match):
        name = match.group(1)
        default = match.group(2)
        if name in environ:
            return environ[name]
        if default is not None:
            return default
        missing.append(name)
        return match.group(0)

    return ENV_PATTERN.sub(replacer, text)
