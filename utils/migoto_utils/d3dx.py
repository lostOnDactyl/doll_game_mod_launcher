# TODO: update to handle analyse options false as comment instead of deleting

import configparser
import json
import os
import re


class D3DXIniHandler:
    def __init__(self, ini_path=None, json_path=None):
        self.ini_path = ini_path
        self.json_path = json_path

    def parse_ini_to_json(self, output_json_path=None):
        """Parses an INI file into JSON format."""
        if not self.ini_path:
            raise ValueError("INI file path is not set.")
        
        config = configparser.ConfigParser(allow_no_value=True, delimiters=('=', ':'))
        config.optionxform = str  # Preserve case sensitivity
        
        with open(self.ini_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_section = None
        ini_data = {}
        keybind_pattern = re.compile(r"(VK_|no_modifiers|Key|ctrl|alt|shift|F\d+)", re.IGNORECASE)
        section_lines = []

        for line in lines:
            stripped_line = line.strip()
            
            # Ignore comments and empty lines
            if stripped_line.startswith(";") or not stripped_line:
                continue
            
            # Detect sections
            if stripped_line.startswith("[") and stripped_line.endswith("]"):
                # Save the previous section if any
                if current_section:
                    if section_lines:
                        ini_data[current_section] = self._parse_section(section_lines, keybind_pattern)
                    section_lines = []
                current_section = stripped_line.strip("[]")
            elif current_section:
                section_lines.append(stripped_line)
        
        # Save the last section
        if current_section and section_lines:
            ini_data[current_section] = self._parse_section(section_lines, keybind_pattern)
        
        json_output = json.dumps(ini_data, indent=4)
        if output_json_path:
            with open(output_json_path, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"JSON output written to {output_json_path}")
        return json_output

    def recompile_ini(self, template_ini_path, output_dir="./render", settings=None):
        """Recompiles JSON data into an INI file."""
        if not self.json_path:
            raise ValueError("JSON file path is not set.")
        
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "d3dx.ini")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        with open(template_ini_path, 'r', encoding='utf-8') as f:
            template_lines = f.readlines()
        
        output_lines = []
        current_section = None
        section_buffer = []
        processed_sections = set()

        def flush_section():
            """Write buffered section data to output."""
            if current_section:
                output_lines.append(f"[{current_section}]\n")
                if current_section in config_data:
                    section_data = config_data[current_section]
                    
                    # Special handling for analyse_options
                    if "analyse_options" in section_data:
                        analyse_options_value = section_data["analyse_options"]
                        if isinstance(analyse_options_value, str):
                            if settings and settings["3dmigoto"].get("analyse_options", False):
                                output_lines.append(f"analyse_options = {analyse_options_value}\n")
                            else:
                                output_lines.append(f"; analyse_options = {analyse_options_value}\n")
                        else:
                            output_lines.append(f"; analyse_options = \n")
                    
                    # Handle directive blocks
                    if "_directives" in section_data and len(section_data["_directives"]) >= 2:
                        directives = section_data["_directives"]
                        # Write opening directive
                        output_lines.append(f"{directives[0]}\n")
                        for key, value in section_data.items():
                            if key in ("_directives", "_keybinds", "analyse_options"):
                                continue
                            if isinstance(value, list):  # Handle repeated keys
                                for v in value:
                                    output_lines.append(f"\t{key} = {v}\n")
                            else:
                                output_lines.append(f"\t{key} = {value}\n")
                        # Write closing directive
                        output_lines.append(f"{directives[-1]}\n")
                    else:
                        # Write non-directive entries as-is
                        for key, value in section_data.items():
                            if key in ("_directives", "_keybinds", "analyse_options"):
                                continue
                            if isinstance(value, list):
                                for v in value:
                                    output_lines.append(f"{key} = {v}\n")
                            else:
                                output_lines.append(f"{key} = {value}\n")
                    
                    # Write keybinds at the end
                    if "_keybinds" in section_data:
                        for key, value in section_data["_keybinds"].items():
                            output_lines.append(f"{key} = {value}\n")
                    
                    processed_sections.add(current_section)
                else:
                    # Write original section content if not overridden
                    output_lines.extend(section_buffer)
                output_lines.append("\n")
            section_buffer.clear()

        for line in template_lines:
            stripped_line = line.strip()

            # Preserve comments and empty lines
            if stripped_line.startswith(";") or not stripped_line:
                output_lines.append(line)
                continue
            
            # Detect sections
            if stripped_line.startswith("[") and stripped_line.endswith("]"):
                flush_section()
                current_section = stripped_line.strip("[]")
                section_buffer = []
                continue
            
            if current_section:
                section_buffer.append(line)
        
        # Flush the last section
        flush_section()

        # Add remaining JSON sections not in the template
        for section, section_data in config_data.items():
            if section not in processed_sections:
                output_lines.append(f"[{section}]\n")
                if "_directives" in section_data and len(section_data["_directives"]) >= 2:
                    directives = section_data["_directives"]
                    output_lines.append(f"{directives[0]}\n")
                    for key, value in section_data.items():
                        if key in ("_directives", "_keybinds", "analyse_options"):
                            continue
                        if isinstance(value, list):
                            for v in value:
                                output_lines.append(f"\t{key} = {v}\n")
                        else:
                            output_lines.append(f"{key} = {value}\n")
                    output_lines.append(f"{directives[-1]}\n")
                else:
                    for key, value in section_data.items():
                        if key in ("_directives", "_keybinds", "analyse_options"):
                            continue
                        if isinstance(value, list):
                            for v in value:
                                output_lines.append(f"{key} = {v}\n")
                        else:
                            output_lines.append(f"{key} = {value}\n")
                if "_keybinds" in section_data:
                    for key, value in section_data["_keybinds"].items():
                        output_lines.append(f"{key} = {value}\n")
                output_lines.append("\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        print(f"Updated INI file written to {output_path}")




    @staticmethod
    def _parse_section(lines, keybind_pattern):
        """Parse the lines of a section."""
        section_data = {"_keybinds": {}}
        key_value_pairs = []
        directives = []
        for line in lines:
            if "=" in line:
                key, value = map(str.strip, line.split("=", 1))
                if keybind_pattern.search(key) or keybind_pattern.search(value):
                    section_data["_keybinds"][key] = value
                else:
                    key_value_pairs.append((key, value))
            else:
                directives.append(line.strip())
        
        key_data = {}
        for key, value in key_value_pairs:
            if key in key_data:
                if isinstance(key_data[key], list):
                    key_data[key].append(value)
                else:
                    key_data[key] = [key_data[key], value]
            else:
                key_data[key] = value

        if directives:
            section_data["_directives"] = directives
        section_data.update(key_data)
        
        if not section_data["_keybinds"]:
            del section_data["_keybinds"]
        
        return section_data
