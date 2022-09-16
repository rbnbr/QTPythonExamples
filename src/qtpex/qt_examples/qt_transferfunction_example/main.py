import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from qtpex.qt_widgets.transferfunction_widget import TransferFunctionWidget


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = TransferFunctionWidget("linear")
    window = QMainWindow()
    window.setCentralWidget(widget)

    window.show()

    sys.exit(app.exec())
