import os
import fnmatch
import sys
import re

def parse_gitignore(gitignore_file):
    if os.path.exists(gitignore_file):
        with open(gitignore_file, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

def is_git_ignored_by_default(path):
    ignored_patterns = [
        '.git',
        '.git/**',
        '.gitignore',
        '.gitmodules',
        '.gitattributes',
    ]
    name = os.path.basename(path)
    return any(fnmatch.fnmatch(name, pattern) for pattern in ignored_patterns)

def pattern_to_regex(pattern):
    pattern = pattern.replace('.', r'\.')  # Escape dots
    pattern = pattern.replace('**', '.*')  # Convert ** to .*
    pattern = pattern.replace('*', '[^/]*')  # Convert * to [^/]*
    pattern = pattern.replace('?', '.')  # Convert ? to .
    if pattern.startswith('/'):
        pattern = '^' + pattern[1:]  # Anchor at start if pattern starts with /
    else:
        pattern = '(^|/)' + pattern  # Match at start or after /
    if pattern.endswith('/'):
        pattern += '.*'  # Match anything after trailing /
    else:
        pattern += '(/.*)?$'  # Optionally match / and anything after
    return re.compile(pattern)

def should_ignore(path, base_path, ignore_patterns, script_path):
    if path == script_path:
        return True
    if is_git_ignored_by_default(path):
        return True
    
    rel_path = os.path.relpath(path, base_path)
    
    for pattern in ignore_patterns:
        if pattern.search(rel_path):
            return True
    return False

def generate_directory_tree(root_dir, base_path=None, prefix="", is_last=True, ignore_patterns=None, script_path=None):
    tree = ""
    root_dir = os.path.abspath(root_dir)
    
    if not os.path.isdir(root_dir):
        return "Error: Not a valid directory"

    if base_path is None:
        base_path = root_dir
        gitignore_path = os.path.join(root_dir, '.gitignore')
        ignore_patterns = parse_gitignore(gitignore_path)
        ignore_patterns = [pattern_to_regex(p) for p in ignore_patterns]

    if root_dir != base_path:
        if not is_last:
            tree += prefix + "├── " + os.path.basename(root_dir) + "\n"
            prefix += "│   "
        else:
            tree += prefix + "└── " + os.path.basename(root_dir) + "\n"
            prefix += "    "

    try:
        files = os.listdir(root_dir)
    except PermissionError:
        return tree + prefix + "Permission denied\n"

    files = [f for f in files if not should_ignore(os.path.join(root_dir, f), base_path, ignore_patterns, script_path)]
    files = sorted(files, key=lambda f: (os.path.isfile(os.path.join(root_dir, f)), f))
    
    for i, file in enumerate(files):
        path = os.path.join(root_dir, file)
        is_last_file = (i == len(files) - 1)
        
        if os.path.isdir(path):
            tree += generate_directory_tree(path, base_path, prefix, is_last_file, ignore_patterns, script_path)
        else:
            if is_last_file:
                tree += prefix + "└── " + file + "\n"
            else:
                tree += prefix + "├── " + file + "\n"
    
    return tree

# Example usage
if __name__ == "__main__":
    directory = "."  # Current directory
    script_path = os.path.abspath(__file__)
    print(generate_directory_tree(directory, script_path=script_path))