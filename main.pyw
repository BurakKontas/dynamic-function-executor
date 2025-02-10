import sys
import traceback
from PyQt6.QtWidgets import QApplication
from ui import MainWindow
from utils import print


def global_exception_handler(exc_type, exc_value, exc_tb):
    if exc_type is not KeyboardInterrupt:
        error_message = f"Unhandled exception: {exc_value}\n"
        error_message += ''.join(traceback.format_tb(exc_tb))

        print(error_message, severity="CRITICAL")
        sys.exit(1)
    if exc_type is KeyboardInterrupt:
        print("KeyboardInterrupt received. Exiting...", severity="DEBUG")
        sys.exit(0)


if __name__ == "__main__":
    # Set the global exception handler
    sys.excepthook = global_exception_handler
    
    print("Starting the application...", severity="DEBUG")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

