from typing import Dict, Any

import PySide6
from PySide6.QtCore import Slot, Signal

from PySide6.QtCharts import QScatterSeries


class ConfigurableScatterSeries(QScatterSeries):
    """
        A QScatterSeries which keeps a second scatter series to keep track of point ids.
        It overrides the set configuration methods for the points to keep the same configurations even if points
            are deleted, or replaced, or intermediately inserted.
        """
    swapped_signal = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # a scatter series that keeps track of the ids of individual points (their y-values)
        self._point_id_series = QScatterSeries()
        self._next_point_id = 0

        self.pointAdded.connect(self.id_series_added)
        self.pointReplaced.connect(self.id_series_replaced)
        self.pointRemoved.connect(self.id_series_removed)
        self.swapped_signal.connect(self.id_series_swapped)

        self._points_id_configuration = {}

    def swap(self, idx1: int, idx2: int):
        """
        Swaps the index of two points and keeps their configuration.
        Triggers the swap signal.
        Does not trigger other signals.
        :param idx1:
        :param idx2:
        :return:
        """
        self.blockSignals(True)
        tmp = self.at(idx2)
        self.replace(idx2, self.at(idx1))
        self.replace(idx1, tmp)
        self.blockSignals(False)

        self.swapped_signal.emit(idx1, idx2)

    def setPointConfiguration(self, index: int,
                              configuration: Dict[PySide6.QtCharts.QXYSeries.PointConfiguration, Any]) -> None:
        self.set_id_configuration_for_point_at_idx(index, configuration)

    def setPointsConfiguration(self, pointsConfiguration: Dict[
        int, Dict[PySide6.QtCharts.QXYSeries.PointConfiguration, Any]]) -> None:
        """
        Sets the configuration for multiple points at once.
        If it is an empty dict, deletes all configurations.
        :param pointsConfiguration:
        :return:
        """
        if len(pointsConfiguration) == 0:
            self._points_id_configuration = {}
            self.update_points_configuration()

        for idx in pointsConfiguration:
            self.setPointConfiguration(idx, pointsConfiguration[idx])

    def get_id_of_point_idx(self, idx: int):
        """
        Returns the id of the point idx.
        :param idx:
        :return:
        """
        return int(self._point_id_series.at(idx).y())

    def set_id_configuration_for_point_at_idx(self, idx: int, conf: dict):
        """
        Sets the configuration for the point at idx based on its id.
        :param conf:
        :param idx:
        :return:
        """
        self._points_id_configuration[self.get_id_of_point_idx(idx)] = conf.copy()
        self.update_points_configuration()

    def get_configuration_for_point_at_idx(self, idx: int):
        return self._points_id_configuration[self.get_id_of_point_idx(idx)].copy()

    def update_points_configuration(self):
        """
        Updates the configuration of scatterseries with the current points_id_configuration.
        :return:
        """
        conf = {}
        for i in range(self._point_id_series.count()):
            conf.update({
                i: self._points_id_configuration[self.get_id_of_point_idx(i)].copy()
                if self.get_id_of_point_idx(i) in self._points_id_configuration else dict()
            })

        super().setPointsConfiguration(conf)

    def get_points_id_configuration(self):
        """
        Returns the current points_id_configuration for all point of scatterseries.
        The id's are the point's id's from point_id_series.
        :return:
        """
        return self._points_id_configuration.copy()

    def set_points_id_configuration(self, conf: dict):
        self._points_id_configuration = conf.copy()
        self.update_points_configuration()

    @Slot(int)
    def id_series_added(self, idx: int):
        p = self.at(idx)
        p.setY(self._next_point_id)

        self._point_id_series.insert(idx, p)

        self._next_point_id += 1
        self.update_points_configuration()

    @Slot(int)
    def id_series_removed(self, idx: int):
        self._point_id_series.remove(idx)
        self.update_points_configuration()

    @Slot(int)
    def id_series_replaced(self, idx: int):
        # replacing does not change id, we only change values here.
        # to change id, implement it when replacing
        self._point_id_series.replace(idx, self._point_id_series.at(idx))
        self.update_points_configuration()
        pass

    @Slot(int, int)
    def id_series_swapped(self, idx1: int, idx2: int):
        """
        Swappes the id_series points.
        :param idx1:
        :param idx2:
        :return:
        """
        tmp = self._point_id_series.at(idx1)
        self._point_id_series.replace(idx1, self._point_id_series.at(idx2))
        self._point_id_series.replace(idx2, tmp)
        self.update_points_configuration()
