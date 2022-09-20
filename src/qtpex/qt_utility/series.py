from PySide6.QtCharts import QXYSeries
from PySide6.QtCore import QPoint


def find_point_idx(point: QPoint, series: QXYSeries) -> int:
    idx = -1

    for i in range(series.count()):
        if series.at(i) == point:
            idx = i
            break
    return idx
