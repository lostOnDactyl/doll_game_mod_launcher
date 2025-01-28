import json
import os
import importlib.util
from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog,
    QTabWidget, QWidget, QScrollArea, QGroupBox, QCheckBox, QTextEdit
)
from PySide6.QtGui import QDoubleValidator
from utils.ui_helpers import create_browse_row
from utils.migoto_utils.d3dx import D3DXIniHandler

class SettingsPage(QWidget):
    def __init__(self, localization, settings, save_settings_callback):
        super().__init__()
        self.localization = localization
        self.settings = settings
        self.save_settings_callback = save_settings_callback

        # Main layout for the page
        self.main_layout = QVBoxLayout(self)

        # Tab widget to hold tabs
        self.tab_widget = QTabWidget()

        # Add Launcher Settings tab
        self.launcher_settings_tab = LauncherSettingsTab(localization, settings, save_settings_callback)
        self.tab_widget.addTab(self.launcher_settings_tab, localization.get("settings.tab_launcher", "Launcher Settings"))

        # Add Other Settings (3DMigoto Settings) tab
        self.other_settings_tab = OtherSettingsTab(localization, settings, save_settings_callback)
        self.tab_widget.addTab(self.other_settings_tab, localization.get("settings.tab_other", "3DMigoto Settings"))

        # Add Dump Settings tab
        self.dump_settings_tab = DumpSettingsTab(localization, settings, save_settings_callback)
        self.tab_widget.addTab(self.dump_settings_tab, localization.get("settings.tab_dump", "Dump Settings"))

        # Add the tab widget to the main layout
        self.main_layout.addWidget(self.tab_widget)

    def reload(self, localization, settings):
        """Reload settings and localization for all tabs."""
        self.localization = localization
        self.settings = settings

        # Reload individual tabs
        self.launcher_settings_tab.reload(localization, settings)
        self.other_settings_tab.reload(localization, settings)
        self.dump_settings_tab.reload(localization, settings)

class LauncherSettingsTab(QWidget):
    def __init__(self, localization, settings, save_settings_callback):
        super().__init__()
        self.localization = localization
        self.settings = settings
        self.save_settings_callback = save_settings_callback
        self.layout = QVBoxLayout(self)
        self.create_layout()

    def create_layout(self):
        # Localization dropdown
        self.localization_label = QLabel(self.localization.get("settings.label_localization", "Localization"))
        self.localization_dropdown = QComboBox()
        self.localization_dropdown.addItems(self.localization.available_locales)
        self.localization_dropdown.setCurrentText(self.settings["general"].get("localization", "en"))
        self.localization_dropdown.currentIndexChanged.connect(self.update_localization)

        # Game executable
        self.game_exe_label = QLabel(self.localization.get("settings.label_game_executable", "Game Executable"))
        self.game_exe_input = QLineEdit(self.settings["paths"].get("game_executable", ""))
        self.game_exe_browse = QPushButton(self.localization.get("settings.button_browse", "Browse"))
        self.game_exe_browse.clicked.connect(self.browse_game_exe)

        # 3DMigoto executable
        self.migoto_exe_label = QLabel(self.localization.get("settings.label_migoto_executable", "3DMigoto Executable"))
        self.migoto_exe_input = QLineEdit(self.settings["paths"].get("migoto_executable", ""))
        self.migoto_exe_browse = QPushButton(self.localization.get("settings.button_browse", "Browse"))
        self.migoto_exe_browse.clicked.connect(self.browse_migoto_exe)

        # 3DMigoto mod folder
        self.migoto_mod_folder_label = QLabel(self.localization.get("settings.label_migoto_mod_folder", "3DMigoto Mod Folder"))
        self.migoto_mod_folder_input = QLineEdit(self.settings["paths"].get("migoto_mod_folder", ""))
        self.migoto_mod_folder_browse = QPushButton(self.localization.get("settings.button_browse", "Browse"))
        self.migoto_mod_folder_browse.clicked.connect(self.browse_mod_folder)

        # Log directory
        self.log_dir_label = QLabel(self.localization.get("settings.label_log_dir", "Log Directory"))
        self.log_dir_input = QLineEdit(self.settings["user_preferences"].get("log_dir", "logs"))
        self.log_dir_browse = QPushButton(self.localization.get("settings.button_browse", "Browse"))
        self.log_dir_browse.clicked.connect(self.browse_log_dir)

        # Style directory
        self.style_dir_label = QLabel(self.localization.get("settings.label_style_dir", "Style Directory"))
        self.style_dir_input = QLineEdit(self.settings["user_preferences"].get("style_dir", "styles"))
        self.style_dir_browse = QPushButton(self.localization.get("settings.button_browse", "Browse"))
        self.style_dir_browse.clicked.connect(self.browse_style_dir)

        # Stylesheet file
        self.stylesheet_label = QLabel(self.localization.get("settings.label_stylesheet", "Stylesheet"))
        self.stylesheet_input = QLineEdit(self.settings["user_preferences"].get("stylesheet", ""))
        self.stylesheet_browse = QPushButton(self.localization.get("settings.button_browse", "Browse"))
        self.stylesheet_browse.clicked.connect(self.browse_stylesheet)

        # Save button
        self.save_button = QPushButton(self.localization.get("settings.button_save", "Save"))
        self.save_button.clicked.connect(self.save_settings)

        # Layout organization
        form_layout = QFormLayout()
        form_layout.addRow(self.localization_label, self.localization_dropdown)
        form_layout.addRow(self.game_exe_label, create_browse_row(self.game_exe_input, self.game_exe_browse))
        form_layout.addRow(self.migoto_exe_label, create_browse_row(self.migoto_exe_input, self.migoto_exe_browse))
        form_layout.addRow(self.migoto_mod_folder_label, create_browse_row(self.migoto_mod_folder_input, self.migoto_mod_folder_browse))
        form_layout.addRow(self.log_dir_label, create_browse_row(self.log_dir_input, self.log_dir_browse))
        form_layout.addRow(self.style_dir_label, create_browse_row(self.style_dir_input, self.style_dir_browse))
        form_layout.addRow(self.stylesheet_label, create_browse_row(self.stylesheet_input, self.stylesheet_browse))

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.save_button)

    def browse_game_exe(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Game Executable")
        if file_path:
            self.game_exe_input.setText(file_path)

    def browse_migoto_exe(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select 3DMigoto Executable")
        if file_path:
            self.migoto_exe_input.setText(file_path)

    def browse_mod_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Mod Folder")
        if folder_path:
            self.migoto_mod_folder_input.setText(folder_path)

    def browse_log_dir(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Log Directory")
        if folder_path:
            self.log_dir_input.setText(folder_path)

    def browse_style_dir(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Style Directory")
        if folder_path:
            self.style_dir_input.setText(folder_path)

    def browse_stylesheet(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Stylesheet")
        if file_path:
            self.stylesheet_input.setText(file_path)

    def update_localization(self):
        selected_locale = self.localization_dropdown.currentText()
        self.settings["general"]["localization"] = selected_locale

    def save_settings(self):
        self.settings["paths"]["game_executable"] = self.game_exe_input.text()
        self.settings["paths"]["migoto_executable"] = self.migoto_exe_input.text()
        self.settings["paths"]["migoto_mod_folder"] = self.migoto_mod_folder_input.text()
        self.settings["user_preferences"]["log_dir"] = self.log_dir_input.text()
        self.settings["user_preferences"]["style_dir"] = self.style_dir_input.text()
        self.settings["user_preferences"]["stylesheet"] = self.stylesheet_input.text()
        self.save_settings_callback(self.settings)

    def reload(self, localization, settings):
        """Reload localization and settings for this tab."""
        self.localization = localization
        self.settings = settings

        # Update dropdown options and selection
        self.localization_dropdown.blockSignals(True)
        self.localization_dropdown.clear()
        self.localization_dropdown.addItems(self.localization.available_locales)
        self.localization_dropdown.setCurrentText(self.settings["general"].get("localization", "en"))
        self.localization_dropdown.blockSignals(False)

        # Update input fields
        self.game_exe_input.setText(self.settings["paths"].get("game_executable", ""))
        self.migoto_exe_input.setText(self.settings["paths"].get("migoto_executable", ""))
        self.migoto_mod_folder_input.setText(self.settings["paths"].get("migoto_mod_folder", ""))
        self.log_dir_input.setText(self.settings["user_preferences"].get("log_dir", "logs"))
        self.style_dir_input.setText(self.settings["user_preferences"].get("style_dir", "styles"))
        self.stylesheet_input.setText(self.settings["user_preferences"].get("stylesheet", ""))

        # Update labels with new localization
        self.localization_label.setText(self.localization.get("settings.label_localization", "Localization"))
        self.game_exe_label.setText(self.localization.get("settings.label_game_executable", "Game Executable"))
        self.migoto_exe_label.setText(self.localization.get("settings.label_migoto_executable", "3DMigoto Executable"))
        self.migoto_mod_folder_label.setText(self.localization.get("settings.label_migoto_mod_folder", "3DMigoto Mod Folder"))
        self.log_dir_label.setText(self.localization.get("settings.label_log_dir", "Log Directory"))
        self.style_dir_label.setText(self.localization.get("settings.label_style_dir", "Style Directory"))
        self.stylesheet_label.setText(self.localization.get("settings.label_stylesheet", "Stylesheet"))
        self.save_button.setText(self.localization.get("settings.button_save", "Save"))


class OtherSettingsTab(QWidget):
    def __init__(self, localization, settings, save_settings_callback):
        super().__init__()
        self.localization = localization
        self.settings = settings
        self.save_settings_callback = save_settings_callback
        self.layout = QVBoxLayout(self)
        self.settings_path = "config/3dmigoto.json"
        self.d3dx_ini_path = self._get_d3dx_ini_path()
        self.settings_data = self.load_settings()
        self.create_layout()

    def _get_d3dx_ini_path(self, folder=False):
        """Derive the d3dx.ini path based on the migoto executable path."""
        migoto_exe = self.settings["paths"].get("migoto_executable", "")
        if folder:
            return "/".join(migoto_exe.split("/")[:-1])
        else:
            return "/".join(migoto_exe.split("/")[:-1]) + "/d3dx.ini"

    def load_settings(self):
        """Load settings from the 3dmigoto.json file."""
        try:
            with open(self.settings_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_settings_to_json(self):
        """Save updated settings to the 3dmigoto.json file."""
        with open(self.settings_path, "w") as file:
            json.dump(self.settings_data, file, indent=4)

    def save_settings_to_ini(self):
        """Save settings to d3dx.ini using D3DXIniHandler."""
        handler = D3DXIniHandler(json_path=self.settings_path)
        handler.recompile_ini(
            template_ini_path=self.d3dx_ini_path,
            output_dir=self._get_d3dx_ini_path(folder=True),
            settings=self.settings  # Pass settings to handler
        )


    def create_layout(self):
        """Create a scrollable form layout for dynamically rendering settings."""
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        main_layout = QVBoxLayout(container)

        for category, settings in self.settings_data.items():
            # Group for each category
            category_group = QGroupBox(f"{category}")
            category_layout = QFormLayout(category_group)

            for key, value in settings.items():
                if key == "analyse_options":
                    # Special handling for analyse_options
                    enabled = self.settings["3dmigoto"].get("analyse_options", False)
                    analyse_checkbox = QCheckBox(self.localization.get("settings.enable_analyse", "Enable Analyse Options"))
                    analyse_checkbox.setChecked(enabled)
                    analyse_input = QLineEdit(value if enabled else "")
                    analyse_input.setEnabled(enabled)

                    analyse_checkbox.toggled.connect(
                        lambda checked, input_field=analyse_input: self.toggle_analyse_options(checked, input_field)
                    )
                    analyse_input.textChanged.connect(
                        lambda text, cat=category, k=key: self.update_setting(cat, k, text)
                    )

                    category_layout.addRow(analyse_checkbox, analyse_input)
                elif key == "_keybinds" and isinstance(value, dict):
                    # Collapsible group for keybinds
                    keybind_group = QGroupBox(self.localization.get("settings.keybinds", "Keybinds"))
                    keybind_group.setCheckable(True)
                    keybind_group.setChecked(False)
                    keybind_layout = QFormLayout()
                    keybind_group.setLayout(keybind_layout)

                    # Populate keybinds
                    for keybind_name, keybind_value in value.items():
                        label = QLabel(keybind_name)
                        input_field = QLineEdit(keybind_value)
                        input_field.setVisible(False)
                        label.setVisible(False)
                        input_field.textChanged.connect(
                            lambda val, cat=category, k=keybind_name: self.update_keybind(cat, k, val)
                        )
                        keybind_layout.addRow(label, input_field)

                        keybind_group.toggled.connect(
                            lambda checked, l=label, f=input_field: self.toggle_keybind_visibility(checked, l, f)
                        )

                    category_layout.addRow(keybind_group)
                else:
                    # Standard field
                    label = QLabel(key)
                    if isinstance(value, str):
                        input_field = QLineEdit(value)
                        input_field.textChanged.connect(
                            lambda val, cat=category, k=key: self.update_setting(cat, k, val)
                        )
                        category_layout.addRow(label, input_field)

            category_group.setLayout(category_layout)
            main_layout.addWidget(category_group)

        save_button = QPushButton(self.localization.get("settings.button_save", "Save"))
        save_button.clicked.connect(self.save_settings)
        main_layout.addWidget(save_button)

        container.setLayout(main_layout)
        scroll_area.setWidget(container)
        self.layout.addWidget(scroll_area)

    def toggle_analyse_options(self, enabled, input_field):
        """Enable or disable the analyse_options field and sync with settings."""
        input_field.setEnabled(enabled)
        if not enabled:
            input_field.setText("")  # Clear value if disabled
        self.settings["3dmigoto"]["analyse_options"] = enabled
        self.save_settings_callback(self.settings)

    def update_setting(self, category, key, value):
        """Update settings_data when a standard field is modified."""
        self.settings_data[category][key] = value

    def toggle_keybind_visibility(self, checked, label, input_field):
        """Toggle the visibility of a keybind label and input field."""
        label.setVisible(checked)
        input_field.setVisible(checked)

    def update_keybind(self, category, key, value):
        """Update keybinds in the settings data."""
        if "_keybinds" in self.settings_data[category]:
            self.settings_data[category]["_keybinds"][key] = value

    def update_setting(self, category, key, value):
        """Update settings_data when a standard field is modified."""
        self.settings_data[category][key] = value

    def save_settings(self):
        """Save both JSON and INI settings."""
        self.save_settings_to_json()
        self.save_settings_to_ini()
        print("Settings saved successfully.")

    def reload(self, localization, settings):
        """Reload settings and update UI."""
        self.localization = localization
        self.settings = settings

        # Update paths
        self.d3dx_ini_path = self._get_d3dx_ini_path()
        self.settings_path = "config/3dmigoto.json"

        # Recreate 3dmigoto.json if d3dx.ini exists
        if os.path.exists(self.d3dx_ini_path):
            handler = D3DXIniHandler(ini_path=self.d3dx_ini_path)
            handler.parse_ini_to_json(output_json_path=self.settings_path)

        # Reload settings data
        self.settings_data = self.load_settings()

        # Clear and recreate the layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.create_layout()

# TODO: probably rework this into a general ini quickwriter util
# TODO: fix reload -- language doesnt reload on this subtab, works on restart tho

class DumpSettingsTab(QWidget):
    def __init__(self, localization, settings, save_settings_callback):
        super().__init__()
        self.localization = localization
        self.settings = settings
        self.save_settings_callback = save_settings_callback

        # Main layout for the Dump tab
        self.main_layout = QVBoxLayout(self)
        self.script_folder = "./scripts"
        self.current_script = None
        self.script_inputs = {}

        self.dump_ini_path = os.path.join(settings["paths"]["migoto_mod_folder"], "dump.ini")

        self.create_layout()

    def load_scripts(self):
        """Load available scripts from the script folder."""
        scripts = {}
        for filename in os.listdir(self.script_folder):
            if filename.endswith(".py"):
                script_path = os.path.join(self.script_folder, filename)
                spec = importlib.util.spec_from_file_location("DumpScript", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                scripts[filename] = module.DumpScript
        return scripts

    def create_layout(self):
        """Create the UI layout for the Dump tab."""
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)

        # Dropdown for script selection
        self.script_dropdown = QComboBox()
        self.scripts = self.load_scripts()
        self.script_dropdown.addItems(self.scripts.keys())
        self.script_dropdown.currentIndexChanged.connect(self.load_script_inputs)
        layout.addWidget(QLabel(self.localization.get("dump.select_script", "Select Script:")))
        layout.addWidget(self.script_dropdown)

        self.input_form = QFormLayout()
        layout.addLayout(self.input_form)

        # Generated INI preview
        self.ini_preview = QTextEdit()
        self.ini_preview.setReadOnly(True)
        layout.addWidget(QLabel(self.localization.get("dump.ini_preview", "Generated INI Preview:")))
        layout.addWidget(self.ini_preview)

        self.save_mode_dropdown = QComboBox()
        self.save_mode_dropdown.addItems([self.localization.get("dump.override", "Override"), self.localization.get("dump.append", "Append")])
        layout.addWidget(QLabel(self.localization.get("dump.save_mode", "Save Mode:")))
        layout.addWidget(self.save_mode_dropdown)

        self.generate_button = QPushButton(self.localization.get("dump.generate", "Generate INI"))
        self.generate_button.clicked.connect(self.generate_ini)
        layout.addWidget(self.generate_button)

        self.save_button = QPushButton(self.localization.get("dump.save", "Send to dump.ini"))
        self.save_button.clicked.connect(self.save_ini)
        layout.addWidget(self.save_button)

        container.setLayout(layout)
        scroll_area.setWidget(container)
        self.main_layout.addWidget(scroll_area)

        self.load_script_inputs()

    def load_script_inputs(self):
        """Load input fields for the selected script."""
        for i in reversed(range(self.input_form.rowCount())):
            self.input_form.removeRow(i)

        script_name = self.script_dropdown.currentText()
        self.current_script = self.scripts[script_name]

        self.script_inputs = {}
        for input_def in self.current_script.get_inputs():
            label = QLabel(input_def["label"])
            if input_def["type"] == "dropdown":
                input_field = QComboBox()
                input_field.addItems(input_def.get("options", []))
            elif input_def["type"] == "string":
                input_field = QLineEdit()
            elif input_def["type"] == "multiline":
                input_field = QTextEdit()
            elif input_def["type"] == "bool":
                input_field = QCheckBox()
            elif input_def["type"] == "number":
                input_field = QLineEdit()
                input_field.setValidator(QDoubleValidator())
            else:
                continue 

            self.script_inputs[input_def["name"]] = input_field
            self.input_form.addRow(label, input_field)

    def get_user_inputs(self):
        """Retrieve user inputs from the UI."""
        inputs = {}
        for name, widget in self.script_inputs.items():
            if isinstance(widget, QLineEdit):
                inputs[name] = widget.text()
            elif isinstance(widget, QTextEdit):
                inputs[name] = widget.toPlainText()
            elif isinstance(widget, QComboBox):
                inputs[name] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                inputs[name] = widget.isChecked()
        return inputs

    def generate_ini(self):
        """Generate the INI content based on user inputs and the selected script."""
        if self.current_script is None:
            return

        inputs = self.get_user_inputs()
        ini_content = self.current_script.generate_ini(inputs)
        self.ini_preview.setPlainText(ini_content)

    def save_ini(self):
        """Save the generated INI content to dump.ini."""
        ini_content = self.ini_preview.toPlainText()
        mode = self.save_mode_dropdown.currentText()

        if mode == "Override":
            with open(self.dump_ini_path, "w", encoding="utf-8") as f:
                f.write(ini_content)
        elif mode == "Append":
            with open(self.dump_ini_path, "a", encoding="utf-8") as f:
                f.write("\n" + ini_content)

        print(f"dump.ini updated in {mode} mode: {self.dump_ini_path}")

    def reload(self, localization, settings):
        """Reload the settings and update the UI."""
        self.localization = localization
        self.settings = settings
        self.dump_ini_path = os.path.join(settings["paths"]["migoto_mod_folder"], "dump.ini")

        self.scripts = self.load_scripts()
        self.script_dropdown.blockSignals(True)
        self.script_dropdown.clear()
        self.script_dropdown.addItems(self.scripts.keys())
        self.script_dropdown.blockSignals(False)

        self.load_script_inputs()

        self.script_dropdown.setCurrentIndex(0)
        self.ini_preview.clear()
        