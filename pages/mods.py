# Ive given up on this file i need to rewrite it ground up
# Absolute monstrosity and shit
# TODO -> MAKE MOD DISPLAY LESS SHIT (and add localizations)
# TODO 2 -> search
# TODO 3 -> thumbnails.. maybe..

from PySide6.QtWidgets import (
    QVBoxLayout, QPushButton, QScrollArea, QWidget, QLabel, QFrame, QGridLayout, QHBoxLayout, QCheckBox
)
from PySide6.QtCore import Qt
import os
import importlib.util
from utils.file_utils import load_json
from utils.settings import load_enable_mapping, save_enable_mapping
from utils.ui_helpers import create_mod_row, create_mod_details
from utils.xini import toggle_mod_ini
from .base import EnhancedBasePage

MASTER_JSON = "./config/mods/master.json"
ENABLE_MAPPING_FILE = "./config/mods/enabled_mods.json"
CHARACTERS_JSON = "./config/characters/characters.json"
SORT_METHODS_DIR = "./config/mods/sort_methods"

class ModsPage(EnhancedBasePage):
    def __init__(self, localization, settings, save_settings_callback):
        super().__init__(localization, settings, save_settings_callback)
        self.layout = QVBoxLayout(self)

        # State
        self.current_sort_method = None
        self.available_sort_methods = []
        self.sorted_mods = []
        self.enable_mapping = {}

        # Sorting and Reload Controls
        self.create_controls()

        # Scrollable Mods Display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

        # Initial Load
        self.load_sort_methods()
        self.refresh_mods()

    def create_controls(self):
        """Create sorting and reload controls."""
        controls_layout = QHBoxLayout()

        # Sorting Method Selector
        self.sorting_method_button = QPushButton(
            self.localization.get("mods.sorting_method", "Sort: Default")
        )
        self.sorting_method_button.clicked.connect(self.toggle_sorting_method)
        controls_layout.addWidget(self.sorting_method_button)

        # Reload Button
        self.reload_button = QPushButton(
            self.localization.get("mods.reload_button", "Reload Mods")
        )
        self.reload_button.clicked.connect(self.refresh_mods)
        controls_layout.addWidget(self.reload_button)

        self.layout.addLayout(controls_layout)

    def update_ui(self):
        """Update UI elements dynamically based on current state."""
        if self.current_sort_method:
            sort_label = os.path.basename(self.current_sort_method).replace(".py", "").capitalize()
        else:
            sort_label = "Default"
        self.sorting_method_button.setText(
            self.localization.get("mods.sorting_method", f"Sort: {sort_label}")
        )
        self.reload_button.setText(self.localization.get("mods.reload_button", "Reload Mods"))

    def load_sort_methods(self):
        """Load sorting methods dynamically from files."""
        try:
            self.available_sort_methods = [
                os.path.join(SORT_METHODS_DIR, f) for f in os.listdir(SORT_METHODS_DIR)
                if f.endswith(".py") and not f.startswith("__")
            ]
            if self.available_sort_methods:
                self.current_sort_method = self.available_sort_methods[0]
                self.update_ui()
            else:
                self.display_error(self.localization.get("mods.no_sort_methods", "No sorting methods available."))
        except Exception as e:
            print(f"Error loading sorting methods: {e}")

    def refresh_mods(self):
        """Refresh mods and display the sorted list."""
        master_data = load_json(MASTER_JSON)
        characters_data = load_json(CHARACTERS_JSON)

        if not master_data or not characters_data:
            self.display_error(self.localization.get("mods.error_loading", "Error loading mod or character data."))
            return

        self.enable_mapping = load_enable_mapping()

        try:
            valid_characters = set(characters_data.get("survivors", []) + characters_data.get("hunters", []))
            if self.current_sort_method:
                spec = importlib.util.spec_from_file_location("sort_method", self.current_sort_method)
                sort_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(sort_module)

                sorted_mods = sort_module.sort_mods(master_data, valid_characters)
                if not isinstance(sorted_mods, dict):
                    raise ValueError("Expected sort_mods to return a dictionary.")
                self.sorted_mods = sorted_mods
            else:
                self.sorted_mods = {
                    "character_mods": [],
                    "object_mods": [],
                    "non_skinmods": list(master_data.values()),
                }
        except Exception as e:
            print(f"Error applying sort method: {e}")
            self.display_error(self.localization.get("mods.error_sorting", "Error sorting mods."))
            return

        self.display_mods()

    def display_mods(self):
        """Display mods in a categorized and user-friendly format."""
        # Clear existing content
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().deleteLater()

        # Add headers
        header = QFrame()
        header_layout = QGridLayout(header)
        header_layout.addWidget(QLabel(self.localization.get("mods.header_enable", "Enable")), 0, 0, alignment=Qt.AlignCenter)
        header_layout.addWidget(QLabel(self.localization.get("mods.header_name", "Name")), 0, 1)
        header_layout.addWidget(QLabel(self.localization.get("mods.header_type", "Type")), 0, 2)
        header_layout.addWidget(QLabel(self.localization.get("mods.header_version", "Version")), 0, 3)
        self.content_layout.addWidget(header)

        for category, mods in self.sorted_mods.items():
            category_label = QLabel(self.localization.get(f"mods.category_{category}", category.replace("_", " ").capitalize()))
            category_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            self.content_layout.addWidget(category_label)

            for mod in mods:
                self.add_mod_row(mod)

    def toggle_mod_state(self, mod_id, state):
        """Enable or disable a mod based on checkbox state."""
        master_data = load_json(MASTER_JSON)
        mod_data = master_data.get(mod_id)

        if not mod_data:
            print(f"Warning: Mod {mod_id} not found in master.json.")
            return

        # Normalize the directory path from mod.json
        mod_path = os.path.normpath(os.path.dirname(mod_data.get("path", "")))
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
            print(f"Enabled mod: {mod_id}")
        elif state == 0:  # Disable
            toggle_mod_ini(mod_path, ini_name, False)
            self.enable_mapping[mod_id] = False
            print(f"Disabled mod: {mod_id}")
        else:
            print(f"Unknown state for mod {mod_id}: {state}")

        # Persist the updated enable mapping
        save_enable_mapping(self.enable_mapping)

    def add_mod_row(self, mod):
        """Add a row for a single mod."""
        if not isinstance(mod, dict):
            print(f"Invalid mod data: {mod}")
            return

        row_layout = QGridLayout()

        # Enable Checkbox
        enable_checkbox = QCheckBox()
        enable_checkbox.setChecked(self.enable_mapping.get(mod.get("id", ""), False))
        enable_checkbox.stateChanged.connect(lambda state, mod_id=mod.get("id", ""): self.toggle_mod_state(mod_id, state))
        row_layout.addWidget(enable_checkbox, 0, 0, alignment=Qt.AlignCenter)

        # Mod Name
        name_label = QLabel(mod["data"].get("id", "Unknown ID"))
        row_layout.addWidget(name_label, 0, 1)

        # Mod Type
        type_label = QLabel(mod.get("type", "N/A"))
        row_layout.addWidget(type_label, 0, 2)

        # Mod Version
        version_label = QLabel(mod["data"].get("version", "N/A"))
        row_layout.addWidget(version_label, 0, 3)

        expand_button = QPushButton(self.localization.get("mods.expand", "Expand"))
        row_layout.addWidget(expand_button, 0, 4)

        row_widget = QWidget()
        row_widget.setLayout(row_layout)
        self.content_layout.addWidget(row_widget)

        details = create_mod_details(mod)
        details.setVisible(False)
        self.content_layout.addWidget(details)

        expand_button.clicked.connect(lambda: self.toggle_expand(details))

    def toggle_expand(self, details_widget):
        """Toggle the visibility of mod details."""
        details_widget.setVisible(not details_widget.isVisible())

    def toggle_sorting_method(self):
        """Cycle through sorting methods."""
        if not self.available_sort_methods:
            self.display_error(self.localization.get("mods.no_sort_methods", "No sorting methods available."))
            return

        current_index = self.available_sort_methods.index(self.current_sort_method)
        self.current_sort_method = self.available_sort_methods[(current_index + 1) % len(self.available_sort_methods)]
        self.update_ui()
        self.refresh_mods()

    def display_error(self, message):
        """Display an error message."""
        error_label = QLabel(message)
        error_label.setStyleSheet("color: red; font-weight: bold;")
        self.content_layout.addWidget(error_label)
