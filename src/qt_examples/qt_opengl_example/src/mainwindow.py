from PySide6.QtWidgets import QMainWindow
from src.ui_mainwindow import Ui_MainWindow
from src.opengl_widget import OpenGLWidget
from PySide6 import QtCore


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, OpenGLWidget)
