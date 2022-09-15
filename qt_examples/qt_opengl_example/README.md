# QT Python and OpenGL

I wanted to try out using QT + Pythong + OpenGL and it seems to be working.
Though, some QT bindings fail (e.g., the self.context().functions().glVertexAttribPointer(...) of the QOpenGLWidget) as well as there is missing support in QT for OpenGL constants.
Thus, I use the [python for OpenGL](https://pypi.org/project/PyOpenGL/) package to workaround that.

In this example, I implemented the very easy first tutorial from https://antongerdelan.net/opengl/hellotriangle.html.
