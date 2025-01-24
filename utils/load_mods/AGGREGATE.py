# TBDeleted

import os
from utils.file_utils import save_json, list_files, load_json
from utils.mod_utils import process_characters_and_objects, identify_conflicts

def remove_duplicates(hash_usage):
    """Ensure each hash points to a unique list of mods."""
    return {hash_value: list(set(mod_ids)) for hash_value, mod_ids in hash_usage.items()}

if __name__ == "__main__":
    master_file = "./master.json"
    chars_file = "./config/characters/characters.json"
    output_dir = "./loaded"

    # Load data
    master_data = load_json(master_file)
    if master_data is None:
        print("Failed to load master.json")
        exit(1)

    chars_data = load_json(chars_file)
    if chars_data is None:
        print("Failed to load characters.json")
        exit(1)

    valid_chars = set(chars_data.get("survivors", []) + chars_data.get("hunters", []))

    # Process characters, objects, and hashes
    character_data, object_data, hash_usage, non_skinmod_data = process_characters_and_objects(master_data, valid_chars)

    # Remove duplicates from hash usage
    hash_usage = remove_duplicates(hash_usage)

    # Identify conflicts
    conflicts = identify_conflicts(hash_usage)

    # Save parsed data
    parsed_data = {
        "character_data": character_data,
        "object_data": object_data,
        "non_skinmod_data": non_skinmod_data
    }
    save_json(parsed_data, os.path.join(output_dir, "loaded.json"))
    save_json(conflicts, os.path.join(output_dir, "hash_conflicts.json"))
