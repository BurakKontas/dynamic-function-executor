from PyQt6.QtWidgets import QComboBox
import inspect
import json
import os
import traceback
import re

from entities import DynamicFunction
from logs import LogsScreen
from settings import SettingsWindow
from utils import convert_to_serializable, get_all_functions, load_settings, print

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
        print("Updating functions...", severity="DEBUG")
        self.functions = new_functions
        self.refresh_tabs()


    def add_function_tab(self, dynamic_function: DynamicFunction):
        if not dynamic_function.settings.enabled:
            return

        tab = QWidget()
        form_layout = QFormLayout()

        func = dynamic_function.func
        settings = dynamic_function.settings
        sig = inspect.signature(func)
        param_inputs = {}

        # Add settings information to the tab header
        if settings.description:
            tab_header = QLabel(f"Description: {settings.description}")
            tab_header.setStyleSheet("font-weight: bold;")
            form_layout.addRow(tab_header)

        for param_name, param in sig.parameters.items():
            input_field = None
            param_type = param.annotation

            if param_type == bool:  # Handle boolean type parameter
                input_field = QComboBox()
                input_field.addItem("True", True)
                input_field.addItem("False", False)

                label = HoverLabel(f"{param_name} ({'bool'})", '')
                form_layout.addRow(label, input_field)

            elif param_type == str and "file_path" in param_name.lower():
                input_field = QLineEdit()
                file_button = QPushButton("Dosya Seç")
                file_button.clicked.connect(
                    lambda _, field=input_field: self.select_file(field))

                hbox = QHBoxLayout()
                hbox.addWidget(input_field)
                hbox.addWidget(file_button)

                label = HoverLabel(f"{param_name} ({param.annotation.__name__ if param.annotation != param.empty else 'Any'})", '')
                form_layout.addRow(label, hbox)

            else:
                if param_type in [dict, list, tuple, set] or (hasattr(param_type, '__name__') and param_type not in {int, str, float, bool}):
                    input_field = QTextEdit()
                    input_field.setFixedHeight(80)
                else:
                    input_field = QLineEdit()

                label = HoverLabel(f"{param_name} ({param.annotation.__name__ if param.annotation != param.empty else 'Any'})", '')
                form_layout.addRow(label, input_field)

            # Handle additional types for class instances
            if param_type is not None and hasattr(param_type, '__name__') and param_type not in {int, str, float, bool}:
                tooltip = constructor_parameter_analyzer(param_type)
                label.tooltip = f"{param_name}: {tooltip}"

            param_inputs[param_name] = input_field

        # Result field and Run button
        run_button = QPushButton("Run")
        result_field = QTextEdit()
        result_field.setAlignment(Qt.AlignmentFlag.AlignTop)
        result_field.setMaximumHeight(500)
        result_field.setReadOnly(True)

        run_button.clicked.connect(lambda: self.run_function(
            func, param_inputs, result_field))

        form_layout.addRow(run_button)
        form_layout.addRow(result_field)

        tab.setLayout(form_layout)
        self.tabs.addTab(tab, dynamic_function.settings.name)

        # Printing the parameter names and the widget values
        param_values = {}
        for param_name, _ in param_inputs.items():
            # Check if the parameter is a primitive type (int, str, float, bool)
            param_type = sig.parameters[param_name].annotation
            if param_type in [int, str, float, bool]:  # Primitive types
                # Just use the type name (e.g., 'int', 'str', etc.)
                description = param_type.__name__
            else:  # Non-primitive types (likely class instances)
                description = constructor_parameter_analyzer(param_type) if param_type else ""

            param_values[param_name] = {
                'description': description
            }

        # Now print the function name with the parameters and their descriptions
        print(f"Added tab for function: {func.__name__} with parameters: {param_values} and settings: {settings.to_dict()}", severity="DEBUG")



    def select_file(self, input_field):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*)")
        if file_path:
            input_field.setText(file_path)


    def run_function(self, func, param_inputs, result_label):
        params = {}
        sig = inspect.signature(func)

        for param_name, param in sig.parameters.items():
            # Widget değerini alıyoruz, doğrudan widget objesini yazdırmak yerine
            value = param_inputs[param_name].toPlainText() if isinstance(param_inputs[param_name], QTextEdit) else (
                param_inputs[param_name].currentText() if isinstance(
                    param_inputs[param_name], QComboBox) else param_inputs[param_name].text()
            )

            if hasattr(param.annotation, '__name__') and param.annotation not in {int, str, float, bool}:
                try:
                    param_value = convert_to_class_instance(
                        param.annotation, json.loads(value))
                    params[param_name] = param_value
                except Exception as e:
                    result_label.setText(f"Error: Failed to convert parameter '{
                                        param_name}' to {param.annotation.__name__}")
                    error_message = "".join(
                        traceback.format_exception(None, e, e.__traceback__))

                    print(error_message, severity="ERROR")
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
            
            # print(f"Function '{func.__name__}' executed with parameters: {params}", severity="DEBUG") # Commented out to reduce log verbosity
            cleaned_data = re.sub(r'\s+', ' ', formatted_result).strip()
            print(f"Result: {cleaned_data}", severity="DEBUG")

        except Exception as e:
            result_label.setText(f"Error: {str(e)}")
            error_message = "".join(
                traceback.format_exception(None, e, e.__traceback__))

            print(error_message, severity="ERROR")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Function Executor")
        self.setGeometry(100, 100, 800, 600)
        self.setFont(QFont("Roboto", 10))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Settings button
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings_window)
        settings_button.setMinimumWidth(120)
        button_layout.addWidget(settings_button)

        # Reload button
        reload_button = QPushButton("Reload")
        reload_button.clicked.connect(self.reload)
        reload_button.setMinimumWidth(120)
        button_layout.addWidget(reload_button)

        # Logs button to open logs screen
        logs_button = QPushButton("Open Logs")
        logs_button.clicked.connect(self.open_logs_window)
        logs_button.setMinimumWidth(120)
        button_layout.addWidget(logs_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)
        self.function_ui = DynamicFunctionUI([])
        layout.addWidget(self.function_ui)

        main_widget.setLayout(layout)
        self.reload()
        
    def open_settings_window(self):
        print("Opening settings window...", severity="DEBUG")
        self.second_window = SettingsWindow(self)
        self.second_window.show()
        self.second_window.move(self.x() + self.width() // 2 - self.second_window.width() // 2,
                                self.y() + self.height() // 2 - self.second_window.height() // 2)

        self.reload_css(self.second_window)

    def open_logs_window(self):
        print("Opening logs window...", severity="DEBUG")
        # Open the logs window
        self.logs_window = LogsScreen()
        self.logs_window.show()
        self.logs_window.move(self.x() + self.width() // 2 - self.logs_window.width() // 2,
                              self.y() + self.height() // 2 - self.logs_window.height() // 2)
        
        self.reload_css(self.logs_window)


    def get_log_folder(self):
        log_folder = load_settings(key="log_folder", default_value="logs")
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)  # Create log folder if not exists
        return log_folder

    def reload(self):
        print("Reloading functions and CSS...", severity="DEBUG")
        self.refresh_functions()
        self.reload_css(self)

    def refresh_functions(self):
        print("Refreshing functions...", severity="DEBUG")
        functions_path = load_settings(key="functions_path")
        new_functions = get_all_functions(functions_path)
        self.function_ui.update_functions(new_functions)

    def reload_css(self, window: QWidget):
        print("Reloading CSS...", severity="DEBUG")
        css_path = load_settings(key="css_path")
        if not css_path:
            print("CSS path not found in settings.json")
            return
        try:
            with open(css_path, "r") as f:
                css = f.read()
            window.setStyleSheet(css)
        except FileNotFoundError:
            print(f"CSS file not found at: {css_path}")
