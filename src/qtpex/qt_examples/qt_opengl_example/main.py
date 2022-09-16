import argparse
import sys

from PySide6.QtWidgets import QApplication
from qtpex.qt_examples.qt_opengl_example.src.mainwindow import MainWindow

from PySide6.QtGui import QSurfaceFormat


if __name__ == "__main__":
    options = argparse.ArgumentParser()
    options.add_argument("-f", "--file", type=str, required=False)
    args = options.parse_args()

    app = QApplication(sys.argv)

    # set default format
    format = QSurfaceFormat()
    format.setDepthBufferSize(24)
    format.setStencilBufferSize(8)
    format.setVersion(4, 6)
    format.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(format)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

    # print(data)
