import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from qt_widgets.interactive_chart import InteractiveChartWidget


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = InteractiveChartWidget()
    window = QMainWindow()
    window.setCentralWidget(widget)

    window.show()

    sys.exit(app.exec())
