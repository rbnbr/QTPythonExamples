from PySide6.QtCharts import QChart, QScatterSeries, QValueAxis
from PySide6.QtGui import QPainter, QMouseEvent
from PySide6.QtWidgets import QSizePolicy

from qt_widgets.iqchartview import IQChartView
from PySide6.QtCore import Slot, QPoint, Qt, Signal
from PySide6.QtCore import QMutex


def printd(*args, **kwargs):
    if not True:
        print(*args, **kwargs)


class InteractiveChartWidget(IQChartView):
    append_point_signal = Signal(QPoint)
    remove_point_signal = Signal(int)
    replace_point_signal = Signal(int, QPoint)

    """
    Interactive Chart Widget.

    Add points by left-clicking in chart.
    Delete points by clicking them.
    Move points by dragging them.
    """
    def __init__(self, parent=None):
        super().__init__(QChart(), parent)

        self.mouse_clicked_signal.connect(self.chart_clicked)
        self.mouse_released_signal.connect(self.chart_released)
        self.mouse_moved_signal.connect(self.chart_moved)
        self.mouse_pressed_signal.connect(self.chart_pressed)

        # Get Chart
        chart = self.chart()
        # chart.setAnimationOptions(QChart.AllAnimations)

        # Create QScatterSeries
        self.scatterseries = QScatterSeries()

        # add listener to scatterseries
        self.scatterseries.clicked.connect(self.point_clicked)
        self.scatterseries.pressed.connect(self.point_pressed)
        self.scatterseries.released.connect(self.point_released)

        chart.addSeries(self.scatterseries)

        # hide legend of scatter series
        chart.legend().markers(self.scatterseries)[0].setVisible(False)

        # Setting X-axis
        self.axis_x = QValueAxis()
        self.axis_x.setTickCount(0)
        chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.scatterseries.attachAxis(self.axis_x)

        # Setting Y-axis
        self.axis_y = QValueAxis()
        self.axis_y.setTickCount(0)
        chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.scatterseries.attachAxis(self.axis_y)

        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setSizePolicy(size)

        self.setRenderHint(QPainter.Antialiasing)

        self.point_is_pressed_idx = -1  # at any time, if this is != -1, then some point is currently being pressed

        # at any time, if this is != -1, then the current execution of chart events was induced by this point idx
        self.point_was_pressed_idx = -1

    def find_point_idx(self, point: QPoint):
        idx = -1

        for i in range(self.scatterseries.count()):
            if self.scatterseries.at(i) == point:
                idx = i
                break
        return idx

    @Slot()
    def chart_moved(self, event: QMouseEvent):
        """
        Moves a point. Does not allow moving over other points.
        :param event:
        :return:
        """
        printd("chart_moved:", self.point_is_pressed_idx, event)
        if self.point_is_pressed_idx != -1 and event.buttons() == Qt.LeftButton:
            # move point
            value = self.chart().mapToValue(event.localPos())

            # self.replace_point_signal.emit(self.point_is_pressed_idx, value)
            # self.scatterseries.append(value)
            self.scatterseries.replace(self.point_is_pressed_idx, value)
        else:
            self.point_is_pressed_idx = -1

    @Slot()
    def chart_clicked(self, event):
        printd("chart_clicked:", self.point_is_pressed_idx, self.point_was_pressed_idx, event)
        # add point at position (if click was not induced by point click)
        if self.point_was_pressed_idx == -1 and event.button() == Qt.LeftButton:
            value = self.chart().mapToValue(event.localPos())
            self.scatterseries.append(value)
            printd("added point", value, "\n")
        elif self.point_was_pressed_idx != -1 and event.button() == Qt.LeftButton:
            # remove point
            self.scatterseries.remove(self.point_was_pressed_idx)
            printd("removed point idx", self.point_was_pressed_idx, "\n")
        else:
            # may need this since point_released is somehow not triggered with right-click
            if event.button() == Qt.RightButton:
                self.point_is_pressed_idx = -1

        self.point_was_pressed_idx = -1  # chart_clicked is last execution of events, reset point was pressed

    @Slot()
    def chart_released(self, event):
        # self.point_is_pressed_idx = -1
        printd("chart_released")
        pass

    @Slot()
    def chart_pressed(self, event):
        printd("chart_pressed")
        self.point_was_pressed_idx = self.point_is_pressed_idx

    @Slot()
    def point_clicked(self, point: QPoint):
        """
        :param point:
        :return:
        """
        printd("point_clicked:", point, self._moved, self.find_point_idx(point))

    @Slot()
    def point_pressed(self, point):
        # print("point_pressed", point)
        idx = self.find_point_idx(point)
        printd("point idx pressed:", point, idx)
        self.point_is_pressed_idx = idx
        self.point_was_pressed_idx = self.point_is_pressed_idx

    @Slot()
    def point_released(self, point):
        printd("point released", point, self.find_point_idx(point))
        self.point_is_pressed_idx = -1
