import os.path
from builtins import RuntimeError

from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat, QOpenGLContext
from PySide6.QtOpenGL import *
from OpenGL.GL import *
from PySide6.QtCore import Slot
import numpy as np
import sys


def path_rel_to_parent_dir(p):
    # return the path p as if it was relative to the parent directory
    # e.g., __file__ is C:/src/__file__.py, then path_rel_to_parent_dir("./glsl/__file__.glsl") -> C:/glsl/__file__.glsl
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", p))


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.setFormat(QSurfaceFormat())  # in main we set the default format

        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.vao = QOpenGLVertexArrayObject()

        self.program = QOpenGLShaderProgram()

    def initializeGL(self) -> None:
        f = self.context().functions()
        f.initializeOpenGLFunctions()

        # print version
        print(f.glGetString(GL_VERSION))

        # set background
        f.glClearColor(0, 0, 0, 1)

        # enable depth testing
        f.glEnable(GL_DEPTH_TEST)
        f.glDepthFunc(GL_LESS)  # smaller depth value is closer

        # define triangle
        points = np.array([
            0.0, 0.5, 0.0,
            0.5, -0.5, 0.0,
            -0.5, -0.5, 0.0
        ], dtype=np.float32)

        # create and init vbo
        if not self.vbo.create():
            raise RuntimeError("failed to create vbo")

        self.vbo.bind()
        self.vbo.allocate(points.tobytes(), points.nbytes)
        self.vbo.setUsagePattern(QOpenGLBuffer.StaticDraw)
        self.vbo.release()

        # create and init vao
        if not self.vao.create():
            raise RuntimeError("failed to create vao")

        self.vao.bind()
        self.vbo.bind()
        f.glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        # f.glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)  # this does fail due to wrong signature
        # glVertexAttribPointer(0, 0, 0, False, 0, void)
        self.vao.release()

        # init shader
        print(path_rel_to_parent_dir("glsl/vertex_shader.glsl"))
        vs = QOpenGLShader(QOpenGLShader.Vertex)
        if not vs.compileSourceFile(path_rel_to_parent_dir("glsl/vertex_shader.glsl")):
            raise RuntimeError("failed to compile vertex shader.\nlog: '{}'".format(vs.log()))

        fs = QOpenGLShader(QOpenGLShader.Fragment)
        if not fs.compileSourceFile(path_rel_to_parent_dir("./glsl/fragment_shader.glsl")):
            raise RuntimeError("failed to compile fragment shader\n" + fs.log())

        # init program
        if not self.program.create():
            raise RuntimeError("failed to create program\n", self.program.log())

        self.program.bind()
        self.program.addShader(vs)
        self.program.addShader(fs)
        self.program.link()
        self.program.removeAllShaders()
        self.program.release()

    def paintGL(self) -> None:
        f = self.context().functions()
        f.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        f.glUseProgram(self.program.programId())

        self.vao.bind()
        f.glDrawArrays(GL_TRIANGLES, 0, 3)
        #self.vao.release()

    def resizeGL(self, w:int, h:int) -> None:
        print(w, h)

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        # print("cleanup")
        pass

