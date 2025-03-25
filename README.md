# Codebase Export

## Overview
A Python utility that generates a PDF or TXT document detailing the folder structure and file contents of a given codebase, with intelligent line wrapping to prevent content from being cut off by margins.

## Features
- Generates a visual representation of your project's folder structure
- Includes the content of each file in the output document
- Intelligently wraps long lines to prevent them from being cut off
- Automatically detects output format based on file extension (.pdf or .txt)
- Optionally removes comments from code files
- Configurable skip list to exclude specific files and directories

## Requirements
- Python 3.x
- ReportLab library (for PDF output only)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/elilat/utils-codebase-export.git
   cd utils-codebase-export
   ```

2. Install the required library (for PDF output):
   ```bash
   pip install reportlab
   ```

## Usage
Run the script with the following command:
```bash
python codebase_export.py <codebase_folder> <output_file> [--remove-comments]
```

### Parameters:
- `<codebase_folder>`: Directory containing the codebase to export
- `<output_file>`: Destination file for the output (.pdf or .txt extension)
- `--remove-comments`: Optional flag to remove comments from code files

The output format is automatically determined by the file extension of the output file. If no extension is provided, PDF format is used by default.

### Examples:
```bash
# Generate PDF output
python codebase_export.py ./my_project output.pdf

# Generate TXT output
python codebase_export.py ./my_project output.txt

# Generate PDF with comments removed
python codebase_export.py ./my_project output.pdf --remove-comments

# If no extension is given, defaults to PDF
python codebase_export.py ./my_project output --remove-comments
```

## Configuration
* **SKIP_LIST:** Modify the `SKIP_LIST` variable in `codebase_export.py` to add or remove files and directories that should be skipped.
* **REMOVE_COMMENTS:** Set this variable to `True` to remove comments from code files by default; set it to `False` to keep them. This can also be controlled via the command line.
* **MAX_LINE_WIDTH:** Set the maximum character width for code lines in the output (default: 100 characters).

## Project Structure
* `codebase_export.py`: Main script that processes the codebase and generates the output file.
* `README.md`: This documentation file.

## Author
Elias Isaac (@elilat)
