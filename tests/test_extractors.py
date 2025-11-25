"""Tests for extractor classes"""
import pytest

from datacrafter.extractors.base import BaseExtractor, DataCrafterConfigurationError


class TestBaseExtractor:
    """Tests for BaseExtractor"""
    
    def test_validate_missing_project(self, sample_config):
        """Test validation fails without project"""
        # Create extractor without project
        class MockProject:
            def __init__(self):
                self.project = sample_config
        
        project = MockProject()
        project.project['extractor'] = {
            'mode': 'singlefile',
            'type': 'file-csv',
            'method': 'url',
            'force': True,
            'config': {}
        }
        
        extractor = BaseExtractor(project)
        extractor.project = None  # Remove project to test validation
        
        with pytest.raises(DataCrafterConfigurationError):
            extractor.validate()
    
    def test_validate_missing_url(self, sample_project):
        """Test validation fails without URL for url method"""
        # Modify project config to have url method without url
        sample_project.project['extractor']['method'] = 'url'
        sample_project.project['extractor']['config'] = {}
        
        extractor = BaseExtractor(sample_project)
        
        with pytest.raises(DataCrafterConfigurationError) as exc_info:
            extractor.validate()
        
        assert 'url' in str(exc_info.value).lower()
    
    def test_validate_urlbypattern_missing_keys(self, sample_project):
        """Test validation fails without required keys for urlbypattern"""
        # Modify project config
        sample_project.project['extractor']['method'] = 'urlbypattern'
        sample_project.project['extractor']['config'] = {}
        
        extractor = BaseExtractor(sample_project)
        
        with pytest.raises(DataCrafterConfigurationError) as exc_info:
            extractor.validate()
        
        error_msg = str(exc_info.value).lower()
        assert 'prefix' in error_msg or 'data_prefix' in error_msg

