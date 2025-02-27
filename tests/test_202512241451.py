import yaml
import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import io

# Add the parent directory to sys.path to import the installation module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from installation import InstallationManager, Spinner


class TestSpinner(unittest.TestCase):
    """Tests for the Spinner class."""
    
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('time.sleep', return_value=None)
    def test_spinner_context_manager(self, mock_sleep, mock_stdout):
        """Test that the spinner context manager works correctly."""
        with Spinner("Testing"):
            pass
        # Check that something was written to stdout
        self.assertTrue(len(mock_stdout.getvalue()) > 0)
        # Check that sleep was called
        self.assertTrue(mock_sleep.called)
        

class TestInstallationManager(unittest.TestCase):
    """Tests for the InstallationManager class."""
    
    def setUp(self):
        """Set up the test fixture."""
        self.mock_config = """
        installation:
          tree:
            windows:
              test_tool:
                check: test_check
                command: test_command
              nested:
                child:
                  check: nested_check
                  command: nested_command
              with_extensions:
                check: ext_check
                command: ext_command
                extensions:
                  command: ext_install
                  items:
                    - ext1
                    - ext2
            macos:
              test_tool:
                check: test_check_mac
                command: test_command_mac
        """
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    @patch('yaml.safe_load')
    def test_load_config(self, mock_yaml_load, mock_exists, mock_file):
        """Test loading configuration from a YAML file."""
        mock_yaml_load.return_value = {'installation': {'tree': {'windows': {}, 'macos': {}}}}
        
        with patch('sys.exit') as mock_exit:
            manager = InstallationManager("test_config.yaml")
            # Call load_config to trigger the file existence check
            result = manager.load_config()
            
            # Now we can assert the existence check was called
            mock_exists.assert_called_once_with("test_config.yaml")
            
            # Also verify the file was opened
            mock_file.assert_called_once_with("test_config.yaml", 'r')
            
            # Verify yaml.safe_load was called with the file handle
            mock_yaml_load.assert_called_once()
            
            # Verify load_config returned True on success
            self.assertTrue(result)
    
    @patch('os.path.exists', return_value=False)
    @patch('sys.exit')
    def test_file_not_found_terminates(self, mock_exit, mock_exists):
        """Test that the script terminates immediately if the config file is not found."""
        # Create an instance of the installer
        installer = InstallationManager("non_existent.yaml")
        
        # This is assuming you have a method like this in your main module        
        # Use assertRaises context manager to verify the exception
        with self.assertRaises(FileNotFoundError) as context:
            installer.load_config()
        
        self.assertIn("non_existent.yaml", str(context.exception))
    
    @patch('yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    @patch('sys.exit')
    def test_yaml_error_terminates(self, mock_exit, mock_exists, mock_file, mock_yaml_load):
        """Test that the script terminates if there's an error parsing the YAML."""
        mock_yaml_load.side_effect = yaml.YAMLError("Test YAML error")
        
        InstallationManager("invalid.yaml")
        mock_exists.assert_called_once_with("invalid.yaml")
        mock_file.assert_called_once_with("invalid.yaml", 'r')
        mock_yaml_load.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_is_installed_true(self, mock_yaml_load, mock_file, mock_exists, mock_run):
        """Test is_installed when a component is installed."""
        mock_yaml_load.return_value = {'installation': {'tree': {'windows': {}, 'macos': {}}}}
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        manager = InstallationManager("test_config.yaml")
        result = manager.is_installed("test_command")
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_is_installed_false(self, mock_yaml_load, mock_file, mock_exists, mock_run):
        """Test is_installed when a component is not installed."""
        mock_yaml_load.return_value = {'installation': {'tree': {'windows': {}, 'macos': {}}}}
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process
        
        manager = InstallationManager("test_config.yaml")
        result = manager.is_installed("test_command")
        self.assertFalse(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_is_installed_exception(self, mock_yaml_load, mock_file, mock_exists, mock_run):
        """Test is_installed when an exception occurs."""
        mock_yaml_load.return_value = {'installation': {'tree': {'windows': {}, 'macos': {}}}}
        mock_run.side_effect = Exception("Test exception")
        
        manager = InstallationManager("test_config.yaml")
        result = manager.is_installed("test_command")
        self.assertFalse(result)
        mock_run.assert_called_once()
    
    @patch.object(InstallationManager, 'execute_command')
    @patch.object(InstallationManager, 'is_installed')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_traverse_and_execute(self, mock_yaml_load, mock_file, mock_exists, mock_is_installed, mock_execute):
        """Test traversing the configuration and executing commands."""
        mock_yaml_load.return_value = {'installation': {'tree': {'windows': {}, 'macos': {}}}}
        mock_is_installed.return_value = False
        mock_execute.return_value = True
        
        config = {
            'tool1': {
                'check': 'check1',
                'command': 'command1'
            },
            'tool2': {
                'check': 'check2',
                'command': 'command2',
                'extensions': {
                    'command': 'ext_cmd',
                    'items': ['ext1', 'ext2']
                }
            }
        }
        
        manager = InstallationManager("test_config.yaml")
        manager.traverse_and_execute(config)
        
        # Check if is_installed was called for both tools
        self.assertEqual(mock_is_installed.call_count, 2)
        
        # Check if execute_command was called for installation and extensions
        self.assertEqual(mock_execute.call_count, 2)  # 2 tools (extensions are ignored)
    
    @patch.object(InstallationManager, 'traverse_and_execute')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    @patch('platform.system')
    def test_run_installation(self, mock_platform, mock_yaml_load, mock_file, mock_exists, mock_traverse):
        """Test running the installation process."""
        mock_platform.return_value = 'Windows'
        mock_traverse.return_value = None
        
        yaml_data = {
            'installation': {
                'tree': {
                    'windows': {'test': 'data'},
                    'macos': {'test': 'data'}
                }
            }
        }
        mock_yaml_load.return_value = yaml_data
        
        manager = InstallationManager("test_config.yaml")
        # Explicitly load the config to set manager.config properly
        load_result = manager.load_config()
        self.assertTrue(load_result, "Config should load successfully")

        # Now run the installation
        result = manager.run_installation()
        self.assertTrue(result)
            
        self.assertTrue(result)
        mock_traverse.assert_called_once_with({'test': 'data'})
    
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    @patch('platform.system')
    def test_run_installation_missing_os_config(self, mock_platform, mock_yaml_load, mock_file, mock_exists):
        """Test running the installation when OS configuration is missing."""
        mock_platform.return_value = 'Windows'
        
        # Missing windows configuration
        yaml_data = {
            'installation': {
                'tree': {
                    'macos': {'test': 'data'}
                }
            }
        }
        mock_yaml_load.return_value = yaml_data
        
        manager = InstallationManager("test_config.yaml")
        result = manager.run_installation()
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()