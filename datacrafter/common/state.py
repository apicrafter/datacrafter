# -*- coding: utf-8 -*-
"""Project state management module."""
import os
from json import load, dumps
import logging


class ProjectState:
    """Keeps project state"""

    def __init__(self, filename=None, reset=True, autosave=True):
        self.data = {}
        self.filename = filename
        self.autosave = autosave
        if not reset and filename and os.path.exists(filename):
            self.load(filename)
        else:
            self.stages = []
            self.last_stage = None

    def add(self, name, status="success", results=None):
        """Add stage"""
        if results is None:
            results = {}
        self.stages.append({'name': name, 'status': status, 'results': results})
        self.last_stage = name
        if self.autosave:
            self.save(self.filename)

    def load(self, filename):
        """Load"""
        with open(filename, 'r', encoding='utf8') as f:
            self.data = load(f)
        self.stages = self.data['stages']
        self.last_stage = self.stages[-1]['name']
        pass

    def save(self, filename=None):
        """Save project state to file."""
        if not filename:
            filename = self.filename
        if filename:
            with open(filename, 'w', encoding='utf8') as f:
                self.data['stages'] = self.stages
                f.write(dumps(self.data, indent=4))
            logging.debug('Saved current state')
        else:
            logging.debug('State not saved, filename not provided')
