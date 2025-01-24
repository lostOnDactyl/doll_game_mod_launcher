import os
from utils.file_utils import save_json, list_files , load_json
from utils.mod_utils import process_characters_and_objects, identify_conflicts

def aggregate_mods(directory):
    """Aggregate mod.json files from a directory."""
    aggregated_data = {}
    error_log = []

    for mod_path in list_files(directory, "mod.json"):
        mod_data = load_json(mod_path)
        if mod_data is None:
            error_log.append(f"Failed to load {mod_path}")
            continue

        mod_id = mod_data.get("id")
        if not mod_id:
            error_log.append(f"Missing 'id' in {mod_path}")
            continue

        aggregated_data[mod_id] = {
            "path": mod_path,
            "data": mod_data
        }

    return aggregated_data, error_log

def remove_duplicates(hash_usage):
    """Ensure each hash points to a unique list of mods."""
    return {hash_value: list(set(mod_ids)) for hash_value, mod_ids in hash_usage.items()}

def load_directory(dir, master):
    mods_directory = dir
    output_file = master

    # Aggregate mods
    aggregated_data, errors = aggregate_mods(mods_directory)

    # Save aggregated data
    try:
        save_json(aggregated_data, output_file)
        print(f"Aggregated data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving aggregated data: {e}")

    # Log errors
    if errors:
        error_log_file = os.path.splitext(output_file)[0] + "_errors.log"
        try:
            with open(error_log_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(errors))
            print(f"Errors logged to {error_log_file}")
        except Exception as e:
            print(f"Error saving error log: {e}")

    # TODO -> add these as settings
    chars_file = "./config/characters/characters.json"
    output_dir = "./config/mods"

    # Load data
    master_data = load_json(master)
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

# TBDeleted
'''
if __name__ == "__main__":
    # Paths
    script_directory = os.path.dirname(os.path.abspath(__file__))
    mods_directory = os.path.join(os.path.dirname(script_directory), "Mods") 
    output_file = os.path.join(script_directory, "master.json")

    # Aggregate mods
    aggregated_data, errors = aggregate_mods(mods_directory)

    # Save aggregated data
    try:
        save_json(aggregated_data, output_file)
        print(f"Aggregated data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving aggregated data: {e}")

    # Log errors
    if errors:
        error_log_file = os.path.splitext(output_file)[0] + "_errors.log"
        try:
            with open(error_log_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(errors))
            print(f"Errors logged to {error_log_file}")
        except Exception as e:
            print(f"Error saving error log: {e}")
'''
