from PySide6.QtCharts import QXYSeries
from PySide6.QtCore import Slot, QMargins, Qt, QPoint
from PySide6.QtGui import QMouseEvent, QColor
from PySide6.QtWidgets import QWidget
from typing import Union

from qt_widgets.interactive_chart import InteractiveChartWidget
from qt_objects.configurable_line_series import ConfigurableLineSeries


def printd(*args, **kwargs):
    if not True:
        print(*args, **kwargs)


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
            self.interpolation_mode = InterpolationModes.LINEAR.mode

        # remove scatter series first to plot it above the others later
        self.chart().removeSeries(self.scatterseries)

        self.line_series = None

        if self.interpolation_mode == InterpolationModes.LINEAR.mode:
            self.line_series = ConfigurableLineSeries()
            self.chart().addSeries(self.line_series)
            self.line_series.attachAxis(self.axis_x)
            self.line_series.attachAxis(self.axis_y)

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

        # connect signal to slots
        self.scatterseries.pointAdded.connect(self.point_added)
        self.scatterseries.pointRemoved.connect(self.point_removed)
        self.scatterseries.pointReplaced.connect(self.point_replaced)

        # set default points (they are not deletable)
        self.scatterseries.append(self.axis_x.min(), self.axis_y.min())
        self.scatterseries.append(self.axis_x.max(), self.axis_y.max())
        # self.scatterseries.setPointConfiguration(0, {QXYSeries.PointConfiguration.Color: QColor(Qt.red)})
        # self.scatterseries.setPointConfiguration(1, {QXYSeries.PointConfiguration.Color: QColor(Qt.red)})

        self.chart().addSeries(self.scatterseries)

        # color selector
        self.scatterseries.clicked.connect(self.open_color_picker)

    @Slot()
    def open_color_picker(self, point: QPoint):
        """
        Opens the color picker for this point to change its color.
        :param point:
        :return:
        """

    @Slot(int)
    def point_added(self, idx: int):
        if self.interpolation_mode == InterpolationModes.LINEAR.mode:
            self.line_series.insert(idx, self.scatterseries.at(idx))

        self.scatterseries.setPointConfiguration(idx, {QXYSeries.PointConfiguration.Color: QColor(Qt.black)})

        printd("point_added")

    @Slot(int)
    def point_removed(self, idx: int):
        if self.interpolation_mode == InterpolationModes.LINEAR.mode:
            self.line_series.remove(idx)
        printd("point_removed")

    @Slot(int)
    def point_replaced(self, idx: int):
        if self.interpolation_mode == InterpolationModes.LINEAR.mode:
            self.line_series.replace(idx, self.scatterseries.at(idx))
        printd("point_replaced")

    @Slot()
    def chart_clicked(self, event: QMouseEvent):
        """
        Don't allow values out of range.
        Don't allow to left-click default points.
        :param event:
        :return:
        """
        if event.button().LeftButton and self.point_was_pressed_idx == 0 or \
                self.point_was_pressed_idx == self.scatterseries.count() - 1:
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
            if self.point_is_pressed_idx == 0 or self.point_is_pressed_idx == self.scatterseries.count() - 1:
                value.setX(self.scatterseries.at(self.point_is_pressed_idx).x())
                if event.buttons() == Qt.LeftButton:
                    self.scatterseries.replace(self.point_is_pressed_idx, value)
            else:
                super().chart_moved(event)
