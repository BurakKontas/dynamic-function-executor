import sys
from PyQt6.QtWidgets import (QApplication)
from ui import DynamicFunctionUI
from utils import get_all_functions



if __name__ == "__main__":
    functions = get_all_functions()
    app = QApplication(sys.argv)
    window = DynamicFunctionUI(functions=functions)
    window.show()
    sys.exit(app.exec())
