# Codebase to PDF

## Overview
A simple Python utility that generates a PDF document detailing the folder structure and file contents of a given codebase.

## Features
- Generates a visual representation of your project's folder structure.
- Includes the content of each file in the PDF.
- Optionally removes comments from code files.
- Configurable skip list to exclude specific files and directories.

## Requirements
- Python 3.x
- ReportLab library

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/elilat/utils-codebase-to-pdf.git
   cd utils-codebase-to-pdf
   ```

2. Install the required library:
   ```bash
   pip install reportlab
   ```

## Usage
Run the script with the following command:
```bash
python codebase_to_pdf.py <codebase_folder> <output_pdf>
```

**Example:**
```bash
python codebase_to_pdf.py ./my_project output.pdf
```

## Configuration
* **SKIP_LIST:** Modify the `SKIP_LIST` variable in `codebase_to_pdf.py` to add or remove files and directories that should be skipped.
* **REMOVE_COMMENTS:** Set this variable to `True` to remove comments from code files; set it to `False` to keep them.

## Project Structure
* `codebase_to_pdf.py`: Main script that processes the codebase and generates the PDF.
* `README.md`: This documentation file.

## Author
Elias Isaac (@elilat)