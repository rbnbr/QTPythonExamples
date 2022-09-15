from PySide6.QtCore import Slot, QMargins, Qt, QMutex
from PySide6.QtGui import QMouseEvent, QColor
from PySide6.QtWidgets import QWidget
from typing import Union

from qt_widgets.interactive_chart import InteractiveChartWidget


class Interpolation:
    def __init__(self, mode: str = "linear"):
        self.mode = mode

    def __str__(self):
        return self.mode


class InterpolationModes:
    LINEAR = Interpolation("linear")


class TransferFunctionWidget(InteractiveChartWidget):
    def __init__(self, interpolation_mode: Union[Interpolation, str], parent: QWidget = None):
        super().__init__(parent=parent)

        if str(interpolation_mode) == str(InterpolationModes.LINEAR):
            self.interpolation_mode = str(interpolation_mode)
        else:
            self.interpolation_mode = "linear"

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

        # set background
        self.chart().setBackgroundBrush(QColor(Qt.lightGray))
        self.chart().setBackgroundRoundness(0)

        # adjust marker size
        self.scatterseries.setColor(QColor(Qt.black))
        self.scatterseries.setMarkerSize(2**3.5)
        self.scatterseries.setBorderColor(Qt.transparent)

        # set default points (they are not deletable)
        self.scatterseries.append(self.axis_x.min(), self.axis_y.min())
        self.left_point_idx = 0
        self.scatterseries.append(self.axis_x.max(), self.axis_y.max())
        self.right_point_idx = 1

        # TODO: handle interpolation mode

    @Slot()
    def chart_clicked(self, event: QMouseEvent):
        """
        Don't allow values out of range.
        Don't allow to left-click default points.
        :param event:
        :return:
        """
        if event.button().LeftButton and self.point_was_pressed_idx == self.left_point_idx or self.point_was_pressed_idx == self.right_point_idx:
            return

        value = self.chart().mapToValue(event.localPos())
        if value.x() <= self.axis_x.min() or value.x() >= self.axis_x.max() or \
                value.y() < self.axis_y.min() or value.y() > self.axis_y.max():
            pass
        else:
            super().chart_clicked(event)

    @Slot()
    def chart_moved(self, event: QMouseEvent):
        """
        Don't allow values out of range.

        Don't allow to change x-value for default points.
        :param event:
        :return:
        """
        value = self.chart().mapToValue(event.localPos())
        if value.x() < self.axis_x.min() or value.x() > self.axis_x.max() or \
                value.y() < self.axis_y.min() or value.y() > self.axis_y.max():
            pass
        else:
            if self.point_is_pressed_idx == self.left_point_idx or self.point_is_pressed_idx == self.right_point_idx:
                value.setX(self.scatterseries.at(self.point_is_pressed_idx).x())
                if event.buttons() == Qt.LeftButton:
                    self.scatterseries.replace(self.point_is_pressed_idx, value)
            else:
                super().chart_moved(event)
