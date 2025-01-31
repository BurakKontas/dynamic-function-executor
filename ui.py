import inspect
import json
from settings import SettingsWindow
from utils import convert_to_serializable, get_all_functions, print

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QToolTip, QMainWindow
)
from utils import constructor_parameter_analyzer, convert_to_class_instance, print
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout
from PyQt6.QtGui import QAction


class HoverLabel(QLabel):
    def __init__(self, text, tooltip):
        super().__init__(text)
        self.setToolTip(tooltip)
        self.tooltip = tooltip
        self.setMouseTracking(True)

    def enterEvent(self, event):
        font_metrics = QFontMetrics(self.font())
        max_width = 400
        wrapped_text = self.wrap_text(self.tooltip, font_metrics, max_width)

        QToolTip.showText(QCursor.pos(), wrapped_text, self)

    def leaveEvent(self, event):
        QToolTip.hideText()

    def wrap_text(self, text, font_metrics, max_width):
        words = text.split()
        wrapped_lines = []
        current_line = ""

        for word in words:
            if font_metrics.horizontalAdvance(current_line + word) <= max_width:
                current_line += word + " "
            else:
                wrapped_lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            wrapped_lines.append(current_line.strip())

        return "\n".join(wrapped_lines)


class DynamicFunctionUI(QWidget):
    def __init__(self, functions):
        super().__init__()
        self.functions = functions
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.refresh_tabs()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def refresh_tabs(self):
        # Clear existing tabs
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)

        # Add new tabs for each function
        for func in self.functions:
            self.add_function_tab(func)

    def update_functions(self, new_functions):
        self.functions = new_functions
        self.refresh_tabs()

    def add_function_tab(self, func):
        tab = QWidget()
        form_layout = QFormLayout()

        sig = inspect.signature(func)
        param_inputs = {}

        QToolTip.setFont(QFont('Arial', 10))

        for param_name, param in sig.parameters.items():
            input_field = None
            param_type = param.annotation

            if param_type == str and "file_path" in param_name.lower():
                input_field = QLineEdit()
                file_button = QPushButton("Dosya Seç")
                file_button.clicked.connect(
                    lambda _, field=input_field: self.select_file(field))

                hbox = QHBoxLayout()
                hbox.addWidget(input_field)
                hbox.addWidget(file_button)

                label = HoverLabel(f"{param_name} ({
                                   param.annotation.__name__ if param.annotation != param.empty else 'Any'})", '')
                form_layout.addRow(label, hbox)
            else:
                if param_type in [dict, list, tuple, set] or (hasattr(param_type, '__name__') and param_type not in {int, str, float, bool}):
                    input_field = QTextEdit()
                    input_field.setFixedHeight(80)
                else:
                    input_field = QLineEdit()

                label = HoverLabel(f"{param_name} ({
                                   param.annotation.__name__ if param.annotation != param.empty else 'Any'})", '')
                form_layout.addRow(label, input_field)

            if param_type is not None and hasattr(param_type, '__name__') and param_type not in {int, str, float, bool}:
                tooltip = constructor_parameter_analyzer(param_type)
                label.tooltip = f"{param_name}: {tooltip}"

            param_inputs[param_name] = input_field

        run_button = QPushButton("Run")
        result_label = QLabel("Result: ")
        result_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        run_button.clicked.connect(lambda: self.run_function(
            func, param_inputs, result_label))

        form_layout.addRow(run_button)
        form_layout.addRow(result_label)

        tab.setLayout(form_layout)
        self.tabs.addTab(tab, func.__name__)

    def select_file(self, input_field):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*)")
        if file_path:
            input_field.setText(file_path)

    def run_function(self, func, param_inputs, result_label):
        params = {}
        sig = inspect.signature(func)

        for param_name, param in sig.parameters.items():
            value = param_inputs[param_name].toPlainText() if isinstance(
                param_inputs[param_name], QTextEdit) else param_inputs[param_name].text()

            if hasattr(param.annotation, '__name__') and param.annotation not in {int, str, float, bool}:
                try:
                    param_value = convert_to_class_instance(
                        param.annotation, json.loads(value))
                    params[param_name] = param_value
                except Exception as e:
                    result_label.setText(f"Error: Failed to convert parameter '{
                                         param_name}' to {param.annotation.__name__}")
                    print(e.with_traceback())
                    return
            else:
                if param.annotation in [int, float]:
                    try:
                        value = param.annotation(value)
                    except ValueError:
                        result_label.setText("Error: Invalid input type")
                        return
                params[param_name] = value
        try:
            result = func(**params)
            result = convert_to_serializable(result)

            if isinstance(result, (dict, list, tuple, set)):
                formatted_result = json.dumps(
                    result, indent=4, ensure_ascii=False)
            elif isinstance(result, str):
                formatted_result = result
            else:
                formatted_result = str(result)

            result_label.setText(
                f"<pre><strong>{formatted_result}</strong></pre>")

        except Exception as e:
            result_label.setText(f"Error: {str(e)}")
            print(e.with_traceback())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Function Executor")
        self.setGeometry(100, 100, 800, 600)

        # Widget'ları oluştur
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Settings butonu
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings_window)
        settings_button.setFixedSize(120, 35)
        button_layout.addWidget(settings_button)

        # Refresh butonu
        reload_button = QPushButton("Reload")
        reload_button.clicked.connect(self.reload)
        reload_button.setFixedSize(120, 35)
        button_layout.addWidget(reload_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)
        self.function_ui = DynamicFunctionUI([])
        layout.addWidget(self.function_ui)

        main_widget.setLayout(layout)
        self.reload()

    def open_settings_window(self):
        self.second_window = SettingsWindow(self)
        self.second_window.show()
        self.second_window.move(self.x() + self.width() // 2 - self.second_window.width() // 2,
                                self.y() + self.height() // 2 - self.second_window.height() // 2)
        
        from css import load_styles
        self.second_window.setStyleSheet(load_styles())

    def reload(self):
        self.refresh_functions()
        self.reload_css()

    def refresh_functions(self):
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                functions_path = settings.get("functions_path", "examples")
        except FileNotFoundError:
            functions_path = "examples"

        new_functions = get_all_functions(functions_path)
        self.function_ui.update_functions(new_functions)

    def reload_css(self):
        from css import load_styles
        self.setStyleSheet(load_styles())