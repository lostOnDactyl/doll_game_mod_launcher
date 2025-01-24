# TODO im going to make a better way of dealing with this later
# when youre not high you idito

import os

def toggle_mod_ini(mod_path, ini_name, enable):
    """
    Enable or disable a mod by renaming its .ini file to .Xini or back to .ini.

    Args:
        mod_path (str): Path to the mod folder.
        ini_name (str): Name of the .ini file.
        enable (bool): True to enable the mod, False to disable it.
    """
    if not os.path.isdir(mod_path):
        print(f"Error: Mod path does not exist or is not a directory: {mod_path}")
        return

    ini_path = os.path.join(mod_path, ini_name)
    xini_path = os.path.join(mod_path, ini_name.replace(".ini", ".Xini"))

    if enable:
        # Enable the mod by ensuring it is named with .ini
        if os.path.exists(xini_path):
            os.rename(xini_path, ini_path)
            print(f"Enabled mod: X{ini_name} -> {os.path.basename(ini_path)}")
        else:
            print(f"Enable operation skipped: .Xini file not found for {ini_name}")
    else:
        # Disable the mod by renaming it to .Xini
        if os.path.exists(ini_path):
            os.rename(ini_path, xini_path)
            print(f"Disabled mod: {ini_name} -> {os.path.basename(xini_path)}")
        else:
            print(f"Disable operation skipped: .ini file not found for {ini_name}")

def apply_enable_mapping(master_data, enable_mapping):
    """
    Apply the enable mapping to all mods in master.json.

    :param master_data: The loaded master.json data.
    :param enable_mapping: The enable mapping dict.
    """
    for mod_id, mod_data in master_data.items():
        mod_path = mod_data.get("path")
        ini_name = mod_data["data"].get("ini")
        enable = enable_mapping.get(mod_id, False)

        toggle_mod_ini(mod_path, ini_name, enable)


def restore_all_inis(master_data):
    """
    Restore all mods to .ini (enabled state) by renaming .Xini back to .ini.

    :param master_data: The loaded master.json data.
    """
    for mod_id, mod_data in master_data.items():
        mod_path = mod_data.get("path")
        ini_name = mod_data["data"].get("ini")

        toggle_mod_ini(mod_path, ini_name, True)  # Always enable
