import json
from collections import defaultdict


def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def identify_hash_conflicts(master_data):
    """Identify hash conflicts in mods."""
    hash_usage = defaultdict(list)
    for mod_entry in master_data.values():
        buffers = mod_entry["data"].get("buffers", [])
        for buf in buffers:
            hash_usage[buf].append(mod_entry["data"]["id"])
    return {h: mods for h, mods in hash_usage.items() if len(mods) > 1}


def sort_mods(master_data, valid_characters):
    """Sort mods into categories and ensure `type` is correctly identified."""
    sorted_mods = {"character_mods": [], "object_mods": [], "non_skinmods": []}

    for mod_id, mod_entry in master_data.items():
        data = mod_entry["data"]
        path = mod_entry.get("path", "Unknown")

        # Determine type
        targets = data.get("targets", [])
        if data.get("skinmod", False):
            char_targets = [t for t in targets if "char" in t and t["char"].upper() in valid_characters]
            obj_targets = [t for t in targets if "object" in t]

            if char_targets:
                mod_type = "character"
                sorted_mods["character_mods"].append({
                    "id": mod_id,
                    "data": data,
                    "path": path,
                    "type": mod_type,
                    "targets": char_targets,
                })
            elif obj_targets:
                mod_type = "object"
                sorted_mods["object_mods"].append({
                    "id": mod_id,
                    "data": data,
                    "path": path,
                    "type": mod_type,
                    "targets": obj_targets,
                })
        else:
            mod_type = "non-skinmod"
            sorted_mods["non_skinmods"].append({
                "id": mod_id,
                "data": data,
                "path": path,
                "type": mod_type,
            })

    return sorted_mods
