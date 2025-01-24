from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QScrollArea, QTextEdit
from .base import EnhancedBasePage
import os
import time
import ctypes

class HomePage(EnhancedBasePage):
    def __init__(self, localization, settings, save_settings_callback):
        super().__init__(localization, settings, save_settings_callback)
        self.initialize_log_file(settings["user_preferences"].get("log_dir", "logs"), "home_page")
        self.layout = QHBoxLayout(self)
        self.create_layout()

    def create_layout(self):
        # Left dock (buttons and options)
        self.left_dock = QVBoxLayout()

        # Launch game button
        self.launch_button = QPushButton()
        self.launch_button.clicked.connect(self.launch_game)
        self.left_dock.addWidget(self.launch_button)

        # Checkbox for 3DMigoto
        self.option_3dmigoto = QCheckBox()
        self.option_3dmigoto.stateChanged.connect(self.update_3dmigoto_setting)
        self.left_dock.addWidget(self.option_3dmigoto)

        self.left_dock.addStretch()
        self.layout.addLayout(self.left_dock, 1)

        # Right content (Info section with scroll area)
        self.right_area = QScrollArea()
        self.right_area.setWidgetResizable(True)

        self.info_content = QTextEdit()
        self.info_content.setReadOnly(True)
        self.right_area.setWidget(self.info_content)
        self.layout.addWidget(self.right_area, 3)

        self.update_ui()

    def update_ui(self):
        """Update UI elements with localization and settings."""
        components = [self.launch_button, self.option_3dmigoto, self.info_content]
        values = [
            self.localization.get("home.button_launch_game", "Launch Game"),
            self.localization.get("home.option_use_3dmigoto", "Use 3DMigoto"),
            self.localization.get("home.default_message", "Welcome to the Game Launcher!"),
        ]
        self.batch_update_ui(components, values)
        self.option_3dmigoto.setChecked(self.settings["user_preferences"].get("use_3dmigoto", False))

    def launch_game(self):
        """Launch the game, optionally with 3DMigoto."""
        use_3dmigoto = self.option_3dmigoto.isChecked()

        if use_3dmigoto:
            if not self.launch_3dmigoto():
                self.log("Aborting game launch due to 3DMigoto failure.")
                return

        time.sleep(5)

        game_exe = self.settings["paths"].get("game_executable", "")
        if not os.path.exists(game_exe):
            self.log("Error: Game executable path not set or invalid!")
            return

        game_dir = os.path.dirname(game_exe)
        self.log(f"Launching game from directory: {game_dir}")
        if self.launch_as_admin(game_exe, working_directory=game_dir):
            self.log("Game launched successfully!")
        else:
            self.log("Failed to launch game.")

    def launch_3dmigoto(self):
        """Launch 3DMigoto."""
        migoto_exe = self.settings["paths"].get("migoto_executable", "")
        if not os.path.exists(migoto_exe):
            self.log("Error: 3DMigoto executable path not set or invalid!")
            return False

        migoto_dir = os.path.dirname(migoto_exe)
        self.log(f"Launching 3DMigoto from directory: {migoto_dir}")
        if self.launch_as_admin(migoto_exe, working_directory=migoto_dir):
            self.log("3DMigoto launched successfully.")
            return True
        else:
            self.log("Failed to launch 3DMigoto.")
            return False

    def launch_as_admin(self, executable_path, working_directory=None):
        """Launch a process as an administrator."""
        try:
            response = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable_path, None, working_directory, 1
            )
            if response <= 32:
                raise Exception(f"Failed to launch {executable_path} with error code {response}")
            return True
        except Exception as e:
            self.log(f"Error launching {executable_path} as admin: {e}")
            return False

    def update_3dmigoto_setting(self, state):
        """Update the 3DMigoto setting."""
        self.settings["user_preferences"]["use_3dmigoto"] = bool(state)
        self.save_settings_callback(self.settings)

    def reload(self, localization, settings):
        """Reload the page."""
        super().reload(localization, settings)
        self.update_ui()

    def log(self, message):
        """Log a message to both the file and the on-screen content."""
        timestamped_message = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        # Append to the on-screen log
        if self.info_content:
            self.info_content.append(timestamped_message)
        # Write to the log file
        super().log(message)
