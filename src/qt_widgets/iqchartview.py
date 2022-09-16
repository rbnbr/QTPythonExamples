import PySide6
from PySide6.QtCharts import QChartView
from PySide6.QtCore import Signal
from PySide6.QtGui import QMouseEvent


class IQChartView(QChartView):
    """
    A QChartView widget which exposes mouse_pressed, mouse_releases, and mouse_moved Signals that are triggered whenever
    the mouseMoveEvent, mousePressEvent, or mouseReleaseEvent listeners are called.
    """
    mouse_pressed_signal = Signal(QMouseEvent)
    mouse_released_signal = Signal(QMouseEvent)
    mouse_moved_signal = Signal(QMouseEvent)
    mouse_clicked_signal = Signal(QMouseEvent)

    def __init__(self, chart, parent=None):
        super().__init__(chart, parent)

        self._moved = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._moved = True
        super().mouseMoveEvent(event)
        self.mouse_moved_signal.emit(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._moved = False
        super().mousePressEvent(event)
        self.mouse_pressed_signal.emit(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Need to call super() before my own signal.
        Otherwise the parent will emit a signal to a potentially deleted entity and the application crashes.
        :param event:
        :return:
        """
        super().mouseReleaseEvent(event)
        self.mouse_released_signal.emit(event)

        if not self._moved:
            self.mouse_clicked_signal.emit(event)
