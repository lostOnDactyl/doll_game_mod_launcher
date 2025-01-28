import re

class DumpScript:
    @staticmethod
    def get_inputs():
        """
        Define the inputs required for this script. Each input should have:
        - name: The unique key for the input.
        - label: The label for the UI.
        - type: The input type (dropdown, string, multiline, bool, number).
        - options: Optional list of options for dropdowns.
        """
        return [
            {"name": "shader_override", "label": "Shader Override", "type": "bool"},
            {"name": "analyse_options", "label": "Analyse Options", "type": "string"},
            {"name": "entries", "label": "Hashes - seperate by comma, \n newline, or space", "type": "multiline"},
        ]

    @staticmethod
    def generate_ini(inputs):
        """
        Generate the content of the dump.ini file based on the user's inputs.
        Args:
            inputs (dict): A dictionary containing user inputs.
        Returns:
            str: The content of the dump.ini file.
        """
        # Extract user inputs
        shader_override = inputs.get("shader_override", False)
        analyse_options = inputs.get("analyse_options", "").strip()
        entries_raw = inputs.get("entries", "").strip()

        # Default analyse options if none provided
        default_analyse_options = "dump_rt dump_tex dump_cb dump_vb dump_ib deferred_ctx_accurate buf txt"
        analyse_options = analyse_options if analyse_options and analyse_options != "default" else default_analyse_options

        # Split multiline entries into a list
        entries = [entry.strip() for entry in re.split(r"[,\s]+", entries_raw) if entry.strip()]

        # Generate INI sections for each entry
        ini_sections = []
        for entry in entries:
            section_name = f"[{'ShaderOverride' if shader_override else 'TextureOverride'}{entry}]"
            ini_sections.append(section_name)
            ini_sections.append(f"hash = {entry}")
            ini_sections.append(f"analyse_options = {analyse_options}")
            ini_sections.append("")  # Blank line between sections

        # Combine into final INI content
        ini_content = ["; Generated dump.ini"]
        ini_content.extend(ini_sections)
        return "\n".join(ini_content)