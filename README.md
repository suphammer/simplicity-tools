# Simplicity Tools

A Python package that wraps `slc-cli` and `zap` tools with automatic platform detection and download functionality.

## Features

- **Automatic Platform Detection**: Detects your operating system and architecture
- **Automatic Tool Download**: Downloads the appropriate version of `slc-cli` and `zap` tools for your platform
- **Easy Integration**: Simple Python API and command-line interface
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Installation

### From PyPI (when published)
```bash
pip install simplicity-tools
```

### From Source
```bash
git clone https://github.com/yourusername/simplicity-tools.git
cd simplicity-tools
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Install tools for your platform
simplicity-tools install

# Run slc-cli
simplicity-tools slc [options]

# Run zap
simplicity-tools zap [options]

# Check tool status
simplicity-tools status
```

### Python API

```python
from simplicity_tools import SimplicityTools

# Initialize the tools manager
tools = SimplicityTools()

# Install tools if needed
tools.ensure_tools_installed()

# Run slc-cli
result = tools.run_slc(['--help'])

# Run zap
result = tools.run_zap(['--version'])

# Get tool paths
slc_path = tools.get_slc_path()
zap_path = tools.get_zap_path()
```

## Configuration

The package automatically manages tool installations in the user's home directory. You can configure the installation directory by setting the `SIMPLICITY_TOOLS_DIR` environment variable.

## Supported Platforms

- **Windows**: x64, x86
- **macOS**: Intel, Apple Silicon (ARM64)
- **Linux**: x64, ARM64, ARM32

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/simplicity-tools.git
cd simplicity-tools
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Building Distribution

```bash
python setup.py sdist bdist_wheel
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Issues

Please report issues on the GitHub repository. 