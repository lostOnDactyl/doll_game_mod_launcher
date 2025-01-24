from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from datetime import datetime
import os

class EnhancedBasePage(QWidget):
    def __init__(self, localization, settings, save_settings_callback):
        super().__init__()
        self.localization = localization
        self.settings = settings
        self.save_settings_callback = save_settings_callback
        self.log_file = None  # Placeholder for log file, can be set by derived classes

    def initialize_log_file(self, log_directory, log_name="page_log"):
        """Initialize a log file for the page."""
        os.makedirs(log_directory, exist_ok=True)
        self.log_file = os.path.join(log_directory, f"{log_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
        with open(self.log_file, "w") as file:
            file.write(f"Log started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def log(self, message):
        """Write a message to the log file."""
        timestamped_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        print(timestamped_message)  # For debugging, remove in production
        if self.log_file:
            with open(self.log_file, "a") as file:
                file.write(timestamped_message + "\n")

    def batch_update_ui(self, components, values):
        """
        Batch update UI components with given values.
        :param components: A list of components (e.g., buttons, labels)
        :param values: A list of corresponding values to set (e.g., text, checked state)
        """
        for component, value in zip(components, values):
            if hasattr(component, "setText"):
                component.setText(value)
            elif hasattr(component, "setChecked"):
                component.setChecked(value)

    def reload(self, localization, settings):
        """Reload settings and localization dynamically."""
        self.localization = localization
        self.settings = settings
        self.update_ui()