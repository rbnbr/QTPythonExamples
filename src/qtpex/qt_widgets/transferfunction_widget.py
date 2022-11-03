import json

import PySide6
from PySide6.QtCharts import QXYSeries
from PySide6.QtCore import Slot, QMargins, Qt, Signal
from PySide6.QtGui import QMouseEvent, QColor
from PySide6.QtWidgets import QWidget, QColorDialog
from typing import Union, Any

from qtpex.qt_utility.interpolation import interpolate_colors
from qtpex.qt_widgets.interactive_chart import InteractiveChartWidget
from qtpex.qt_objects.configurable_line_series import ConfigurableLineSeries


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
    changed_signal = Signal()  # fired when the something was changed that affects the resulting color map

    def __init__(self, interpolation_mode: Union[Interpolation, str], x_range=None, y_range=None, *, parent: QWidget = None):
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

        # x and y range
        self.x_range = (0, 255) if x_range is None else x_range
        self.y_range = (0, 1) if y_range is None else y_range

        assert self.x_range[0] < self.x_range[1], "invalid x-range: {}".format(self.x_range)
        assert self.y_range[0] < self.y_range[1], "invalid y-range: {}".format(self.y_range)

        marker_size = 2**3.5

        # set margins (xleft, xright, ybottom, ytop)
        self.axis_margins = (marker_size, marker_size - 4, marker_size, marker_size + 2)

        # set x-axis
        self.axis_x.setTickCount(2)
        self.axis_x.setRange(self.x_range[0],
                             self.x_range[1])
        self.axis_x.setVisible(False)

        # set y-axis
        self.axis_y.setTickCount(2)
        self.axis_y.setRange(self.y_range[0],
                             self.y_range[1])
        self.axis_y.setVisible(False)

        # remove border empty space
        self.chart().setMargins(QMargins(0, 0, 0, 0))
        #self.chart().setContentsMargins(10, 10, 10, 10)
        self.chart().legend().setVisible(False)
        #self.setContentsMargins(-10, -10, -10, -10)

        # set background
        self.chart().setBackgroundBrush(QColor(Qt.lightGray))
        self.chart().setBackgroundRoundness(0)

        # adjust marker size
        self.scatterseries.setColor(QColor(Qt.black))
        self.scatterseries.setMarkerSize(marker_size)
        self.scatterseries.setBorderColor(Qt.black)

        # default color
        self._default_color = QColor(Qt.black)

        # connect signal to slots
        self.scatterseries.pointAdded.connect(self.point_added)
        self.scatterseries.pointRemoved.connect(self.point_removed)
        self.scatterseries.pointReplaced.connect(self.point_replaced)
        self.scatterseries.swapped_signal.connect(self.points_swapped)

        # set default points (they are not deletable)
        ok = self._add_default_points_()
        assert ok, "failed to add default points"
        # self.scatterseries.setPointConfiguration(0, {QXYSeries.PointConfiguration.Color: QColor(Qt.red)})
        # self.scatterseries.setPointConfiguration(1, {QXYSeries.PointConfiguration.Color: QColor(Qt.red)})

        self.chart().addSeries(self.scatterseries)
        self.scatterseries.attachAxis(self.axis_x)
        self.scatterseries.attachAxis(self.axis_y)

        # color selector
        self.mouse_clicked_signal.connect(self.open_color_picker)

    def _add_default_points_(self) -> bool:
        """
        Adds default points.
        Only works if scatter series is empty.

        Returns True on success, else False.

        Triggers changed signal at most once
        :return:
        """
        if self.scatterseries.count() > 0:
            return False
        else:
            self.blockSignals(True)
            self.scatterseries.append(self.x_range[0], self.y_range[0])
            self.scatterseries.append(self.x_range[1], self.y_range[1])
            self.blockSignals(False)
            self.changed_signal.emit()
            return True

    def reset_tf(self):
        """
        Clears the transfer function to initial state.
        Deletes all points and clears all configurations, then adds back default points.
        Triggers changed_signal only once.
        :return:
        """
        self.blockSignals(True)
        for i in reversed(range(self.scatterseries.count())):
            self.scatterseries.remove(i)

        self._add_default_points_()
        self.blockSignals(False)
        self.changed_signal.emit()

    def copy_from_other_tf_widget(self, other):
        """
        Removes own values, then adds the values from the other transfer function widget.

        Triggers changed signal only once.
        :param other:
        :return:
        """
        prev_block_state = self.signalsBlocked()
        self.blockSignals(True)
        for i in reversed(range(self.scatterseries.count())):
            self.scatterseries.remove(i)

        for idx in range(other.scatterseries.count()):
            self.scatterseries.append(other.scatterseries.at(idx))
            self.scatterseries.setPointConfiguration(idx, other.scatterseries.get_configuration_for_point_at_idx(idx))
        self.blockSignals(prev_block_state)
        self.changed_signal.emit()

    def tf_from_json(self, json_string: str):
        d = json.loads(json_string)
        d["points"] = self.scatterseries.json_compatible_list_to_regular_point_list(d["points"])

        prev_block_state = self.signalsBlocked()
        self.blockSignals(True)
        for i in reversed(range(self.scatterseries.count())):
            self.scatterseries.remove(i)

        for idx in range(len(d["points"])):
            self.scatterseries.append(d["points"][idx]["x"], d["points"][idx]["y"])
            self.scatterseries.setPointConfiguration(idx, d["points"][idx]["configuration"])
        self.blockSignals(prev_block_state)
        self.changed_signal.emit()

    def tf_as_json(self) -> str:
        """
        Returns a json representation of this transferfunction.
        The JSON representation only contains the points and the QT compatible configurations:
            Color, Size, Visibility, LabelVisibility
            per point.
        :return:
        """
        j = dict()

        j["points"] = self.scatterseries.as_json_compatible_list()

        return json.dumps(j)

    def resizeEvent(self, event:PySide6.QtGui.QResizeEvent) -> None:
        super(TransferFunctionWidget, self).resizeEvent(event)

        size = event.size()

        self.axis_x.setRange(
            self.x_range[0] - (self.axis_margins[0] * ((self.x_range[1] - self.x_range[0]) / size.width())),
            self.x_range[1] + (self.axis_margins[1] * ((self.x_range[1] - self.x_range[0]) / size.width())))

        self.axis_y.setRange(
            self.y_range[0] - (self.axis_margins[2] * ((self.y_range[1] - self.y_range[0]) / size.height())),
            self.y_range[1] + (self.axis_margins[3] * ((self.y_range[1] - self.y_range[0]) / size.height())))

    @property
    def default_color(self):
        return QColor(self._default_color)

    def get_point_color_with_idx(self, point_idx):
        """
        Returns the color in the stored configuration for point with given idx.
        :param point_idx:
        :return:
        """
        return self.scatterseries.get_configuration_for_point_at_idx(point_idx)[QXYSeries.PointConfiguration.Color]

    def get_current_color_map(self):
        """
        Returns a list of colors for each value between 0 and 255.
        :return:
        """
        return [self.get_current_color_for(x / 255) for x in range(256)]  # x takes 256 from [0, 1]

    def get_current_color_for(self, x):
        """
        Returns the current color for x based on the transfer function.
        :param x: some values between including [0, 1].
        :return:
        """
        left, right = 0, self.scatterseries.count() - 1

        assert 0 <= x <= 1, "x has to be between 0 and 1, got: {}".format(x)

        # map x to values from x_range
        x = self.x_range[0] + x * self.x_range[1]

        if x <= self.x_range[0]:
            return self.get_point_color_with_idx(left)
        if x >= self.x_range[1]:
            return self.get_point_color_with_idx(right)

        # get left and right of x
        for i in range(0, self.scatterseries.count()):
            if self.scatterseries.at(i).x() >= x:
                left, right = (i - 1), i
                break

        left_color = self.get_point_color_with_idx(left)
        right_color = self.get_point_color_with_idx(right)

        # TODO: other interpolation methods
        printd(left, right)
        l = self.scatterseries.at(right).x() - self.scatterseries.at(left).x()
        if l == 0:
            l = 1
        t = (x - self.scatterseries.at(left).x()) / float(l)

        return interpolate_colors(left_color, right_color, t)

    def adjust_point_color_with_alpha(self, color: QColor, point_idx: int):
        """
        Returns the color for this point with adjusted alpha value.
        :param color:
        :param point_idx:
        :return:
        """
        color.setAlphaF(self.get_point_alpha(point_idx))
        return color

    def get_point_alpha(self, point_idx: int):
        """
        Returns the alpha value [0, 1] of this point.
        :param point_idx:
        :return:
        """
        point = self.scatterseries.at(point_idx)
        alpha = point.y() / (self.y_range[1] - self.y_range[0])
        return alpha

    @Slot()
    def update_point_color(self, color: QColor, point_idx: int):
        """
        Updates the point color and y-value (transparency) based on the selected color.
        :param color:
        :param point_idx:
        :return:
        """
        # color picker always returns a color with full opacity so we need to adjust that
        self.scatterseries.setPointConfiguration(
            point_idx, {QXYSeries.PointConfiguration.Color:
                                             self.adjust_point_color_with_alpha(color, point_idx)})

        self.changed_signal.emit()

        # print(self.get_current_color_map())

        # old_point = self.scatterseries.at(point_idx)
        # old_point.setY(self.axis_y.min() + color.alphaF() * self.axis_y.max())
        # self.scatterseries.replace(point_idx, old_point)

    @Slot()
    def open_color_picker(self, event: QMouseEvent):
        """
        Opens the color picker for the currently clicked point to change its color.
        :param point:
        :return:
        """
        if self.point_was_pressed_idx == -1:
            return

        if event.button() == Qt.RightButton:
            color_picker = QColorDialog(self)

            v = self.point_was_pressed_idx

            color_picker.colorSelected.connect(lambda c: self.update_point_color(c, v))

            color_picker.show()

            self.point_is_pressed_idx = -1
            self.point_was_pressed_idx = self.point_is_pressed_idx

        # printd(self.get_current_color_for(155))

    @Slot(int)
    def point_added(self, idx: int):
        if self.interpolation_mode == InterpolationModes.LINEAR.mode:
            self.line_series.insert(idx, self.scatterseries.at(idx))

        # self.scatterseries.setPointConfiguration(idx, {QXYSeries.PointConfiguration.Color:
        #                                                self.adjust_point_color_with_alpha(self.default_color, idx)})

        # self.scatterseries.setPointConfiguration(idx, {"lolol": True})
        self.update_point_color(self.default_color, idx)

        printd("point_added", idx, self.scatterseries.get_id_of_point_idx(idx))
        printd(self.scatterseries.get_points_id_configuration())

    @Slot(int)
    def point_removed(self, idx: int):
        if self.interpolation_mode == InterpolationModes.LINEAR.mode:
            self.line_series.remove(idx)

        self.changed_signal.emit()
        # printd("point_removed")
        printd(self.tf_as_json())

    @Slot(int, int)
    def points_swapped(self, idx1: int, idx2: int):
        if self.interpolation_mode == InterpolationModes.LINEAR.mode:
            self.line_series.swap(idx1, idx2)

    @Slot(int)
    def point_replaced(self, idx: int):
        if self.interpolation_mode == InterpolationModes.LINEAR.mode:
            self.line_series.replace(idx, self.scatterseries.at(idx))

        # self.scatterseries.setPointConfiguration(idx, {QXYSeries.PointConfiguration.Color:
        #                                                    self.adjust_point_color_with_alpha(
        #                                                        self.get_point_color_with_idx(idx), idx)})

        self.update_point_color(self.get_point_color_with_idx(idx), idx)
        printd("point_replaced", idx, self.scatterseries.get_id_of_point_idx(idx), self.adjust_point_color_with_alpha(
                                                               self.get_point_color_with_idx(idx), idx))
        printd(self.scatterseries.get_points_id_configuration())

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
        if value.x() <= self.x_range[0] or value.x() >= self.x_range[1] or \
                value.y() < self.y_range[0] or value.y() > self.y_range[1]:
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

        # adjust value to be still in range
        if value.x() < self.x_range[0] or value.x() > self.x_range[1] or \
            value.y() < self.y_range[0] or value.y() > self.y_range[1]:

            if value.x() < self.x_range[0]:
                value.setX(self.x_range[0])

            if value.x() > self.x_range[1]:
                value.setX(self.x_range[1])

            if value.y() < self.y_range[0]:
                value.setY(self.y_range[0])

            if value.y() > self.y_range[1]:
                value.setY(self.y_range[1])

        if self.point_is_pressed_idx == 0 or self.point_is_pressed_idx == self.scatterseries.count() - 1:
            value.setX(self.scatterseries.at(self.point_is_pressed_idx).x())
            if event.buttons() == Qt.LeftButton:
                self.scatterseries.replace(self.point_is_pressed_idx, value)
            else:
                self.point_is_pressed_idx = -1
        else:
            if self.point_is_pressed_idx != -1 and event.buttons() == Qt.LeftButton:
                self.point_is_pressed_idx = self.sorted_replace(self.point_is_pressed_idx, value)
                self.point_was_pressed_idx = self.point_is_pressed_idx
            else:
                self.point_is_pressed_idx = -1
