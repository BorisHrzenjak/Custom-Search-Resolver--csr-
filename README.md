# CSR (Custom Search Resolver)

A powerful command-line interface (CLI) tool designed to mimic and extend the functionalities of the standard Windows search function.

## Installation

```bash
pip install .
```

## Usage

The tool can be invoked using the `csr` command followed by various options:

```bash
# Search for Python files
csr --name "*.py"

# Search for Python files containing specific text
csr --content "import os" --type "py"

# Search for large files in a specific directory
csr --size ">10MB" --path "C:\Users\Documents"

# Search recursively with JSON output
csr --name "*.txt" --recursive --output json

# Search system-wide for large Python files
csr --syswide --type "py" --size ">100MB"
```

## Options

- `--name`: Search for files by name (supports wildcards)
- `--content`: Search for files containing specific text
- `--type`: Search for files by type (file extension)
- `--size`: Search for files by size (e.g., >10MB, <1GB)
- `--modified`: Search for files by last modified date
- `--path`: Specify the directory to search within
- `--recursive`: Search recursively within directories
- `--syswide`: Search across all drives on the PC (excludes system directories)
- `--output`: Specify output format (table, list, or JSON)
- `--help`: Display help information

## Requirements

- Python 3.8 or higher
- Windows 10 Pro or later

## Dependencies

- click: Command line interface creation kit
- rich: Rich text and beautiful formatting in the terminal
- pathlib: Object-oriented filesystem paths
