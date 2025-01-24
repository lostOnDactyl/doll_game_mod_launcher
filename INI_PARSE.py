import json
import os
import re
import argparse

def parse_ini(ini_file, output_dir):
    """Parse a .ini file for shader mod, skin mod, or object mod metadata and generate a mod.json file."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Data for mod.json
    mod_data = {
        "id": "auto_generated_mod",
        "ini": os.path.basename(ini_file),
        "skinmod": False,
        "description": "",
        "version": "1",
        "authors": [],
        "targets": [],
        "buffers": []
    }

    # Detect if the mod is a shader mod or object mod
    is_shader_mod = False
    is_object_mod = False

    # Read the .ini file line-by-line
    try:
        with open(ini_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError as e:
        print(f"Error reading .ini file: {e}")
        return

    current_note = None  # Holds the most recent note
    current_section = None  # Tracks the current section being processed

    # Parse the .ini file
    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Parse notes for metadata or shader/object toggle
        if line.startswith(";"):
            note = line.lstrip(";").strip()

            # Detect metadata in notes
            if note.startswith("id="):
                mod_data["id"] = note.split("=", 1)[1].strip()
            elif note.startswith("desc="):
                mod_data["description"] = note.split("=", 1)[1].strip()
            elif note.startswith("author="):
                mod_data["authors"].append(note.split("=", 1)[1].strip())
            elif note.startswith("skinmod="):
                mod_data["skinmod"] = note.split("=", 1)[1].strip().lower() == "true"
            elif note.startswith("version="):
                mod_data["version"] = note.split("=", 1)[1].strip()
            elif note.startswith("SHADER = true"):
                is_shader_mod = True
            elif note.startswith("OBJECT = true"):
                is_object_mod = True

            # Parse notes for targets (e.g., char/object, type, note)
            else:
                current_note = {}
                note_match = re.search(r'note=(.+)', note)
                target_key = "object" if is_object_mod else "char"
                target_match = re.search(rf'{target_key}=([\w]+)', note)
                type_match = re.search(r'type=([\w]+)', note)
                if note_match:
                    current_note["note"] = note_match.group(1).strip()
                if target_match:
                    current_note[target_key] = target_match.group(1).strip()
                if type_match:
                    current_note["type"] = type_match.group(1).strip()
            continue

        # Handle shader mods
        if is_shader_mod:
            ini_folder = os.path.dirname(ini_file)
            shader_files = [f for f in os.listdir(ini_folder) if f.endswith("_replace.txt")]
            for shader_file in shader_files:
                shader_id = shader_file.rsplit("-", 1)[0]  # Extract the identifier before the "-replace.txt"
                if shader_id not in mod_data["buffers"]:
                    mod_data["buffers"].append(shader_id)
            break  # Stop further processing for shader mods

        # Detect sections for standard mods
        if line.startswith("[") and line.endswith("]"):
            current_section = line.strip("[]")
            continue

        # Process section content
        if current_section and "=" in line:
            key, value = map(str.strip, line.split("=", 1))
            if key == "hash":
                # Add hash to buffers
                if value not in mod_data["buffers"]:
                    mod_data["buffers"].append(value)

                # Add to targets if a note exists
                if current_note:
                    target_entry = {
                        "hash": value
                    }
                    target_entry.update(current_note)  # Add char/object, type, and note if available
                    mod_data["targets"].append(target_entry)
                    current_note = None  # Reset note after use

    # Generate output file path
    output_file = os.path.join(output_dir, "mod.json")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mod_data, f, indent=4, ensure_ascii=False)
        print(f"mod.json file successfully created at: {output_file}")
    except Exception as e:
        print(f"Error writing mod.json file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse an INI file and output the results to directory.")
    
    parser.add_argument(
        "ini_path",
        type=str,
        help="Path to the .ini file to be parsed."
    )
    parser.add_argument(
        "--output_directory",
        type=str,
        default=None,
        help="Directory where the parsed output will be saved. Defaults to the parent directory of the .ini file."
    )

    args = parser.parse_args()

    # Determine the default output directory if not specified
    output_directory = args.output_directory
    if output_directory is None:
        output_directory = os.path.dirname(os.path.abspath(args.ini_path))

    # Ensure the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    parse_ini(args.ini_path, output_directory)
