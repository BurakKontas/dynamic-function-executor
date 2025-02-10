import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import QTimer
from utils import load_settings, print
from datetime import datetime

severity_colors = {
    'INFO': 'rgba(0, 0, 255, 1)',  # Bright blue with 80% opacity
    'WARNING': 'rgba(255, 255, 0, 1)',  # Bright yellow with 80% opacity
    'ERROR': 'rgba(255, 0, 0, 1)',  # Strong red with 90% opacity
    'DEBUG': 'rgba(0, 255, 0, 1)',  # Bright green with 80% opacity
    'RESET': 'rgba(0, 0, 0, 1)',  # Black (fully opaque)
    # Intense red with 100% opacity for critical
    'CRITICAL': 'rgba(255, 120, 120, 1)',
    'DEV': 'rgba(255, 0, 255, 1)' 
}


class LogsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        self.layout.addWidget(self.log_display)
        
        open_logs = QPushButton("Open logs folder")
        open_logs.clicked.connect(lambda: os.startfile(load_settings(key="logs", default_value="logs")))
        self.layout.addWidget(open_logs)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_logs)
        self.timer.start(2000)

        self.load_logs()

    def load_logs(self):
        # Get current vertical scrollbar position
        scrollbar_pos = self.log_display.verticalScrollBar().value()

        log_path = load_settings(key="logs", default_value="logs")
        log_files = sorted([f for f in os.listdir(log_path) if f.startswith(
            "logs_") and f.endswith(".txt")], reverse=True)

        if log_files:
            latest_log = log_files[0]
            latest_log_path = os.path.join(log_path, latest_log)

            # Get the current date and hour
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_hour = datetime.now().strftime("%H")

            with open(latest_log_path, "r", encoding="utf-8") as file:
                log_content = file.readlines()

            # Filter logs by today's date and the current hour
            filtered_content = []
            for line in log_content:
                # Check if the line contains the current date and hour
                if current_date in line and current_hour in line:
                    filtered_content.append(line)

            if filtered_content:
                colored_content = self.apply_colors("".join(filtered_content))
                self.log_display.setHtml(colored_content)
            else:
                self.log_display.setPlainText("No logs found for this hour.")

        else:
            self.log_display.setPlainText("No logs found.")

        # Restore scrollbar position after the content is updated
        self.log_display.verticalScrollBar().setValue(scrollbar_pos)

    def apply_colors(self, log_content):
        lines = log_content.splitlines()
        colored_lines = []
        current_severity = None  # Keep track of the last severity

        for line in lines:
            # Determine the severity of the line
            if '[INFO]' in line:
                color = severity_colors['INFO']
                current_severity = 'INFO'
            elif '[WARNING]' in line:
                color = severity_colors['WARNING']
                current_severity = 'WARNING'
            elif '[ERROR]' in line:
                color = severity_colors['ERROR']
                current_severity = 'ERROR'
            elif '[DEBUG]' in line:
                color = severity_colors['DEBUG']
                current_severity = 'DEBUG'
            elif '[CRITICAL]' in line:
                color = severity_colors['CRITICAL']
                current_severity = 'CRITICAL'
            elif '[DEV]' in line:
                color = severity_colors['DEV']
                current_severity = 'DEV'
            else:
                # If no severity is found, use the previous line's severity
                if current_severity:
                    color = severity_colors[current_severity]
                else:
                    color = severity_colors['RESET']

            # Add the line to the colored output
            colored_line = f"<span style='color:{color}'>{line}</span>"
            colored_lines.append(colored_line)

        return "<br>".join(colored_lines)
