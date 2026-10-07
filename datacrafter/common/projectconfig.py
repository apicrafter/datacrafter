"""Project configuration loading (safe YAML + environment interpolation)."""
import yaml

from .env import interpolate_env


def load_config(filename):
    """Load YAML configuration file using safe loading.

    ``yaml.safe_load`` is used (rather than the full ``Loader``/``CLoader``) so that
    configuration files cannot construct arbitrary Python objects via YAML tags.
    """
    with open(filename, 'r', encoding='utf8') as file_obj:
        data = yaml.safe_load(file_obj)
    return interpolate_env(data) if data is not None else {}
