from PySide6.QtCore import Slot, QMargins, Qt, QMutex
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget

from qt_widgets.interactive_chart import InteractiveChartWidget


class TransferFunctionWidget(InteractiveChartWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent)

        # set x-axis
        self.axis_x.setTickCount(2)
        self.axis_x.setRange(0, 255)
        self.axis_x.setVisible(False)

        # set y-axis
        self.axis_y.setTickCount(2)
        self.axis_y.setRange(0, 1)
        self.axis_y.setVisible(False)

        # remove border empty space
        self.chart().setMargins(QMargins(0, 0, 0, 0))
        self.chart().legend().setVisible(False)

    @Slot()
    def chart_clicked(self, event: QMouseEvent):
        """
        Don't allow values out of range.
        :param event:
        :return:
        """
        value = self.chart().mapToValue(event.localPos())
        if value.x() < self.axis_x.min() or value.x() > self.axis_x.max() or \
                value.y() < self.axis_y.min() or value.y() > self.axis_y.max():
            pass
        else:
            super().chart_clicked(event)

    @Slot()
    def chart_moved(self, event: QMouseEvent):
        """
        Don't allow values out of range.
        :param event:
        :return:
        """
        value = self.chart().mapToValue(event.localPos())
        if value.x() < self.axis_x.min() or value.x() > self.axis_x.max() or \
                value.y() < self.axis_y.min() or value.y() > self.axis_y.max():
            pass
        else:
            super().chart_moved(event)
