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

        # a scatter series that keeps track of the ids of individual points (their y-values)
        self.point_id_series = QScatterSeries()
        self.next_point_id = 0

        self.scatterseries.pointAdded.connect(self.id_series_added)
        self.scatterseries.pointReplaced.connect(self.id_series_replaced)
        self.scatterseries.pointRemoved.connect(self.id_series_removed)

        self.points_id_configuration = {}

    def get_id_of_point_idx(self, idx: int):
        """
        Returns the id of the point idx.
        :param idx:
        :return:
        """
        return self.point_id_series.at(idx).y()

    def set_id_configuration_for_point_at_idx(self, idx: int, conf: dict):
        """
        Sets the configuration for the point at idx based on its id.
        :param conf:
        :param idx:
        :return:
        """
        self.points_id_configuration[self.get_id_of_point_idx(idx)] = conf
        self.update_points_configuration()

    def update_points_configuration(self):
        """
        Updates the configuration of scatterseries with the current points_id_configuration.
        :return:
        """
        conf = {}
        for i in range(self.point_id_series.count()):
            conf.update({
                i: self.points_id_configuration[self.point_id_series.at(i).y()]
                if self.point_id_series.at(i).y() in self.points_id_configuration else dict()
            })

        self.scatterseries.setPointsConfiguration(conf)

    def get_points_id_configuration(self):
        """
        Returns the current points_id_configuration for all point of scatterseries.
        The id's are the point's id's from point_id_series.
        :return:
        """
        return self.points_id_configuration

    def set_points_id_configuration(self, conf):
        self.points_id_configuration = conf
        self.update_points_configuration()

    @Slot(int)
    def id_series_added(self, idx: int):
        p = self.scatterseries.at(idx)
        p.setY(self.next_point_id)

        self.point_id_series.insert(idx, p)

        self.next_point_id += 1
        self.update_points_configuration()

    @Slot(int)
    def id_series_removed(self, idx: int):
        self.point_id_series.remove(idx)
        self.update_points_configuration()

    @Slot(int)
    def id_series_replaced(self, idx: int):
        # don't need to do this since replacing does not change id
        #self.point_id_series.replace(idx, self.point_id_series.at(idx))
        #self.update_points_configuration()
        pass

    def find_point_idx(self, point: QPoint, series=None):
        idx = -1

        if series is None:
            series = self.scatterseries

        for i in range(series.count()):
            if series.at(i) == point:
                idx = i
                break
        return idx

    def sorted_insert(self, point, series=None):
        """
        Insert the point into series, s.t., the series stays sorted.
        If two points are the same, insert left of it.
        :param series: A sorted series.
        :param point:
        :return:
        """
        if series is None:
            series = self.scatterseries

        for i in range(series.count()):
            if series.at(i).x() >= point.x():
                series.insert(i, point)
                return

        series.append(point)

    def sorted_replace(self, idx_to_replace, new_point: QPoint, series=None):
        """
        Replace point of idx_to_replace with new_point but keeps ordering in series.
        :param series:
        :param idx_to_replace:
        :param new_point:
        :return: Returns the new idx of the added point
        """
        if series is None:
            series = self.scatterseries

        # check if order changes
        if idx_to_replace < series.count() - 1 and new_point.x() > series.at(idx_to_replace + 1).x():
            # swap index with next one
            series.replace(idx_to_replace, series.at(idx_to_replace+1))
            series.replace(idx_to_replace + 1, new_point)
            return idx_to_replace + 1
        if idx_to_replace > 0 and new_point.x() < series.at(idx_to_replace - 1).x():
            series.replace(idx_to_replace, series.at(idx_to_replace-1))
            series.replace(idx_to_replace-1, new_point)
            return idx_to_replace-1

        # no order changes necessary
        series.replace(idx_to_replace, new_point)
        return idx_to_replace

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
            self.point_is_pressed_idx = self.sorted_replace(self.point_is_pressed_idx, value)
            self.point_was_pressed_idx = self.point_is_pressed_idx
        else:
            self.point_is_pressed_idx = -1

    @Slot()
    def chart_clicked(self, event):
        printd("chart_clicked:", self.point_is_pressed_idx, self.point_was_pressed_idx, event)
        # add point at position (if click was not induced by point click)
        if self.point_was_pressed_idx == -1 and event.button() == Qt.LeftButton:
            value = self.chart().mapToValue(event.localPos())
            self.sorted_insert(value)
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
