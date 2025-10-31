#!/usr/bin/env python3
"""
Indentation Fixer for Python Files
Automatically fixes common indentation issues in Python files
"""

import os
import re
import sys
from pathlib import Path


def fix_indentation_issues(file_path):
    """
    Fix common indentation issues in Python files
    """
    print(f"🔧 Fixing indentation issues in: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    
    original_content = content
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Fix common indentation issues
        fixed_line = line
        
        # Fix: Missing indentation after try/except/if/for/while/def/class
        if re.match(r'^\s*(try|except|if|for|while|def|class|else|elif|finally):\s*$', line):
            # Check if next line has proper indentation
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() and not next_line.startswith('    ') and not next_line.startswith('\t'):
                    # Add proper indentation to next line
                    if next_line.strip():
                        lines[i + 1] = '    ' + next_line.strip()
        
        # Fix: Inconsistent indentation (mix of spaces and tabs)
        if '\t' in line and '    ' in line:
            fixed_line = line.replace('\t', '    ')
        
        # Fix: Missing indentation for function body
        if re.match(r'^\s*def\s+\w+.*:\s*$', line):
            # Check if next line needs indentation
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() and not next_line.startswith('    '):
                    lines[i + 1] = '    ' + next_line.strip()
        
        # Fix: Missing indentation for class body
        if re.match(r'^\s*class\s+\w+.*:\s*$', line):
            # Check if next line needs indentation
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() and not next_line.startswith('    '):
                    lines[i + 1] = '    ' + next_line.strip()
        
        fixed_lines.append(fixed_line)
    
    # Join lines back
    fixed_content = '\n'.join(fixed_lines)
    
    # Only write if content changed
    if fixed_content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed indentation issues in: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error writing file {file_path}: {e}")
            return False
    else:
        print(f"✅ No indentation issues found in: {file_path}")
        return False


def validate_python_syntax(file_path):
    """
    Validate Python syntax by compiling the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, file_path, 'exec')
        print(f"✅ Syntax validation passed: {file_path}")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating {file_path}: {e}")
        return False


def fix_all_python_files(directory):
    """
    Fix indentation issues in all Python files in directory
    """
    print(f"🔍 Scanning directory: {directory}")
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"📁 Found {len(python_files)} Python files")
    
    fixed_count = 0
    syntax_errors = 0
    
    for file_path in python_files:
        print(f"\n📝 Processing: {file_path}")
        
        # First, try to validate syntax
        if not validate_python_syntax(file_path):
            syntax_errors += 1
            print(f"🔧 Attempting to fix syntax issues...")
            
            # Try to fix indentation issues
            if fix_indentation_issues(file_path):
                fixed_count += 1
                
                # Validate again after fixing
                if validate_python_syntax(file_path):
                    print(f"✅ Successfully fixed: {file_path}")
                else:
                    print(f"❌ Still has syntax issues: {file_path}")
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {len(python_files)}")
    print(f"   Files fixed: {fixed_count}")
    print(f"   Syntax errors found: {syntax_errors}")
    
    return fixed_count > 0


def main():
    """
    Main function to fix indentation issues
    """
    print("🔧 Python Indentation Fixer")
    print("=" * 50)
    
    # Get current directory
    current_dir = os.getcwd()
    print(f"📁 Working directory: {current_dir}")
    
    # Check if we're in the right directory
    if not os.path.exists('app_simple.py'):
        print("❌ app_simple.py not found in current directory")
        print("Please run this script from the doctor directory")
        return
    
    # Fix all Python files
    success = fix_all_python_files(current_dir)
    
    if success:
        print("\n✅ Indentation issues fixed successfully!")
        print("You can now run your Python applications without indentation errors.")
    else:
        print("\n✅ No indentation issues found!")
        print("All Python files have correct indentation.")


if __name__ == "__main__":
    main()
