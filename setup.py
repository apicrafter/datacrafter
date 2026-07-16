"""Legacy setup.py shim.

Project metadata, dependencies, and build configuration now live in
``pyproject.toml`` (PEP 621). This shim is kept only for compatibility with
older tooling that invokes ``setup.py`` directly. Modern installs should use::

    pip install .          # or
    python -m build
"""
from setuptools import setup

setup()
