from PySide6.QtCharts import QChartView
from PySide6.QtCore import Signal
from PySide6.QtGui import QMouseEvent


class IChartView(QChartView):
    mouse_pressed = Signal(QMouseEvent)
    mouse_released = Signal(QMouseEvent)
    mouse_moved = Signal(QMouseEvent)

    def __init__(self, chart, parent=None):
        super().__init__(chart, parent)

    def mouseMoveEvent(self, event:QMouseEvent) -> None:
        self.mouse_moved.emit(event)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event:QMouseEvent) -> None:
        self.mouse_pressed.emit(event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event:QMouseEvent) -> None:
        self.mouse_released.emit(event)
        super().mouseReleaseEvent(event)
