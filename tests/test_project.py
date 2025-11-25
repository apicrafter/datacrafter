"""Tests for Project class"""
import os
import yaml
import pytest

from datacrafter.cmds.project import Project
from datacrafter.extractors.base import DataCrafterConfigurationError


class TestProject:
    """Tests for Project class"""
    
    def test_init_creates_directories(self, temp_dir):
        """Test that init creates required directories"""
        project = Project(temp_dir)
        project.init(name="test-project")
        
        assert os.path.exists(os.path.join(temp_dir, 'current'))
        assert os.path.exists(os.path.join(temp_dir, 'output'))
        assert os.path.exists(os.path.join(temp_dir, 'temp'))
        assert os.path.exists(os.path.join(temp_dir, 'builds'))
        assert os.path.exists(os.path.join(temp_dir, 'storage'))
    
    def test_init_creates_config_file(self, temp_dir):
        """Test that init creates datacrafter.yml"""
        project = Project(temp_dir)
        project.init(name="test-project")
        
        config_file = os.path.join(temp_dir, 'datacrafter.yml')
        assert os.path.exists(config_file)
        
        with open(config_file, 'r', encoding='utf8') as f:
            config = yaml.safe_load(f)
        assert config['project-name'] == 'test-project'
        assert 'project-id' in config
    
    def test_validate_returns_true(self, sample_project):
        """Test that validate returns True for valid project"""
        is_valid, report = sample_project.validate()
        assert is_valid is True
    
    def test_clean_removes_files(self, sample_project):
        """Test that clean removes temporary files"""
        # Create some test files
        output_file = os.path.join(sample_project.output, 'test.jsonl')
        with open(output_file, 'w') as f:
            f.write('test')
        
        assert os.path.exists(output_file)
        sample_project.clean()
        assert not os.path.exists(output_file)
    
    def test_load_existing_project(self, temp_dir):
        """Test loading an existing project"""
        # Create project
        project1 = Project(temp_dir)
        project1.init(name="test-project")
        
        # Load project
        project2 = Project(temp_dir)
        assert project2.project is not None
        assert project2.project['project-name'] == 'test-project'

