import sys
import os
import importlib
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QToolBar, QWidget
from PySide6.QtCore import Qt
from localization import Localization
from utils.load_mods.DIRECTORY import load_directory
from utils.file_utils import load_json
from utils.xini import toggle_mod_ini
from utils.settings import load_settings, save_settings, load_enable_mapping, save_enable_mapping

# Factories
def create_nav_button(name, callback, localization):
    """Create a navigation button with localized text."""
    localized_name = localization.get(f"nav.{name.lower()}", name)
    button = QPushButton(localized_name)
    button.clicked.connect(callback)
    return button

def create_toolbar_button(name, callback, localization):
    """Create a toolbar button with localized text."""
    localized_name = localization.get(f"nav.{name.lower()}", name)
    button = QPushButton(localized_name)
    button.clicked.connect(callback)
    return button

# Main Class
class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Launcher")
        self.resize(800, 600)

        # Load settings and localization
        self.settings = load_settings()
        self.localization = Localization(self.settings["general"].get("localization", "en"))

        self.toolbar = QToolBar(self.localization.get("nav.toolbar", "Main Toolbar"))
        toolbar_position = Qt.ToolBarArea(self.settings["user_preferences"]["toolbar_position"])
        self.addToolBar(toolbar_position, self.toolbar)
        self.reload_button = create_toolbar_button("reload_all", self.reload_launcher, self.localization)
        self.toolbar.addWidget(self.reload_button)
        self.restore_button = create_toolbar_button("restore_all", self.restore_all_mods, self.localization)
        self.toolbar.addWidget(self.restore_button)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.nav_bar = QHBoxLayout()
        self.layout.addLayout(self.nav_bar)
        self.pages = QStackedWidget()
        self.page_map = self.load_pages()
        self.layout.addWidget(self.pages)

        self.nav_buttons = {}
        for page_name in self.page_map.keys():
            button = create_nav_button(page_name, lambda _, name=page_name: self.switch_page(name), self.localization)
            self.nav_bar.addWidget(button)
            self.nav_buttons[page_name] = button

        self.switch_page("Home")

        # Mod enable/disable mapping
        self.enable_mapping = load_enable_mapping()
        self.aggregate_mods()
        self.apply_mod_states()

    def closeEvent(self, event):
        """Handle application close, save settings, and restore all mods."""
        self.settings["user_preferences"]["toolbar_position"] = self.toolBarArea(self.toolbar).value
        save_settings(self.settings)

        try:
            self.restore_all_mods()
            print("All mods restored successfully.")
        except Exception as e:
            print(f"Error restoring mods during application close: {e}")

        event.accept()

    def load_pages(self):
        """Dynamically load pages from the `pages` directory."""
        page_map = {}
        pages_dir = "pages"
        for file in os.listdir(pages_dir):
            if file.endswith(".py") and file not in ["__init__.py", "base.py"]:
                module_name = f"pages.{file[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    page_class_name = file[:-3].capitalize() + "Page"
                    if hasattr(module, page_class_name):
                        page_class = getattr(module, page_class_name)
                        instance = page_class(self.localization, self.settings, save_settings)
                        page_map[file[:-3].capitalize()] = instance
                        self.pages.addWidget(instance)
                except Exception as e:
                    print(f"Failed to load page {file}: {e}")
        return page_map

    def switch_page(self, page_name):
        """Switch pages based on navigation."""
        if page_name in self.page_map:
            index = list(self.page_map.keys()).index(page_name)
            self.pages.setCurrentIndex(index)

    def aggregate_mods(self):
        """Run the mod aggregation process."""
        mod_directory = self.settings["paths"]["migoto_mod_folder"]
        config_mods_dir = os.path.join(os.path.dirname(__file__), "config", "mods")
        master_file = os.path.join(config_mods_dir, "master.json")

        try:
            os.makedirs(config_mods_dir, exist_ok=True)
            load_directory(mod_directory, master_file)
            print(f"Mod aggregation completed. Master file created at {master_file}.")
        except Exception as e:
            print(f"Error during mod aggregation: {e}")

    def apply_mod_states(self):
        """Apply the enable/disable states to mods based on enable_mapping."""
        master_data = load_json("./config/mods/master.json")
        for mod_id, enabled in self.enable_mapping.items():
            mod_data = master_data.get(mod_id)
            if not mod_data:
                print(f"Warning: Mod {mod_id} not found in master.json.")
                continue

            mod_path = os.path.normpath(os.path.dirname(mod_data["path"]))
            ini_name = mod_data["data"].get("ini")

            if not ini_name:
                print(f"Warning: Mod {mod_id} does not specify an ini file.")
                continue

            if not os.path.isdir(mod_path):
                print(f"Error: Mod path does not exist or is not a directory: {mod_path}")
                continue

            toggle_mod_ini(mod_path, ini_name, enabled)

    def restore_all_mods(self):
        """Restore all mods in the Mods directory."""
        mods_dir = self.settings["paths"].get("migoto_mod_folder", "")
        if not os.path.isdir(mods_dir):
            print(self.localization.get("nav.error_mod_directory", f"Error: Mods directory does not exist: {mods_dir}").format(directory=mods_dir))
            return

        for root, _, files in os.walk(mods_dir):
            for file in files:
                if file.endswith(".Xini"):
                    original_path = os.path.join(root, file)
                    new_path = os.path.join(root, file.replace(".Xini", ".ini"))
                    try:
                        os.rename(original_path, new_path)
                        print(f"Restored mod: {original_path} -> {new_path}")
                    except Exception as e:
                        print(f"Error restoring mod {original_path}: {e}")

    def reload_toolbar(self):
        """Reload toolbar buttons with updated localization."""
        self.reload_button.setText(self.localization.get("nav.reload_all", "Reload"))
        self.restore_button.setText(self.localization.get("nav.restore_all", "Restore"))

    def reload_navigation(self):
        """Reload navigation buttons with updated localization."""
        for page_name, button in self.nav_buttons.items():
            localized_name = self.localization.get(f"nav.{page_name.lower()}", page_name)
            button.setText(localized_name)

    def reload_launcher(self):
        """Reload the launcher settings, localization, and mods."""
        self.settings = load_settings()
        self.localization.reload_language(self.settings["general"].get("localization", "en"))

        self.reload_toolbar()
        self.reload_navigation()

        # Re-aggregate mods and apply states
        self.aggregate_mods()
        self.apply_mod_states()

        # Reload pages
        for page in self.page_map.values():
            page.reload(self.localization, self.settings)

        print("Launcher settings, localization, and mods reloaded.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec())
