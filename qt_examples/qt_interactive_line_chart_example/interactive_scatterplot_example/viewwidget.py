from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget)
from PySide6.QtCore import QDateTime, Qt, Slot
from PySide6.QtGui import QPainter, QMouseEvent, QColor

from PySide6.QtCharts import QChart, QLineSeries, QDateTimeAxis, QValueAxis, QScatterSeries

from tablemodel import CustomTableModel
from qt_widgets.iqchartview import IQChartView


class Widget(QWidget):
    def __init__(self, data):
        super().__init__()

        # Getting the Model
        self.model = CustomTableModel(data)

        # Creating a QTableView
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # QTableView Headers
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)

        # Creating QChart
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)

        self.add_series("Magnitude (Column 1)", [0, 1])

        # Creating QChartView
        self.chart_view = IQChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # binding press and release signals to slots
        # self.chart_view.mouse_released.connect(self.chart_released)
        self.chart_view.mouse_moved_signal.connect(self.chart_moved)

        # QWidget Layout
        self.main_layout = QHBoxLayout()

        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        ## Left layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        self.main_layout.addWidget(self.table_view)

        # Right Layout
        size.setHorizontalStretch(4)
        self.chart_view.setSizePolicy(size)
        self.main_layout.addWidget(self.chart_view)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)

        # connect data of table to chart
        self.model.data_changed.connect(self.update_data)

        self.pressed_point = None
        self.notmoved = True

    @Slot(QMouseEvent)
    def chart_moved(self, event: QMouseEvent):
        if self.pressed_point is not None:
            self.notmoved = False
            if self.pressed_point == -1:
                print("failed to find moved point")
            else:
                # move point
                value = self.chart.mapToValue(event.localPos())

                self.model.setData(self.model.index(self.pressed_point, 1), value.y(), Qt.EditRole)

                #self.series.replace(self.pressed_point, x, value.y())
                #self.scatterseries.replace(self.pressed_point, x, value.y())

    @Slot()
    def point_pressed(self, point):
        idx = -1

        for i in range(self.scatterseries.count()):
            if self.scatterseries.at(i) == point:
                idx = i
                break

        if idx != -1:
            self.pressed_point = idx
            self.notmoved = True
        else:
            print("failed to find pressed point")

    @Slot()
    def point_released(self, point):
        idx = -1

        for i in range(self.scatterseries.count()):
            if self.scatterseries.at(i) == point:
                idx = i
                break

        if idx != -1 and self.notmoved:
            if idx == self.pressed_point:
                if not self.scatterseries.isPointSelected(idx):
                    self.scatterseries.selectPoint(idx)
                else:
                    self.scatterseries.deselectPoint(idx)

        self.pressed_point = None

    @Slot(int, int, float, float)
    def update_data(self, row, column, old_magnitude, new_magnitude):
        # Getting the data
        t = self.model.index(row, 0).data()
        date_fmt = "yyyy-MM-dd HH:mm:ss.zzz"
        x = float(QDateTime().fromString(t, date_fmt).toSecsSinceEpoch())
        y = old_magnitude

        self.series.replace(x, y, x, new_magnitude)
        self.scatterseries.replace(x, y, x, new_magnitude)

        self.axis_y.setRange(self.model.input_magnitudes.min(), self.model.input_magnitudes.max())

    def add_series(self, name, columns):
        # Create QLineSeries
        self.series = QLineSeries()
        self.series.setName(name)

        # Create QScatterSeries
        self.scatterseries = QScatterSeries()

        # add listener to scatterseries
        # self.scatterseries.clicked.connect(self.point_clicked)
        self.scatterseries.pressed.connect(self.point_pressed)
        self.scatterseries.released.connect(self.point_released)

        # specify selected color
        sc = QColor(0,0,255)
        self.scatterseries.setSelectedColor(sc)

        # Filling QLineSeries and QScatterSeries
        for i in range(self.model.rowCount()):
            # Getting the data
            t = self.model.index(i, 0).data()
            date_fmt = "yyyy-MM-dd HH:mm:ss.zzz"
            x = QDateTime().fromString(t, date_fmt).toSecsSinceEpoch()
            y = float(self.model.index(i, 1).data())

            if x > 0 and y > 0:
                self.series.append(x, y)
                self.scatterseries.append(x, y)

        self.chart.addSeries(self.series)
        self.chart.addSeries(self.scatterseries)

        # hide legend of scatter series
        self.chart.legend().markers(self.scatterseries)[0].setVisible(False)

        # Setting X-axis
        self.axis_x = QDateTimeAxis()
        self.axis_x.setTickCount(10)
        self.axis_x.setFormat("dd.MM (h:mm)")
        self.axis_x.setTitleText("Date")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)
        self.scatterseries.attachAxis(self.axis_x)

        # Setting Y-axis
        self.axis_y = QValueAxis()
        self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setTitleText("Magnitude")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)
        self.scatterseries.attachAxis(self.axis_y)

        # Getting the color from the QChart to use it on the QTableView
        color_name = self.series.pen().color().name()
        self.model.color = f"{color_name}"

