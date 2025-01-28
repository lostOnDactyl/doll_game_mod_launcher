from PySide6.QtWidgets import QHBoxLayout

def create_browse_row(input_field, browse_button):
    """Create a layout with an input field and a browse button."""
    row = QHBoxLayout()
    row.addWidget(input_field)
    row.addWidget(browse_button)
    return row

from PySide6.QtWidgets import QFrame, QVBoxLayout, QGridLayout, QLabel, QCheckBox, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

def create_mod_row(mod, enable_mapping, toggle_callback, expand_callback):
    """Factory to create a mod row with its details."""
    row = QFrame()
    row_layout = QGridLayout(row)
    row_layout.setContentsMargins(5, 5, 5, 5)

    # Checkbox
    checkbox = QCheckBox()
    checkbox.setChecked(enable_mapping.get(mod["id"], False))  # Set initial state
    checkbox.stateChanged.connect(lambda state, mod_id=mod["id"]: toggle_callback(mod_id, state))
    row_layout.addWidget(checkbox, 0, 0, alignment=Qt.AlignCenter)

    # Mod Details
    mod_name = QLabel(mod["id"])
    row_layout.addWidget(mod_name, 0, 1)

    # Display Type
    mod_type = mod.get("type", "Unknown")
    row_layout.addWidget(QLabel(mod_type), 0, 2)

    # Display Version
    mod_version = mod["data"].get("version", "Unknown")
    row_layout.addWidget(QLabel(mod_version), 0, 3)

    # Expand/Collapse Button
    expand_button = QPushButton()
    expand_button.setIcon(QIcon(":/icons/triangle_down.png"))  # Replace with appropriate icon path
    expand_button.setFixedSize(20, 20)
    expand_button.clicked.connect(lambda: expand_callback(expand_button))
    row_layout.addWidget(expand_button, 0, 4)

    return row, expand_button

def create_mod_details(mod):
    """Factory to create detailed information for a mod."""
    details = QFrame()
    details.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
    details.setVisible(False)  # Initially hidden
    details_layout = QVBoxLayout(details)
    details_layout.setContentsMargins(10, 10, 10, 10)

    # Path
    mod_path = mod.get("path", "Unknown")
    details_layout.addWidget(QLabel(f"Path: {mod_path}"))

    # Buffers
    buffers = mod["data"].get("buffers", [])
    details_layout.addWidget(QLabel(f"Buffers: {', '.join(buffers) if buffers else 'None'}"))

    # Targets
    targets = mod.get("targets", [])
    if targets:
        details_layout.addWidget(QLabel("Targets:"))
        for target in targets:
            char_or_obj = target.get("char") or target.get("object")
            target_type = target.get("type", "Unknown")
            target_note = target.get("note", "No note provided")
            target_hash = target.get("hash", "Unknown")
            details_layout.addWidget(QLabel(f"  - {target_type} ({char_or_obj}): {target_note} [{target_hash}]"))

    return details
