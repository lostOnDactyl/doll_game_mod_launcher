# Ive given up on this file i need to rewrite it ground up
# Absolute monstrosity and shit
# TODO -> MAKE MOD DISPLAY LESS SHIT (and add localizations)
# TODO 2 -> search
# TODO 3 -> thumbnails.. maybe..

from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton, QScrollArea, QWidget, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
import os
from utils.file_utils import load_json
import importlib
from utils.settings import load_enable_mapping, save_enable_mapping
from utils.ui_helpers import create_mod_row, create_mod_details
from utils.xini import toggle_mod_ini
from .base import EnhancedBasePage

MASTER_JSON = "./config/mods/master.json"
ENABLE_MAPPING_FILE = "./config/mods/enabled_mods.json"
CHARACTERS_JSON = "./config/characters/characters.json"
SORT_METHODS_DIR = "config.mods.sort_methods"

class ModsPage(EnhancedBasePage):
    def __init__(self, localization, settings, save_settings_callback):
        super().__init__(localization, settings, save_settings_callback)
        self.layout = QVBoxLayout(self)

        # State
        self.current_sort_method = "method_one"
        self.sorted_mods = []
        self.enable_mapping = {}

        # Sorting Method Selector
        self.sorting_method_selector = QPushButton(self.localization.get("mods.sorting_method", "Sorting Method: Default"))
        self.sorting_method_selector.clicked.connect(self.toggle_sorting_method)
        self.layout.addWidget(self.sorting_method_selector)

        # Reload Button
        self.reload_button = QPushButton(self.localization.get("mods.reload_button", "Re-render Mods"))
        self.reload_button.clicked.connect(self.refresh_mods)
        self.layout.addWidget(self.reload_button)

        # Scrollable Area for Mods
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

        # Initial Refresh
        self.refresh_mods()

    def update_ui(self):
        """Update UI elements with the latest localization and settings."""
        self.sorting_method_selector.setText(
            self.localization.get("mods.sorting_method", f"Sorting Method: {self.current_sort_method.capitalize()}")
        )
        self.reload_button.setText(self.localization.get("mods.reload_button", "Re-render Mods"))

    def toggle_sorting_method(self):
        """Cycle through available sorting methods."""
        try:
            available_methods = [
                m[:-3] for m in os.listdir(SORT_METHODS_DIR)
                if m.endswith(".py") and not m.startswith("__")
            ]
            current_index = available_methods.index(self.current_sort_method)
            self.current_sort_method = available_methods[(current_index + 1) % len(available_methods)]
            self.update_ui()
            self.refresh_mods()
        except Exception as e:
            print(f"Error toggling sorting methods: {e}")

    def refresh_mods(self):
        """Refresh mods and display results."""
        master_data = load_json(MASTER_JSON)
        characters_data =load_json(CHARACTERS_JSON)

        if not master_data or not characters_data:
            self.display_error(self.localization.get("mods.error_loading_data", "Error loading mod or character data."))
            return

        self.enable_mapping = load_enable_mapping()

        try:
            valid_characters = set(characters_data.get("survivors", []) + characters_data.get("hunters", []))
            sort_module = importlib.import_module(f"{SORT_METHODS_DIR}.{self.current_sort_method}")
            self.sorted_mods = sort_module.sort_mods(master_data, valid_characters)
        except Exception as e:
            self.display_error(self.localization.get("mods.error_sorting", "Error applying sorting method."))
            print(f"Error loading sorting module: {e}")
            return

        self.display_mods()

    def display_mods(self):
        """Display mods in a table-like format."""
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().deleteLater()

        header = QFrame()
        header_layout = QGridLayout(header)
        header_layout.addWidget(QLabel(self.localization.get("mods.header_enable", "Enable")), 0, 0, alignment=Qt.AlignCenter)
        header_layout.addWidget(QLabel(self.localization.get("mods.header_name", "Name")), 0, 1)
        header_layout.addWidget(QLabel(self.localization.get("mods.header_type", "Type")), 0, 2)
        header_layout.addWidget(QLabel(self.localization.get("mods.header_version", "Version")), 0, 3)
        self.content_layout.addWidget(header)

        all_mods = (
            self.sorted_mods.get("character_mods", [])
            + self.sorted_mods.get("object_mods", [])
            + self.sorted_mods.get("non_skinmods", [])
        )

        for mod in all_mods:
            self.add_mod_row(mod)

    def add_mod_row(self, mod):
        """Add a mod row with a checkbox and expandable details."""
        row, expand_button = create_mod_row(
            mod,
            self.enable_mapping,
            self.toggle_mod_state,
            self.toggle_expand
        )
        self.content_layout.addWidget(row)

        details = create_mod_details(mod)
        self.content_layout.addWidget(details)

        expand_button.details_widget = details

    def toggle_mod_state(self, mod_id, state):
        """Update the enable mapping based on checkbox state."""
        master_data = load_json(MASTER_JSON)
        mod_data = master_data.get(mod_id)

        if not mod_data:
            print(f"Warning: Mod {mod_id} not found in master.json.")
            return

        # Normalize the directory path from mod.json
        mod_path = os.path.normpath(os.path.dirname(mod_data["path"]))
        ini_name = mod_data["data"].get("ini")

        if not ini_name:
            print(f"Warning: Mod {mod_id} does not specify an ini file.")
            return

        if not os.path.isdir(mod_path):
            print(f"Error: Mod path does not exist or is not a directory: {mod_path}")
            return

        # Enable or disable the mod
        if state == 2:  # Enable
            toggle_mod_ini(mod_path, ini_name, True)
            self.enable_mapping[mod_id] = True
            print(f"Updated enable state for {mod_id}: enabled")
        elif state == 0:  # Disable
            toggle_mod_ini(mod_path, ini_name, False)
            self.enable_mapping[mod_id] = False
            print(f"Updated enable state for {mod_id}: disabled")
        else:
            print(f"Unknown state for {mod_id}: {state}")

        # Persist the updated enable_mapping
        save_enable_mapping(self.enable_mapping)

    def toggle_expand(self, button):
        """Toggle the expansion of mod details."""
        details_widget = button.details_widget
        details_widget.setVisible(not details_widget.isVisible())

    def display_error(self, message):
        """Display an error message."""
        error_label = QLabel(message)
        error_label.setStyleSheet("color: red;")
        self.content_layout.addWidget(error_label)