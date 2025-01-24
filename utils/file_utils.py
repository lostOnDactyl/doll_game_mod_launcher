import os
import json

def load_json(file_path):
    """Load JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None

def save_json(data, file_path):
    """Save data to JSON"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")

def list_files(directory, extension):
    """All files with certain ext in dir and its subdirs."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                yield os.path.join(root, file)