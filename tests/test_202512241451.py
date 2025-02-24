# test_installation.py
import pytest
import os
import yaml
from installation import DevelopmentEnvironmentInstaller

def test_load_config():
    # Create a temporary test config
    test_config = {
        'installation': {
            'tree': {
                'windows': {
                    'system': {'package_manager': {'name': 'test'}}
                },
                'macos': {
                    'system': {'package_manager': {'name': 'test'}}
                }
            }
        }
    }
    
    # Write test config to a temporary file
    with open('test_config.yaml', 'w') as f:
        yaml.dump(test_config, f)
    
    try:
        installer = DevelopmentEnvironmentInstaller('test_config.yaml')
        assert installer.config == test_config
    finally:
        # Clean up the temporary file
        if os.path.exists('test_config.yaml'):
            os.remove('test_config.yaml')

def test_os_type_detection():
    installer = DevelopmentEnvironmentInstaller('test_config.yaml')
    assert installer.os_type in ['windows', 'macos']

def test_is_installed_command():
    installer = DevelopmentEnvironmentInstaller('test_config.yaml')
    # Test with 'python' command which should exist in the test environment
    assert installer._is_installed('python --version') == True
    # Test with non-existent command
    assert installer._is_installed('nonexistentcommand123') == False