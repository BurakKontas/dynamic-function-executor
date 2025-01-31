import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout

class SettingsWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # Parent penceresini saklıyoruz
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 250)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create a horizontal layout for the label, input, and button
        hbox = QHBoxLayout()

        # Functions Path Label
        self.path_label = QLabel("Functions Path:")
        hbox.addWidget(self.path_label)

        # Functions Path Input
        self.path_input = QLineEdit(self.load_settings("functions_path", "examples"))
        hbox.addWidget(self.path_input)

        # Select Folder Button
        select_folder_button = QPushButton("Select Folder")
        select_folder_button.clicked.connect(self.select_folder)
        hbox.addWidget(select_folder_button)

        layout.addLayout(hbox)  # Add the horizontal layout to the main layout

        # Info Label (for explanation)
        info_label = QLabel("Set the path to the folder containing your function modules.\n"
                             "You can also select the folder manually by clicking 'Select Folder'.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Save Button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def load_settings(self, key, default_value):
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                return settings.get(key, default_value)
        except (FileNotFoundError, json.JSONDecodeError):
            return default_value

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.path_input.setText(folder)

    def save_settings(self):
        functions_path = self.path_input.text()
        with open("settings.json", "w") as file:
            json.dump({"functions_path": functions_path}, file)

        print(f"Functions path saved: {functions_path}")
        
        # Parent pencerenin refresh_functions fonksiyonunu çağırıyoruz
        self.parent.refresh_functions()

        self.close()
