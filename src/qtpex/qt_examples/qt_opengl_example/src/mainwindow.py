from PySide6.QtWidgets import QMainWindow
from qtpex.qt_examples.qt_opengl_example.src.ui_mainwindow import Ui_MainWindow
from qtpex.qt_examples.qt_opengl_example.src.opengl_widget import OpenGLWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, OpenGLWidget)
