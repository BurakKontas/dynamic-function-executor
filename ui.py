import inspect
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout, QLineEdit, QTextEdit, QPushButton, QLabel, QToolTip
)
from utils import constructor_parameter_analyzer, convert_to_class_instance, print
from PyQt6.QtGui import QFont, QCursor
import json
from utils import print


from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout

class HoverLabel(QLabel):
    def __init__(self, text, tooltip):
        super().__init__(text)
        self.setToolTip(tooltip)
        self.tooltip = tooltip
        self.setMouseTracking(True)  # Fare hareketlerini izle
    
    def enterEvent(self, event):
        # Tooltip metnini belirli bir genişlikle sınırla
        font_metrics = QFontMetrics(self.font())
        max_width = 400  # Tooltip'in maksimum genişliği
        wrapped_text = self.wrap_text(self.tooltip, font_metrics, max_width)
        
        # Tooltip'i fare pozisyonuna göre göster
        QToolTip.showText(QCursor.pos(), wrapped_text, self)
    
    def leaveEvent(self, event):
        QToolTip.hideText()
    
    def wrap_text(self, text, font_metrics, max_width):
        """Metni belirli bir genişliğe göre satır sonlarına böler."""
        words = text.split()
        wrapped_lines = []
        current_line = ""

        for word in words:
            # Mevcut satıra kelimeyi ekleyip eklemeyeceğimizi kontrol et
            if font_metrics.horizontalAdvance(current_line + word) <= max_width:
                current_line += word + " "
            else:
                wrapped_lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            wrapped_lines.append(current_line.strip())
        
        return "\n".join(wrapped_lines)


from PyQt6.QtWidgets import QHBoxLayout  # Yatay düzen için eklendi

class DynamicFunctionUI(QWidget):
    def __init__(self, functions):
        super().__init__()
        self.functions = functions
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        for func in self.functions:
            self.add_function_tab(func)
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def add_function_tab(self, func):
        tab = QWidget()
        form_layout = QFormLayout()

        sig = inspect.signature(func)
        param_inputs = {}

        QToolTip.setFont(QFont('Arial', 10))

        for param_name, param in sig.parameters.items():
            input_field = None
            param_type = param.annotation

            # Eğer parametre tipi str ve adında "file_path" geçiyorsa, dosya seçme butonu ekle
            if param_type == str and "file_path" in param_name.lower():
                input_field = QLineEdit()
                file_button = QPushButton("Dosya Seç")
                file_button.clicked.connect(lambda _, field=input_field: self.select_file(field))
                
                # Yatay düzen oluştur ve input alanı ile butonu yan yana yerleştir
                hbox = QHBoxLayout()
                hbox.addWidget(input_field)
                hbox.addWidget(file_button)
                
                # Etiketi ve yatay düzeni forma ekle
                label = HoverLabel(f"{param_name} ({param.annotation.__name__ if param.annotation != param.empty else 'Any'})", '')
                form_layout.addRow(label, hbox)
            else:
                # Diğer parametreler için standart input alanı ekle
                if param_type in [dict, list, tuple, set] or (hasattr(param_type, '__name__') and param_type not in {int, str, float, bool}):
                    input_field = QTextEdit()
                    input_field.setFixedHeight(80)
                else:
                    input_field = QLineEdit()
                
                # Etiket ve input alanını forma ekle
                label = HoverLabel(f"{param_name} ({param.annotation.__name__ if param.annotation != param.empty else 'Any'})", '')
                form_layout.addRow(label, input_field)

            # Tooltip'i ayarla (eğer parametre tipi bir sınıfsa)
            if param_type is not None and hasattr(param_type, '__name__') and param_type not in {int, str, float, bool}:
                tooltip = constructor_parameter_analyzer(param_type)
                label.tooltip = f"{param_name}: {tooltip}"

            # Input alanını parametreler sözlüğüne ekle
            param_inputs[param_name] = input_field

        run_button = QPushButton("Run")
        result_label = QLabel("Result: ")

        run_button.clicked.connect(lambda: self.run_function(func, param_inputs, result_label))

        form_layout.addRow(run_button)
        form_layout.addRow(result_label)

        tab.setLayout(form_layout)
        self.tabs.addTab(tab, func.__name__)

    def select_file(self, input_field):
        """Dosya seçme diyaloğunu açar ve seçilen dosya yolunu input alanına yazar."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "All Files (*)")
        if file_path:
            input_field.setText(file_path)
    
    def run_function(self, func, param_inputs, result_label):
        params = {}
        sig = inspect.signature(func)

        for param_name, param in sig.parameters.items():
            value = param_inputs[param_name].toPlainText() if isinstance(param_inputs[param_name], QTextEdit) else param_inputs[param_name].text()

            # Eğer parametre tipi bir sınıfsa, örneklendir
            if hasattr(param.annotation, '__name__') and param.annotation not in {int, str, float, bool}:
                try:
                    param_value = convert_to_class_instance(param.annotation, json.loads(value))  # JSON'dan sözlüğe dönüştür
                    params[param_name] = param_value
                except Exception as e:
                    result_label.setText(f"Error: Failed to convert parameter '{param_name}' to {param.annotation.__name__}")
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
            result_label.setText(f"Result: {result}")
        except Exception as e:
            result_label.setText(f"Error: {str(e)}")
            print(e.with_traceback())