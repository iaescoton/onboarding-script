import yaml
import platform
import subprocess
import sys
import time
import threading
import itertools
import shutil
import os

class Spinner:
    def __init__(self, message="Installing"):
        self.spinner = itertools.cycle(["|", "/", "-", "\\"])
        self.stop_running = False
        self.message = message

    def spin(self):
        while not self.stop_running:
            sys.stdout.write(f"\r{self.message} {next(self.spinner)}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r')
        sys.stdout.flush()

    def __enter__(self):
        self.stop_running = False
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_running = True
        self.thread.join()

class InstallationManager:
    def __init__(self, config_file):
        """Initialize the installation manager with a YAML config file.

        Args:
            config_file (str): Path to the YAML configuration file
        """
        self.config_file = config_file
        self.success = True
        self.config = None


    def load_config(self):
        """Load the YAML configuration file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        #print(f"---load_config--- \nself.config_file: {str(self.config_file)}")
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file '{self.config_file}' not found") 

        try:
            with open(self.config_file, 'r') as file:
                self.config = yaml.safe_load(file)                
            return True
        except yaml.YAMLError as exc:
            print(f"Yaml Error: {str(exc)}")
            return False
        except Exception as e:
            print(f"Error loading config file: {str(e)}")
            return False


    def is_installed(self, check_command):
        """Check if a component is already installed.
        
        Args:
            check_command (str): Command to check installation
            
        Returns:
            bool: True if installed, False otherwise
        """
        #print("---is_installed---")
        try:
            result = subprocess.run(check_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except Exception:
            return False


    def execute_command(self, command, description):
        #print("---execute_command---")
        with Spinner(description):
            result = subprocess.run(command, shell=True)
            if result.returncode == 0:
                print(f"\033[92m✔ {description} - Success\033[0m")
            else:
                print(f"\033[91m✗ {description} - Failed\033[0m")


    def traverse_and_execute(self, node, path=None):
        #print(f"---traverse_and_execute---")
        # print(f"node: {str(node.items())}")
        # print(f"path type: {type(path)}")
        if path is None:
            path = []


        if isinstance(node, dict):
            for key, value in node.items():
                new_path = path + [key]
                if 'check' in value and 'command' in value:
                    check_cmd = value['check']
                    install_cmd = value['command']
                    if self.is_installed(check_cmd):
                        print(f"\033[93m⏩ Skipping {' > '.join(new_path)} (Already Installed)\033[0m")
                    else:
                        self.execute_command(install_cmd, f"Installing {' > '.join(new_path)}")
                elif isinstance(value, dict) and 'command' in value and 'items' in value:
                    for item in value['items']:
                        self.execute_command(f"{value['command']} {item}", f"Executing {' > '.join(new_path)} for {item}")
                else:
                    self.traverse_and_execute(value, new_path)
        elif isinstance(node, list):
            for item in node:
                self.traverse_and_execute(item, path)


    def run_installation(self):
        """Run the installation process.
        
        Returns:
            bool: True if all installations succeeded, False otherwise
        """
        #print("---run_installation---")
        # if not self.load_config():
        #     return False
            
        if self.config:
            # print(f"*** calling self.traverse_and_execute() | with parameter self.config: {str(self.config)}")
            os_type = 'windows' if platform.system().lower() == 'windows' else 'macos'            
            self.traverse_and_execute(self.config['installation']['tree'][os_type])
            return self.success
        return False


def main():
    """Main function to run the installation script."""
    if len(sys.argv) < 2:
        print("Usage: python installation.py <install_config.yaml>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    try:

        installer = InstallationManager(config_file)
        installer.load_config()
        success = installer.run_installation()
        
        if success:
            print("\nInstallation completed successfully!")
        else:
            print("\nInstallation completed with errors.")
            
        input("\nPress any key to exit...")
        return 0 if success else 1

    except FileNotFoundError as e:
        print(f"File not found Error: {str(e)}")
        return 1

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())