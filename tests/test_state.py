"""Tests for ProjectState"""
import os
import json
import pytest

from datacrafter.common.state import ProjectState


class TestProjectState:
    """Tests for ProjectState class"""
    
    def test_init_new_state(self, state_file):
        """Test initializing a new state"""
        state = ProjectState(filename=state_file, reset=True, autosave=False)
        assert state.stages == []
        assert state.last_stage is None
        assert state.data == {}
    
    def test_add_stage(self, state_file):
        """Test adding a stage"""
        state = ProjectState(filename=state_file, reset=True, autosave=False)
        state.add('extractor', status='success', results={'files': ['test.jsonl']})
        
        assert len(state.stages) == 1
        assert state.stages[0]['name'] == 'extractor'
        assert state.stages[0]['status'] == 'success'
        assert state.last_stage == 'extractor'
    
    def test_save_and_load(self, state_file):
        """Test saving and loading state"""
        # Create and save state
        state1 = ProjectState(filename=state_file, reset=True, autosave=False)
        state1.add('extractor', status='success', results={'files': ['test.jsonl']})
        state1.save()
        
        # Load state
        state2 = ProjectState(filename=state_file, reset=False, autosave=False)
        assert len(state2.stages) == 1
        assert state2.stages[0]['name'] == 'extractor'
        assert state2.last_stage == 'extractor'
    
    def test_autosave(self, state_file):
        """Test autosave functionality"""
        state = ProjectState(filename=state_file, reset=True, autosave=True)
        state.add('extractor', status='success', results={})
        
        # Check file was saved
        assert os.path.exists(state_file)
        with open(state_file, 'r', encoding='utf8') as f:
            saved_data = json.load(f)
        assert 'stages' in saved_data
        assert len(saved_data['stages']) == 1
    
    def test_multiple_stages(self, state_file):
        """Test adding multiple stages"""
        state = ProjectState(filename=state_file, reset=True, autosave=False)
        state.add('extractor', status='success', results={})
        state.add('processor', status='success', results={})
        state.add('destination', status='success', results={})
        
        assert len(state.stages) == 3
        assert state.last_stage == 'destination'
        assert state.stages[0]['name'] == 'extractor'
        assert state.stages[1]['name'] == 'processor'
        assert state.stages[2]['name'] == 'destination'

