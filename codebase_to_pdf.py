#!/usr/bin/env python3
"""
Codebase to PDF

This script scans a given codebase folder, builds a representation of its folder structure,
and exports both the structure and the content of each file into a PDF document.
Optionally, it can remove comments from code files based on their file extension.
"""

import os
import sys
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Preformatted, PageBreak

# ==========================
# Configuration Variables
# ==========================
# List of directory or file patterns (in POSIX format) to skip during processing.
SKIP_LIST = [
    'node_modules',
    '.env',
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
    'eslint.config.mjs'
]

# Set to True to remove code comments based on file extension; otherwise, leave them intact.
REMOVE_COMMENTS = True

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

def generate_pdf(root_folder, output_pdf):
    """
    Generate a PDF document containing the folder structure and file contents.

    Parameters:
        root_folder (str): The codebase root directory.
        output_pdf (str): Path for the output PDF file.
    """
    # Create folder structure overview
    folder_tree = build_folder_tree(root_folder)
    
    # Get list of files to process
    files = gather_files(root_folder)
    
    # Initialize PDF document with ReportLab
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    styles = getSampleStyleSheet()
    code_style = ParagraphStyle(
        name='Code',
        fontName='Courier',
        fontSize=8,
        leading=10,
    )
    story = []
    
    # Add folder structure to PDF
    story.append(Paragraph("Folder Structure", styles['Heading1']))
    story.append(Preformatted(folder_tree, code_style))
    story.append(PageBreak())
    
    # Add each file's content to PDF
    for filepath in files:
        relative_path = os.path.relpath(filepath, root_folder)
        story.append(Paragraph(relative_path, styles['Heading2']))
        code_content = process_file(filepath)
        story.append(Preformatted(code_content, code_style))
        story.append(PageBreak())
    
    # Build the PDF file
    doc.build(story)
    print(f"PDF generated successfully: {output_pdf}")

def main():
    """
    Main entry point of the script.
    
    Expects two command-line arguments: the codebase folder and the output PDF file path.
    """
    if len(sys.argv) < 3:
        print("Usage: python export_code.py <codebase_folder> <output_pdf>")
        sys.exit(1)
    
    root_folder = sys.argv[1]
    output_pdf = sys.argv[2]
    generate_pdf(root_folder, output_pdf)

if __name__ == "__main__":
    main()
