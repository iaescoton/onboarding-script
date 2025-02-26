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


def is_installed(check_command):
    try:
        result = subprocess.run(check_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False


def execute_command(command, description):
    with Spinner(description):
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            print(f"\033[92m✔ {description} - Success\033[0m")
        else:
            print(f"\033[91m✗ {description} - Failed\033[0m")


def traverse_and_execute(node, path=None):
    if path is None:
        path = []

    if isinstance(node, dict):
        for key, value in node.items():
            new_path = path + [key]
            if 'check' in value and 'command' in value:
                check_cmd = value['check']
                install_cmd = value['command']
                if is_installed(check_cmd):
                    print(f"\033[93m⏩ Skipping {' > '.join(new_path)} (Already Installed)\033[0m")
                else:
                    execute_command(install_cmd, f"Installing {' > '.join(new_path)}")
            # elif 'command' in value:
            #     for cmd_name, cmd in value['command'].items():
            #         execute_command(cmd, f"Executing {' > '.join(new_path)} > {cmd_name}")
            elif isinstance(value, dict) and 'command' in value and 'items' in value:
                for item in value['items']:
                    execute_command(f"{value['command']} {item}", f"Executing {' > '.join(new_path)} for {item}")
            else:
                traverse_and_execute(value, new_path)
    elif isinstance(node, list):
        for item in node:
            traverse_and_execute(item, path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python install_script.py <install_config.yml>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        print(f"YAML file '{config_file}' not found!")
        sys.exit(1)

    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    os_type = 'windows' if platform.system().lower() == 'windows' else 'macos'
    print(f"Starting installation for {os_type.capitalize()}...\n")
    os_config = config['installation']['tree'][os_type]
    traverse_and_execute(os_config)
    
    input("\nInstallation complete! Press any key to exit...")


if __name__ == '__main__':
    main()
