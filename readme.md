# Development Environment Installer

A robust Python application for automating the setup of development environments on Windows and macOS. This tool streamlines the installation of programming languages, development tools, editors, and other software using system package managers (Chocolatey for Windows and Homebrew for macOS).

## Features

- **Cross-Platform Support**: Works on both Windows and macOS
- **YAML Configuration**: Flexible, easy-to-modify installation configurations
- **Smart Installation**: Checks for existing installations to avoid redundancy
- **Progress Tracking**: Real-time installation progress with rich visual feedback
- **Detailed Logging**: Comprehensive logging system for troubleshooting
- **Error Handling**: Robust error handling and reporting
- **Installation Summary**: Detailed summary of successful and failed installations

## Prerequisites

- Python:
  - 3.7 or higher
  - recommended: 
- Windows or macOS operating system
- Administrator/sudo privileges

For Windows:
- PowerShell:
  - with execution policy allowing script execution
  - should be executed with adminitrative rights

For macOS:
- Terminal access
- Command Line Tools (will be installed with Homebrew if not present)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dev-environment-installer.git
cd dev-environment-installer
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python installation.py install_config.yaml
```

### Advanced Options

```bash
# Skip confirmation prompt
python installation.py install_config.yaml --skip-confirmation

# Enable debug logging
python installation.py install_config.yaml --debug

# View help
python installation.py --help


# create executable (make sure pyinstaller is already installed via `pip install pyinstaller`)
pyinstaller --onefile installation.py --name <filename of the executable>
```

## Configuration

The installer uses a YAML configuration file to define the installation process. Here's an example structure:

```yaml
installation:
  tree:
    windows:  # Windows-specific configuration
      package_manager:
        name: chocolatey
        commands:
          install: <installation command>
          verify: <verification command>      
      python:
        check: where python
        command: choco install -y python
    macos:    # macOS-specific configuration
      package_manager:
        name: homebrew
        commands:
          install: <installation command>
          verify: <verification command>
      name: python
        check: which python
        command: brew install python
```

## Running tests

To execute tests using `pytest`, use the following:
```
pytest -v tests/
```


## Logging

The installer creates detailed logs in `installation.log`. Log levels can be controlled using the `--debug` flag:

- ~~INFO: Default level, shows main installation steps~~
- ~~DEBUG: Detailed logging for troubleshooting~~
- ~~ERROR: Installation failures and errors~~

\* currently not yet implemented

## Error Handling

The installer handles various types of errors:
- Configuration file errors
- Installation failures
- Command execution errors
- System permission issues

Failed installations are reported in the installation summary with detailed error messages.

## Contributing

1. Fork the repository
1. Create a feature branch (`git checkout -b feature/AmazingFeature`)
1. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
1. Push to the branch (`git push origin feature/AmazingFeature`)
1. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **Permission Errors**
   - Windows: Run PowerShell as Administrator
   - macOS: Use sudo when necessary

1. **Package Manager Installation Fails**
   - Windows: Ensure PowerShell execution policy allows script execution
   - macOS: Install Command Line Tools first: `xcode-select --install`

1. **Tool Installation Fails**
   - Check internet connection
   - Verify package name in configuration
   - Check system requirements for specific tools

### Getting Help

1. Check the logs in `installation.log`
1. Enable debug mode with `--debug` flag
1. Open an issue on GitHub with:
   - Log contents
   - System information
   - Configuration file
   - Error messages

## Roadmap

- # v.0.1.0 Roadmap
  - [ ] Logging
  - [ ] **DEBUG** and **VERBOSE** modes
  - [ ] yaml versioning
  - [ ] switching to [Poetry](https://python-poetry.org/)
  - [ ] specific version to install
  - [ ] Custom installation sequences
  - [ ] Installation profiles
  - [ ] Update checking for installed tools
  - [ ] ~~GUI interface~~ _(this will remain as a cli tool only)_

## Requirements

```txt
altgraph==0.17.4
colorama==0.4.6
iniconfig==2.0.0
markdown-it-py==3.0.0
mdurl==0.1.2
packaging==24.2
pefile==2023.2.7
pluggy==1.5.0
Pygments==2.19.1
pyinstaller==6.12.0
pyinstaller-hooks-contrib==2025.1
pytest==8.3.4
pywin32-ctypes==0.2.3
PyYAML==6.0.2
rich==13.9.4
setuptools==75.8.0
tqdm==4.67.1
```

# Notes:

1. When creating an executable [using pyinstaller](https://pyinstaller.org/en/v4.1/usage.html), if you are using python v3.14 or highter, you will encounter an error wherein a library `imp` is missing, since that library is removed in Python 3.14.*.