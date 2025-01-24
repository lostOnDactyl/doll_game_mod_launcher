from collections import defaultdict

def process_characters_and_objects(mod_data, valid_chars):
    """Process mod data to extract character, object, and hash usage information."""
    character_data = defaultdict(lambda: defaultdict(list))
    object_data = defaultdict(lambda: defaultdict(list))
    hash_usage = defaultdict(list)
    non_skinmod_data = defaultdict(list)

    for mod_id, mod_entry in mod_data.items():
        data = mod_entry.get("data", {})
        # Normalize `skinmod` to a boolean
        skinmod = str(data.get("skinmod", "false")).lower() == "true"

        if skinmod:
            # Process skinmod targets
            targets = data.get("targets", [])
            for target in targets:
                # Check for object mods
                if "object" in target:
                    obj_name = target.get("object", "Unknown Object")
                    target_type = target.get("type", "Unknown Type")
                    note = target.get("note", "")
                    hash_value = target.get("hash", "Unknown Hash")

                    object_data[obj_name][target_type].append({
                        "mod": mod_id,
                        "hash": hash_value,
                        "note": note
                    })
                    hash_usage[hash_value].append(mod_id)

                # Process character mods
                elif "char" in target:
                    char = target.get("char", "").upper()
                    if char not in valid_chars:
                        print(f"Invalid character '{char}' in mod '{mod_id}'. Skipping.")
                        continue

                    target_type = target.get("type", "Unknown Type")
                    note = target.get("note", "")
                    hash_value = target.get("hash", "Unknown Hash")

                    character_data[char][target_type].append({
                        "mod": mod_id,
                        "hash": hash_value,
                        "note": note
                    })
                    hash_usage[hash_value].append(mod_id)

            # Process buffers for skinmod
            buffers = data.get("buffers", [])
            for buffer_hash in buffers:
                hash_usage[buffer_hash].append(mod_id)
        else:
            # Process non-skinmod
            non_skinmod_data[mod_id].append({
                "description": data.get("description", ""),
                "version": data.get("version", "Unknown Version"),
                "authors": data.get("authors", []),
                "buffers": data.get("buffers", [])
            })

    return character_data, object_data, hash_usage, non_skinmod_data

def identify_conflicts(hash_usage):
    """Identify hash conflicts between mods."""
    conflicts = []
    for hash_value, mod_ids in hash_usage.items():
        if len(mod_ids) > 1:
            conflicts.append({"hash": hash_value, "mods": mod_ids})
    return conflicts