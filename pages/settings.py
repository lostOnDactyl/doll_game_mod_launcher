from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QWidget
from utils.ui_helpers import create_browse_row
import os


class SettingsPage(QWidget):
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
        """Update localization when dropdown changes."""
        selected_locale = self.localization_dropdown.currentText()
        if selected_locale in self.localization.available_locales:
            self.localization.reload_language(selected_locale)
            self.settings["general"]["localization"] = selected_locale

    def save_settings(self):
        """Save the updated settings."""
        self.settings["paths"]["game_executable"] = self.game_exe_input.text()
        self.settings["paths"]["migoto_executable"] = self.migoto_exe_input.text()
        self.settings["paths"]["migoto_mod_folder"] = self.migoto_mod_folder_input.text()
        self.settings["user_preferences"]["log_dir"] = self.log_dir_input.text()
        self.settings["user_preferences"]["style_dir"] = self.style_dir_input.text()
        self.settings["user_preferences"]["stylesheet"] = self.stylesheet_input.text()
        self.settings["general"]["localization"] = self.localization_dropdown.currentText()
        self.save_settings_callback(self.settings)

    def reload(self, localization, settings):
        """Reload settings and localization dynamically."""
        self.localization = localization
        self.settings = settings

        # Reload UI elements
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

        # Update labels with localization
        self.localization_label.setText(self.localization.get("settings.label_localization", "Localization"))
        self.game_exe_label.setText(self.localization.get("settings.label_game_executable", "Game Executable"))
        self.migoto_exe_label.setText(self.localization.get("settings.label_migoto_executable", "3DMigoto Executable"))
        self.migoto_mod_folder_label.setText(self.localization.get("settings.label_migoto_mod_folder", "3DMigoto Mod Folder"))
        self.log_dir_label.setText(self.localization.get("settings.label_log_dir", "Log Directory"))
        self.style_dir_label.setText(self.localization.get("settings.label_style_dir", "Style Directory"))
        self.stylesheet_label.setText(self.localization.get("settings.label_stylesheet", "Stylesheet"))
        self.save_button.setText(self.localization.get("settings.button_save", "Save"))
