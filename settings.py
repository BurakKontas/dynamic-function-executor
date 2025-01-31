import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout

from utils import load_settings, print


class SettingsWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # Parent window reference
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Functions Path Section
        func_hbox = QHBoxLayout()
        self.path_label = QLabel("Functions Path:")
        func_hbox.addWidget(self.path_label)
        self.path_input = QLineEdit(
            load_settings("functions_path","examples"))
        func_hbox.addWidget(self.path_input)
        select_folder_button = QPushButton("Select Folder")
        select_folder_button.clicked.connect(self.select_folder)
        func_hbox.addWidget(select_folder_button)
        layout.addLayout(func_hbox)

        # CSS Path Section
        css_hbox = QHBoxLayout()
        self.css_label = QLabel("CSS File Path:")
        css_hbox.addWidget(self.css_label)
        self.css_input = QLineEdit(load_settings("css_path", "style.css"))
        css_hbox.addWidget(self.css_input)
        select_css_button = QPushButton("Select File")
        select_css_button.clicked.connect(self.select_css_file)
        css_hbox.addWidget(select_css_button)
        layout.addLayout(css_hbox)

        # Log Folder Path Section
        log_folder_hbox = QHBoxLayout()
        self.log_folder_label = QLabel("Logs Folder Path:")
        log_folder_hbox.addWidget(self.log_folder_label)
        self.log_folder_input = QLineEdit(
            load_settings("log_folder", "logs"))
        log_folder_hbox.addWidget(self.log_folder_input)
        select_log_folder_button = QPushButton("Select Folder")
        select_log_folder_button.clicked.connect(self.select_log_folder)
        log_folder_hbox.addWidget(select_log_folder_button)
        layout.addLayout(log_folder_hbox)

        # Info Label
        info_label = QLabel("Set the paths to the function modules, CSS file, and logs folder.\n"
                            "You can also select them manually.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Save Button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.path_input.setText(folder)

    def select_log_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Logs Folder")
        if folder:
            self.log_folder_input.setText(folder)

    def select_css_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select CSS File", "", "CSS Files (*.css);;All Files (*)")
        if file:
            self.css_input.setText(file)

    def save_settings(self):
        functions_path = self.path_input.text()
        css_path = self.css_input.text()
        log_folder_path = self.log_folder_input.text()

        with open("settings.json", "w") as file:
            json.dump({"functions_path": functions_path,
                      "css_path": css_path,
                       "log_folder": log_folder_path}, file)

        print(f"Settings saved: Functions Path: {functions_path}, CSS Path: {css_path}, Log Folder: {log_folder_path}", severity="DEBUG")

        # Refresh the parent window's functions
        self.parent.reload()

        self.close()
