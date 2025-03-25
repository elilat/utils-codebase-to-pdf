#!/usr/bin/env python3
"""
Codebase Export

This script scans a given codebase folder, builds a representation of its folder structure,
and exports both the structure and the content of each file into a PDF or TXT document.
The output format is automatically determined based on the output file extension.
Optionally, it can remove comments from code files based on their file extension.
Lines that are too long are automatically wrapped to prevent being cut off by margins.
"""

import os
import sys
import re
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Preformatted, PageBreak
from reportlab.lib.units import inch

# ==========================
# Configuration Variables
# ==========================
# List of directory or file patterns (in POSIX format) to skip during processing.
SKIP_LIST = [
    'node_modules',
    '.env',
    '.next',
    'test',
    'tests',
    'package-lock.json',
    '.DS_Store',
    '.next',
    '.git',
    '.env.local',
    'public',
    'jsconfig.json',
    'postcss.config.mjs',
    'next.config.mjs',
    'README.md',
    'tailwind.config.mjs',
    '.gitignore',
    'eslint.config.mjs',
    'venv',
    '.DS_Store',
    'frontend/.DS_Store',
    'backend/.DS_Store',
    'frontend/node_modules',
    'frontend/package-lock.json',
]

# Set to True to remove code comments based on file extension; otherwise, leave them intact.
REMOVE_COMMENTS = False

# Maximum width for code lines (in characters)
# This will be used for TXT export and as a guide for PDF wrapping
MAX_LINE_WIDTH = 100

# ==========================
# Helper Functions
# ==========================

def should_skip(rel_path):
    """
    Determine if a given relative path should be skipped.

    Converts the path to POSIX style and checks for an exact match or a nested match in SKIP_LIST.

    Parameters:
        rel_path (str): Relative path from the codebase root.

    Returns:
        bool: True if the path is in SKIP_LIST; False otherwise.
    """
    posix_rel_path = rel_path.replace(os.sep, '/')
    for skip in SKIP_LIST:
        if posix_rel_path == skip or posix_rel_path.startswith(skip + '/'):
            return True
    return False

def remove_comments(code, file_extension):
    """
    Remove comments from a code string based on its file extension.
    
    This uses regex substitutions to remove both single-line and block comments.
    Note: This is a best-effort approach and may not cover every edge case.

    Parameters:
        code (str): The original code.
        file_extension (str): The file extension (e.g., '.py', '.js').

    Returns:
        str: The code with comments removed.
    """
    ext = file_extension.lower()
    if ext in ['.js', '.ts', '.cpp', '.c', '.h', '.cs', '.java', '.go', '.swift', '.rs']:
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'//.*', '', code)
    elif ext == '.py':
        code = re.sub(r'#.*', '', code)
    elif ext in ['.html', '.htm']:
        code = re.sub(r'<!--.*?-->', '', code, flags=re.DOTALL)
    elif ext == '.css':
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    elif ext in ['.rb', '.sh', '.bash']:
        code = re.sub(r'#.*', '', code)
    elif ext == '.php':
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'#.*', '', code)
    else:
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'//.*', '', code)
    return code

def wrap_long_lines(code, max_width=MAX_LINE_WIDTH):
    """
    Wrap long lines of code to prevent them from being cut off in the output.
    
    Parameters:
        code (str): The original code.
        max_width (int): Maximum width for each line.
    
    Returns:
        str: Code with long lines wrapped.
    """
    lines = code.split('\n')
    wrapped_lines = []
    
    for line in lines:
        if len(line) > max_width:
            # Preserve indentation for wrapped lines
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * (indent + 4)  # Add 4 spaces extra indent for continuation
            
            # Get the indented part
            indented_part = line[:indent]
            # Get the content part
            content_part = line[indent:]
            
            # Wrap the content part
            wrapped_content = textwrap.fill(
                content_part,
                width=max_width - indent,  # Account for indent in width
                subsequent_indent=indent_str,
                break_long_words=False,
                break_on_hyphens=False
            )
            
            # Add the indented part back to the wrapped content
            if wrapped_content.startswith(indent_str):
                wrapped_lines.append(wrapped_content)
            else:
                wrapped_lines.append(indented_part + wrapped_content[indent:])
        else:
            wrapped_lines.append(line)
    
    return '\n'.join(wrapped_lines)

def build_folder_tree(root):
    """
    Create a string that represents the folder structure starting at the root.

    Skips directories and files listed in SKIP_LIST.

    Parameters:
        root (str): Root directory of the codebase.

    Returns:
        str: A formatted string showing the folder hierarchy.
    """
    tree_lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == '.':
            rel_dir = ''
        # Filter out directories to skip
        dirnames[:] = [d for d in dirnames if not should_skip(os.path.join(rel_dir, d))]
        depth = rel_dir.count(os.sep) if rel_dir else 0
        indent = '    ' * depth
        dir_display = os.path.basename(dirpath) if rel_dir else os.path.basename(os.path.abspath(root))
        tree_lines.append(f"{indent}{dir_display}/")
        for f in filenames:
            file_rel = os.path.join(rel_dir, f) if rel_dir else f
            if should_skip(file_rel):
                continue
            tree_lines.append(f"{indent}    {f}")
    return "\n".join(tree_lines)

def gather_files(root):
    """
    Recursively collect all file paths in the codebase that are not in SKIP_LIST.

    Parameters:
        root (str): Root directory of the codebase.

    Returns:
        list: A list of absolute file paths.
    """
    file_entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == '.':
            rel_dir = ''
        # Exclude directories to skip
        dirnames[:] = [d for d in dirnames if not should_skip(os.path.join(rel_dir, d))]
        for f in filenames:
            file_rel = os.path.join(rel_dir, f) if rel_dir else f
            if should_skip(file_rel):
                continue
            full_path = os.path.join(dirpath, f)
            file_entries.append(full_path)
    return file_entries

def process_file(filepath):
    """
    Read a file's content and optionally remove comments.

    Parameters:
        filepath (str): Absolute path to the file.

    Returns:
        str: The file content after optional processing.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        content = f"Error reading file: {e}"
    if REMOVE_COMMENTS:
        _, ext = os.path.splitext(filepath)
        content = remove_comments(content, ext)
    return content

def generate_pdf(root_folder, output_file):
    """
    Generate a PDF document containing the folder structure and file contents.

    Parameters:
        root_folder (str): The codebase root directory.
        output_file (str): Path for the output PDF file.
    """
    # Create folder structure overview
    folder_tree = build_folder_tree(root_folder)
    
    # Get list of files to process
    files = gather_files(root_folder)
    
    # Initialize PDF document with ReportLab
    doc = SimpleDocTemplate(output_file, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch)
    styles = getSampleStyleSheet()
    code_style = ParagraphStyle(
        name='Code',
        fontName='Courier',
        fontSize=8,
        leading=10,
    )
    
    # Calculate available width for code in PDF
    available_width = letter[0] - doc.leftMargin - doc.rightMargin
    # Approximate characters per inch for Courier 8pt
    chars_per_inch = 12
    max_chars = int(available_width / inch * chars_per_inch)
    
    story = []
    
    # Add folder structure to PDF
    story.append(Paragraph("Folder Structure", styles['Heading1']))
    # Wrap folder tree text if needed
    wrapped_folder_tree = wrap_long_lines(folder_tree, max_chars)
    story.append(Preformatted(wrapped_folder_tree, code_style))
    story.append(PageBreak())
    
    # Add each file's content to PDF
    for filepath in files:
        relative_path = os.path.relpath(filepath, root_folder)
        story.append(Paragraph(relative_path, styles['Heading2']))
        code_content = process_file(filepath)
        # Wrap long lines to fit the PDF width
        wrapped_content = wrap_long_lines(code_content, max_chars)
        story.append(Preformatted(wrapped_content, code_style))
        story.append(PageBreak())
    
    # Build the PDF file
    doc.build(story)
    print(f"PDF generated successfully: {output_file}")

def generate_txt(root_folder, output_file):
    """
    Generate a TXT document containing the folder structure and file contents.

    Parameters:
        root_folder (str): The codebase root directory.
        output_file (str): Path for the output TXT file.
    """
    # Create folder structure overview
    folder_tree = build_folder_tree(root_folder)
    wrapped_folder_tree = wrap_long_lines(folder_tree)
    
    # Get list of files to process
    files = gather_files(root_folder)
    
    with open(output_file, 'w', encoding='utf-8') as txt_file:
        # Write folder structure
        txt_file.write("=" * 80 + "\n")
        txt_file.write("FOLDER STRUCTURE\n")
        txt_file.write("=" * 80 + "\n\n")
        txt_file.write(wrapped_folder_tree)
        txt_file.write("\n\n")
        
        # Write each file's content
        for filepath in files:
            relative_path = os.path.relpath(filepath, root_folder)
            txt_file.write("=" * 80 + "\n")
            txt_file.write(f"FILE: {relative_path}\n")
            txt_file.write("=" * 80 + "\n\n")
            
            code_content = process_file(filepath)
            # Wrap long lines
            wrapped_content = wrap_long_lines(code_content)
            txt_file.write(wrapped_content)
            txt_file.write("\n\n")
    
    print(f"TXT file generated successfully: {output_file}")

def main():
    """
    Main entry point of the script.
    
    Expects command-line arguments for the codebase folder, output file, and optional flags.
    Automatically determines the output format based on the file extension.
    """
    if len(sys.argv) < 3:
        print("Usage: python codebase_export.py <codebase_folder> <output_file> [--remove-comments]")
        print("  Output format is automatically determined based on file extension (.pdf or .txt)")
        print("  --remove-comments  Remove comments from code files")
        sys.exit(1)
    
    root_folder = sys.argv[1]
    output_file = sys.argv[2]
    
    # Parse optional arguments
    global REMOVE_COMMENTS
    
    for arg in sys.argv[3:]:
        if arg == "--remove-comments":
            REMOVE_COMMENTS = True
    
    # Determine output format based on file extension
    _, ext = os.path.splitext(output_file)
    if not ext:
        # Default to PDF if no extension provided
        output_file += ".pdf"
        ext = ".pdf"
    
    # Generate output based on file extension
    if ext.lower() == ".pdf":
        try:
            generate_pdf(root_folder, output_file)
        except ImportError:
            print("Error: ReportLab library is required for PDF generation.")
            print("Please install it using: pip install reportlab")
            sys.exit(1)
    elif ext.lower() == ".txt":
        generate_txt(root_folder, output_file)
    else:
        print(f"Unsupported file extension: {ext}. Use '.pdf' or '.txt'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
