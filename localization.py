import json
import os

class Localization:
    def __init__(self, language="en"):
        self.language = language
        self.assets_dir = os.path.join("assets", "locales") 
        self.translations = self.load_language(language)

    def load_language(self, language):
        """Load localization file for the given language."""
        file_path = os.path.join(self.assets_dir, f"{language}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for {language}: {e}")
        print(f"Language '{language}' not found in '{self.assets_dir}'. Falling back to default.")
        return {}

    def reload_language(self, language):
        """Reload the translations for a new language."""
        self.language = language
        self.translations = self.load_language(language)

    def get(self, key, default=None):
        """Retrieve a translation by key, supporting dot notation for nested keys."""
        keys = key.split(".")
        value = self.translations
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default or key
        return value

    @property
    def available_locales(self):
        """List available localization files in the assets/locales directory."""
        if not os.path.exists(self.assets_dir):
            print(f"Locales directory '{self.assets_dir}' not found.")
            return []
        return [os.path.splitext(f)[0] for f in os.listdir(self.assets_dir) if f.endswith(".json")]
